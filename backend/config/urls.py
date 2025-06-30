from django.urls import include, path

urlpatterns = [
    path('', include('pages.urls')),
    path('', include('links.urls')),
    path('accounts/', include('allauth.urls')),
]
