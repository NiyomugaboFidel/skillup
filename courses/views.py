from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Avg
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Course, Module, Content, Enrollment, Review
from .forms import CourseForm, ModuleFormSet, ContentFormSet, ReviewForm, EnrollmentForm
from notifications.models import Notification
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'pages/home.html'  

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published')
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['enrolled_courses'] = self.request.user.enrolled_courses.all()
        return context


class InstructorCoursesView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/instructor_courses.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Check if user is enrolled
        is_enrolled = False
        if self.request.user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(user=self.request.user, course=course).exists()
        
        # Get course stats
        avg_rating = course.reviews.aggregate(Avg('rating'))['rating__avg']
        
        context.update({
            'is_enrolled': is_enrolled,
            'avg_rating': avg_rating,
            'review_form': ReviewForm(),
            'reviews': course.reviews.select_related('user').all(),
            'modules': course.modules.prefetch_related('contents').all()
        })
        return context


@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}!')
        
        # Notify instructor
        Notification.objects.create(
            recipient=course.instructor,
            sender=request.user,
            notification_type='enrollment',
            content_object=course
        )
    else:
        messages.info(request, f'You are already enrolled in {course.title}')
    
    return redirect('course_detail', slug=slug)


@login_required
def unenroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    enrollment.delete()
    messages.success(request, f'You have unenrolled from {course.title}')
    return redirect('course_list')


@login_required
def review_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Check if user is enrolled
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    if not is_enrolled:
        messages.error(request, 'You must be enrolled in the course to leave a review.')
        return redirect('course_detail', slug=slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                user=request.user,
                course=course,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'comment': form.cleaned_data['comment']
                }
            )
            
            if created:
                messages.success(request, 'Your review has been submitted!')
                
                # Notify instructor
                Notification.objects.create(
                    recipient=course.instructor,
                    sender=request.user,
                    notification_type='review',
                    content_object=review
                )
            else:
                messages.success(request, 'Your review has been updated!')
                
    return redirect('course_detail', slug=slug)


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Course "{self.object.title}" has been created!')
        return response


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def test_func(self):
        course = self.get_object()
        return self.request.user == course.instructor
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Course "{self.object.title}" has been updated!')
        return response


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('instructor_courses')
    
    def test_func(self):
        course = self.get_object()
        return self.request.user == course.instructor
    
    def delete(self, request, *args, **kwargs):
        course = self.get_object()
        messages.success(request, f'Course "{course.title}" has been deleted!')
        return super().delete(request, *args, **kwargs)


@login_required
def manage_course_modules(request, pk):
    course = get_object_or_404(Course, id=pk, instructor=request.user)
    
    if request.method == 'POST':
        formset = ModuleFormSet(request.POST, instance=course)
        if formset.is_valid():
            formset.save()
            messages.success(request, f'Modules for "{course.title}" have been updated!')
            return redirect('manage_course_modules', pk=course.id)
    else:
        formset = ModuleFormSet(instance=course)
    
    return render(request, 'courses/manage_modules.html', {
        'course': course,
        'formset': formset
    })


@login_required
def manage_module_contents(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    course = module.course
    
    # Check if user is the instructor
    if request.user != course.instructor:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        formset = ContentFormSet(request.POST, request.FILES, instance=module)
        if formset.is_valid():
            formset.save()
            messages.success(request, f'Contents for module "{module.title}" have been updated!')
            return redirect('manage_module_contents', module_id=module.id)
    else:
        formset = ContentFormSet(instance=module)
    
    return render(request, 'courses/manage_contents.html', {
        'module': module,
        'course': course,
        'formset': formset
    })


class StudentDashboardView(LoginRequiredMixin, ListView):
    model = Enrollment
    template_name = 'courses/student_dashboard.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            user=self.request.user
        ).select_related('course').prefetch_related('course__modules')


@login_required
def update_enrollment_status(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.user)
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course status updated for {enrollment.course.title}')
    
    return redirect('student_dashboard')


@login_required
def view_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    module = content.module
    course = module.course
    
    # Check if user is enrolled or is the instructor
    is_authorized = (
        request.user == course.instructor or 
        Enrollment.objects.filter(user=request.user, course=course, status='active').exists()
    )
    
    if not is_authorized:
        messages.error(request, 'You must be enrolled in this course to view the content.')
        return redirect('course_detail', slug=course.slug)
    
    # Get next and previous content
    module_contents = list(module.contents.order_by('order'))
    current_index = module_contents.index(content)
    prev_content = module_contents[current_index - 1] if current_index > 0 else None
    next_content = module_contents[current_index + 1] if current_index < len(module_contents) - 1 else None
    
    # Get next and previous modules
    course_modules = list(course.modules.order_by('order'))
    current_module_index = course_modules.index(module)
    prev_module = course_modules[current_module_index - 1] if current_module_index > 0 else None
    next_module = course_modules[current_module_index + 1] if current_module_index < len(course_modules) - 1 else None
    
    # Update progress
    if request.user != course.instructor:
        enrollment = Enrollment.objects.get(user=request.user, course=course)
        # Simple progress calculation (can be improved)
        total_contents = sum(m.contents.count() for m in course_modules)
        if total_contents > 0:
            # This is a simple way to calculate progress - in a real app you'd track completed content
            enrollment.progress = min(
                enrollment.progress + int(100 / total_contents),
                100
            )
            enrollment.save()
    
    return render(request, 'courses/view_content.html', {
        'content': content,
        'module': module,
        'course': course,
        'prev_content': prev_content,
        'next_content': next_content,
        'prev_module': prev_module,
        'next_module': next_module,
    })