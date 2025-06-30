# your_app/urls.py

from django.urls import path

from . import views

app_name = 'links'

urlpatterns = [
    path('api/links/shortener', views.link_shortener_api, name='link_shortener_api'),
    path('<slug:slug>/', views.redirect_link, name='redirect_link'),
    path('links/new/', views.new, name='new'),
    path('api/fetch-page-info/', views.fetch_page_info_api, name='fetch_page_info_api'),
    path('links/list', views.index, name='index'),
    path('links/update/<int:id>/', views.update, name='update'),
    path('links/delete/<int:id>/', views.delete, name='delete'),
]
