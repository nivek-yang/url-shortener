# your_app/urls.py

from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('api/links/shortener', views.link_shortener_api, name='link_shortener_api'),
    path('<slug:slug>/', views.redirect_link, name='redirect_link'),
    path('links/new/', views.new, name='new'),
]
