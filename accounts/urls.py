from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile_edit/', views.update_profile, name='update_profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),

]

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=160, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    cover_image = models.ImageField(upload_to='covers/', default='covers/default.png')
    website = models.URLField(max_length=100, blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    @property
    def follower_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.user.profile.following.count()

    def get_full_name(self):  # This should be inside the Profile class
        return self.user.get_full_name()

# Signal to create and save the Profile instance
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


        
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from .forms import ProfileUpdateForm, UserUpdateForm
from .models import Profile
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.profile.following.filter(user=user).exists()
    
    context = {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/update_profile.html', context)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user != user_to_follow:
        if request.user.profile.following.filter(user=user_to_follow).exists():
            # Unfollow
            request.user.profile.following.remove(user_to_follow.profile)
        else:
            # Follow
            request.user.profile.following.add(user_to_follow.profile)
            
            # Create notification
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            )
    
    return redirect('profile', username=username)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

    from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date', 'avatar', 'cover_image', 'website']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }
