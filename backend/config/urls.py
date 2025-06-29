from django.urls import include, path

urlpatterns = [
    path('', include('links.urls')),
    path('', include('pages.urls')),
]
