from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('generate/', views.generate_ai_quiz, name='generate_quiz'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/<int:quiz_id>/stats/', views.quiz_stats, name='quiz_stats'),
    path('attempt/<int:attempt_id>/results/', views.quiz_results, name='quiz_results'),
     path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]