from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view_courses , name='home'),
    path('', views.dashboard_view_courses , name='courses'),
      path('me/', views.my_courses_view , name='my_courses'),
]
