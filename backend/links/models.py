import hashlib

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from .constants import (
    PASSWORD_MAX_LENGTH_ERROR,
    SLUG_DUPLICATE_ERROR,
    SLUG_MAX_LENGTH_ERROR,
    URL_INVALID_ERROR,
)
from .utils import generate_unique_slug


class Link(models.Model):
    original_url = models.URLField(
        max_length=2048, error_messages={'invalid': URL_INVALID_ERROR}
    )
    original_url_hash = models.CharField(
        max_length=64, unique=True, db_index=True, blank=True, null=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        db_index=True,
        error_messages={
            'unique': SLUG_DUPLICATE_ERROR,
            'max_length': SLUG_MAX_LENGTH_ERROR,
        },
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='links',
        null=True,  # 允許資料庫中此欄位為 NULL
        blank=True,  # 允許在 Django Admin 或表單中此欄位為空
    )
    password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        error_messages={'max_length': PASSWORD_MAX_LENGTH_ERROR},
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    click_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    def get_click_count(self):
        from .views import counter_redis  # Avoid circular import

        count = counter_redis.get(f'click_count:{self.slug}')
        return int(count) if count else 0

    def clean_slug(self, slug_value):
        slugified_slug = slugify(slug_value)
        if len(slugified_slug) > 50:
            raise ValidationError(SLUG_MAX_LENGTH_ERROR)
        if Link.objects.exclude(pk=self.pk).filter(slug=slugified_slug).exists():
            raise ValidationError(SLUG_DUPLICATE_ERROR)
        return slugified_slug

    def clean_password(self, password_value):
        if (
            password_value
            and not password_value.startswith('pbkdf2_')
            and len(password_value) > 64
        ):
            raise ValidationError(PASSWORD_MAX_LENGTH_ERROR)

        if password_value and not password_value.startswith('pbkdf2_'):
            return make_password(password_value)
        return password_value

    def clean(self):
        # 驗證 slug
        if self.slug:
            slugified_slug = slugify(self.slug)
            if len(slugified_slug) > 50:
                raise ValidationError({'slug': SLUG_MAX_LENGTH_ERROR})
            if Link.objects.exclude(pk=self.pk).filter(slug=slugified_slug).exists():
                raise ValidationError({'slug': SLUG_DUPLICATE_ERROR})
        # 驗證密碼
        if (
            self.password
            and not self.password.startswith('pbkdf2_')
            and len(self.password) > 64
        ):
            raise ValidationError({'password': PASSWORD_MAX_LENGTH_ERROR})

    def save(self, *args, **kwargs):
        if self.slug:
            self.slug = slugify(self.slug)

        else:
            self.slug = generate_unique_slug()
            while Link.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
                self.slug = generate_unique_slug()

        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)

        if not self.original_url_hash:
            self.original_url_hash = hashlib.sha256(
                self.original_url.encode()
            ).hexdigest()

        super().save(*args, **kwargs)
        # Invalidate cache
        cache.delete(f'link:{self.slug}')

    def __str__(self):
        return f'slug: {self.slug} -> original url: {self.original_url}'
