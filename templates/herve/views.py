from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .models import User, StudentProfile, TeacherProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm, StudentProfileForm, TeacherProfileForm

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user_type = form.cleaned_data['user_type']
        
        if user_type == 'student':
            StudentProfile.objects.create(user=self.object)
        elif user_type == 'teacher':
            TeacherProfile.objects.create(user=self.object)
            
        return response

@login_required
def profile_view(request):
    user = request.user
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        
        if user.is_student():
            profile_form = StudentProfileForm(request.POST, instance=user.student_profile)
        elif user.is_teacher():
            profile_form = TeacherProfileForm(request.POST, instance=user.teacher_profile)
        else:
            profile_form = None
            
        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            return redirect('profile')
    else:
        user_form = CustomUserChangeForm(instance=user)
        
        if user.is_student():
            profile_form = StudentProfileForm(instance=user.student_profile)
        elif user.is_teacher():
            profile_form = TeacherProfileForm(instance=user.teacher_profile)
        else:
            profile_form = None
            
    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_profile'
```

### accounts/urls.py

```python
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
```

### courses/models.py

```python
from django.db import models
from accounts.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_teaching')
    students = models.ManyToManyField(User, related_name='courses_enrolled', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.code}: {self.title}"

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.code} - {self.title}"

class Material(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='course_materials/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Announcement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
```

### courses/views.py

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .models import Course, Module, Material, Announcement
from .forms import CourseForm, ModuleForm, MaterialForm, AnnouncementForm

class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_student():
            return user.courses_enrolled.all()
        elif user.is_teacher():
            return user.courses_teaching.all()
        else:
            return Course.objects.all()

class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['announcements'] = course.announcements.all()[:5]
        return context

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_teacher() or self.request.user.is_superuser

class CourseCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')
    
    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

class CourseUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.object.pk})
    
    def test_func(self):
        course = self.get_object()
        return super().test_func() and (self.request.user == course.teacher or self.request.user.is_superuser)

class ModuleCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Module
    form_class = ModuleForm
    template_name = 'courses/module_form.html'
    
    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        form.instance.course = course
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.kwargs['course_pk']})

class MaterialCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = 'courses/material_form.html'
    
    def form_valid(self, form):
        module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        form.instance.module = module
        return super().form_valid(form)
    
    def get_success_url(self):
        module = get_object_or_404(Module, pk=self.kwargs['module_pk'])
        return reverse_lazy('course_detail', kwargs={'pk': module.course.pk})

@login_required
def enroll_course(request, pk):
    if not request.user.is_student():
        return redirect('course_list')
        
    course = get_object_or_404(Course, pk=pk)
    course.students.add(request.user)
    return redirect('course_detail', pk=pk)

@login_required
def unenroll_course(request, pk):
    if not request.user.is_student():
        return redirect('course_list')
        
    course = get_object_or_404(Course, pk=pk)
    course.students.remove(request.user)
    return redirect('course_list')

class AnnouncementCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'courses/announcement_form.html'
    
    def form_valid(self, form):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        form.instance.course = course
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('course_detail', kwargs={'pk': self.kwargs['course_pk']})