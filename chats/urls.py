from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('new/<str:username>/', views.start_thread, name='start_thread'),
]
