from django.urls import path
from . import views

urlpatterns = [
    
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('courses/<slug:slug>/unenroll/', views.unenroll_course, name='unenroll_course'),
    path('courses/<slug:slug>/review/', views.review_course, name='review_course'),
    
    # Course content viewing
    path('content/<int:content_id>/', views.view_content, name='view_content'),
    
    # Student dashboard
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('enrollment/<int:enrollment_id>/update/', views.update_enrollment_status, name='update_enrollment'),
    
    # Instructor dashboard
    path('instructor/courses/', views.InstructorCoursesView.as_view(), name='instructor_courses'),
    path('instructor/courses/new/', views.CourseCreateView.as_view(), name='course_create'),
    path('instructor/courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_update'),
    path('instructor/courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('instructor/courses/<int:pk>/modules/', views.manage_course_modules, name='manage_course_modules'),
    path('instructor/modules/<int:module_id>/contents/', views.manage_module_contents, name='manage_module_contents'),
]