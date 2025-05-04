
from django.shortcuts import render
from django.views.generic import TemplateView


def dashboard_view_courses(request):
    return render(request, 'courses/dashboard.html')
def my_courses_view(request):
    return render(request, 'courses/my_courses.html')


class IndexView(TemplateView):
    template_name = 'pages/home.html'
