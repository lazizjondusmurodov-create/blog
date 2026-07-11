from django.urls import path 
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('category/<int:pk>/', views.category_detail, name='category_detail'),
    path('search/', views.search, name='search'),
    path('contact/', views.contact, name='contact'),
]
