from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.create_post, name='create_post'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:pk>/like/', views.like_post, name='like_post'),
    path('<int:pk>/retweet/', views.retweet_post, name='retweet_post'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
