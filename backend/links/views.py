import hashlib
import json
import os

import redis
import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.core.cache import caches
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from links.constants import (
    CREATED_LINK_SUCCESS,
    JSON_PARSE_ERROR,
    ORIGINAL_URL_REQUIRED_ERROR,
)

from .forms import LinkForm
from .models import Link

# Get the default cache (for links)
link_cache = caches['default']

# Create a separate Redis client for counters
counter_redis = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'), port=6379, db=1
)


@csrf_exempt
@require_http_methods(['POST'])
def link_shortener_api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': JSON_PARSE_ERROR}, status=400)

    original_url = data.get('original_url')
    if not original_url:
        return JsonResponse(
            {'success': False, 'message': ORIGINAL_URL_REQUIRED_ERROR}, status=400
        )

    custom_slug = data.get('slug')
    password = data.get('password')
    is_active = data.get('is_active', True)
    notes = data.get('notes', '')

    # 1. 先驗證 slug/password 等欄位
    link_instance = Link(
        original_url=original_url,
        slug=custom_slug,
        password=password,
        is_active=is_active,
        notes=notes,
    )

    if request.user.is_authenticated:
        link_instance.owner = request.user

    try:
        link_instance.full_clean()  # 只做驗證，不存 DB
    except ValidationError as e:
        msg = ''
        if hasattr(e, 'message_dict'):
            for v in e.message_dict.values():
                if v:
                    msg = v[0]
                    break
        elif hasattr(e, 'messages'):
            msg = e.messages[0]
        else:
            msg = str(e)
        return JsonResponse({'success': False, 'message': msg}, status=400)

    # 2. 檢查 cache
    hash_val = hashlib.sha256(original_url.encode()).hexdigest()
    cached_slug = link_cache.get(f'rev:{hash_val}')
    if cached_slug:
        short_url = request.build_absolute_uri(f'/{cached_slug}')
        return JsonResponse(
            {
                'success': True,
                'message': CREATED_LINK_SUCCESS,
                'short_url': short_url,
                'original_url': original_url,
            },
            status=201,
        )

    # 3. 寫入 DB
    link_instance.save()
    # 4. Cache the new link and reverse link
    link_cache.set(
        f'link:{link_instance.slug}',
        {
            'original_url': link_instance.original_url,
            'is_active': link_instance.is_active,
            'password': link_instance.password,
        },
        timeout=60 * 60 * 24 * 7,
    )
    link_cache.set(f'rev:{hash_val}', link_instance.slug, timeout=60 * 60 * 24 * 7)

    short_url = request.build_absolute_uri(f'/{link_instance.slug}')
    response_data = {
        'success': True,
        'message': CREATED_LINK_SUCCESS,
        'short_url': short_url,
        'original_url': link_instance.original_url,
    }
    return JsonResponse(response_data, status=201)


def redirect_link(request, slug):
    # 1. Check cache first
    cached_link = link_cache.get(f'link:{slug}')
    if cached_link:
        if not cached_link['is_active']:
            return render(
                request,
                'links/error_page.html',
                {
                    'error_title': '連結已停用',
                    'error_message': '這個短網址目前已被擁有者設為停用狀態，暫時無法訪問。',
                },
                status=403,
            )

        if cached_link.get('password'):
            if request.method == 'POST':
                input_password = request.POST.get('password')
                if check_password(input_password, cached_link['password']):
                    counter_redis.incr(f'click_count:{slug}')
                    return HttpResponseRedirect(cached_link['original_url'])
                else:
                    return render(
                        request,
                        'links/enter_password.html',
                        {'slug': slug, 'error': '密碼不正確.'},
                    )
            return render(request, 'links/enter_password.html', {'slug': slug})

        counter_redis.incr(f'click_count:{slug}')
        return HttpResponseRedirect(cached_link['original_url'])

    # 2. If not in cache, get from DB
    try:
        link = Link.objects.get(slug=slug)
        # Cache the link info
        link_cache.set(
            f'link:{link.slug}',
            {
                'original_url': link.original_url,
                'is_active': link.is_active,
                'password': link.password,
            },
            timeout=60 * 60 * 24 * 7,  # Cache for 7 days
        )

    except Link.DoesNotExist:
        # Cache a "not found" value to prevent cache penetration
        link_cache.set(f'link:{slug}', 'NULL', timeout=60)
        context = {
            'error_title': '找不到短網址',
            'error_message': f'抱歉，我們找不到與 "{slug}" 對應的網址。請檢查您輸入的連結是否正確。',
        }
        return render(request, 'links/error_page.html', context, status=404)

    # Check if the link is inactive
    if not link.is_active:
        context = {
            'error_title': '連結已停用',
            'error_message': '這個短網址目前已被擁有者設為停用狀態，暫時無法訪問。',
        }
        return render(request, 'links/error_page.html', context, status=403)

    if link.password:
        if request.method == 'POST':
            input_password = request.POST.get('password')
            if check_password(input_password, link.password):
                counter_redis.incr(f'click_count:{slug}')
                return HttpResponseRedirect(link.original_url)
            else:
                return render(
                    request,
                    'links/enter_password.html',
                    {'slug': slug, 'error': '密碼不正確.'},
                )
        return render(request, 'links/enter_password.html', {'slug': slug})

    # For non-password protected links, increment click count and redirect
    counter_redis.incr(f'click_count:{slug}')
    return HttpResponseRedirect(link.original_url)


def new(req):
    return render(
        req,
        'links/new.html',
    )


@csrf_exempt
@require_http_methods(['POST'])
def fetch_page_info_api(request):
    try:
        data = json.loads(request.body)
        url = data.get('original_url')
        if not url:
            return JsonResponse(
                {'success': False, 'message': '未提供 URL。'}, status=400
            )

        # 設定 headers 模擬瀏覽器，避免被某些網站阻擋
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=5, verify=False)
        response.raise_for_status()  # 如果狀態碼不是 2xx，會拋出異常

        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 獲取標題
        title_tag = soup.find('title')
        title = title_tag.string.strip() if title_tag else '（未找到標題）'

        # 獲取描述 (description meta tag)
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = (
            desc_tag['content'].strip()
            if desc_tag and 'content' in desc_tag.attrs
            else '（未找到描述）'
        )

        # 組合成要填入備註欄的文字
        notes_text = f'標題：{title}\n描述：{description}'

        return JsonResponse({'success': True, 'notes': notes_text})

    except requests.exceptions.RequestException:
        # 處理網路請求相關錯誤 (如超時、連線失敗、無效 URL)
        return JsonResponse({'success': False, 'message': '無法抓取網頁'}, status=400)
    except Exception:
        return JsonResponse({'success': False, 'message': '處理時發生錯誤'}, status=500)


@login_required
def index(request):
    links = Link.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'links/list.html', {'links': links})


@login_required  # (Update)
def update(request, id):
    link = get_object_or_404(Link, pk=id, owner=request.user)

    if request.method == 'POST':
        form = LinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, '短網址已成功更新！')
            return redirect('links:index')
    else:
        form = LinkForm(instance=link)

    return render(request, 'links/edit.html', {'form': form, 'action': '更新'})


@login_required
def delete(request, id):
    link = get_object_or_404(Link, pk=id, owner=request.user)

    if request.method == 'POST':
        link_name = link.slug
        link.delete()
        messages.success(request, f'短網址 "{link_name}" 已成功刪除。')
        return redirect('links:index')
