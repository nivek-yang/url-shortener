from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from .utils import generate_unique_slug


class Link(models.Model):
    original_url = models.URLField(max_length=2048)
    slug = models.SlugField(max_length=50, unique=True, blank=True, db_index=True)
    password = models.CharField(max_length=64, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.slug:  # User provided a custom slug
            slugified_slug = slugify(self.slug)

            if Link.objects.exclude(pk=self.pk).filter(slug=slugified_slug).exists():
                raise ValidationError(
                    f"The slug '{slugified_slug}' is already in use. Please choose a different one."
                )

            self.slug = slugified_slug

        else:  # No custom slug provided, generate one
            self.slug = generate_unique_slug()
            while Link.objects.exclude(pk=self.pk).filter(slug=self.slug).exists():
                self.slug = generate_unique_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'slug: {self.slug} -> original url: {self.original_url}'
