import json

from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from links.constants import (
    CREATED_LINK_SUCCESS,
    JSON_PARSE_ERROR,
    ORIGINAL_URL_REQUIRED_ERROR,
)

from .models import Link


@csrf_exempt  # 允許 CSRF 保護被跳過，僅在 API 中使用
@require_http_methods(['POST'])
def link_shortener_api(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': JSON_PARSE_ERROR}, status=400)

    original_url = data.get('original_url')
    custom_slug = data.get('slug')
    password = data.get('password')

    if not original_url:
        return JsonResponse(
            {'success': False, 'message': ORIGINAL_URL_REQUIRED_ERROR}, status=400
        )

    link_instance = Link(
        original_url=original_url,
        slug=custom_slug,
        password=password,  # 密碼會在 model.save() 中被 hash
    )

    try:
        link_instance.save()
    except ValidationError as e:
        # 取第一個錯誤訊息
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

    short_url = request.build_absolute_uri(f'/{link_instance.slug}')

    response_data = {
        'success': True,
        'message': CREATED_LINK_SUCCESS,
        'short_url': short_url,
        'original_url': link_instance.original_url,
    }

    return JsonResponse(response_data, status=201)


def redirect_link(request, slug):
    try:
        link = Link.objects.get(slug=slug)
    except Link.DoesNotExist:
        return JsonResponse(
            {'success': False, 'message': 'Short URL not found.'}, status=404
        )

    if not link.is_active:
        return JsonResponse(
            {'success': False, 'message': 'This short URL is inactive.'}, status=403
        )

    if link.password:
        if request.method == 'POST':
            input_password = request.POST.get('password')

            if check_password(input_password, link.password):
                return HttpResponseRedirect(link.original_url)

            else:
                return render(
                    request,
                    'links/enter_password.html',
                    {'slug': slug, 'error': '密碼不正確.'},
                )

        return render(request, 'links/enter_password.html', {'slug': slug})

    link.click_count += 1
    link.save(update_fields=['click_count'])

    return HttpResponseRedirect(link.original_url)


def new(req):
    return render(
        req,
        'links/new.html',
    )
