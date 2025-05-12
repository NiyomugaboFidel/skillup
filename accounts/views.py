
        
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