from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comment
from .forms import PostForm, CommentForm
from notifications.models import Notification
from django.contrib.contenttypes.models import ContentType

class HomeView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    
    # def get_queryset(self):
    #     # Get posts from users that the current user follows + own posts
    #     following_users = self.request.user.profile.following.values_list('user', flat=True)
    #     return Post.objects.filter(user__in=list(following_users) + [self.request.user.id])
def get_queryset(self):
    # Get all posts from all users in the system, ordered by newest first
    return Post.objects.all().order_by('-created_at')
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Your post has been created!')
            return redirect('home')
    else:
        form = PostForm()
    
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            
            # Create notification for post owner
            if post.user != request.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='comment',
                    content_type=ContentType.objects.get_for_model(post),
                    object_id=post.id
                )
            
            messages.success(request, 'Your comment has been added!')
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        
        # Create notification
        if post.user != request.user:
            Notification.objects.create(
                recipient=post.user,
                sender=request.user,
                notification_type='like',
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id
            )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
      
        return JsonResponse({'liked': liked, 'count': post.like_count})
    return redirect('post_detail', pk=post.pk)

@login_required
def retweet_post(request, pk):
    original_post = get_object_or_404(Post, pk=pk)
    
    # Check if user already retweeted this post
    if original_post.retweets.filter(id=request.user.id).exists():
        # Find and delete the retweet
        retweet = Post.objects.filter(
            user=request.user,
            parent=original_post
        ).first()
        if retweet:
            retweet.delete()
        original_post.retweets.remove(request.user)
        retweeted = False
    else:
        # Create a new retweet
        retweet = Post(
            user=request.user,
            content=original_post.content,
            parent=original_post
        )
        retweet.save()
        original_post.retweets.add(request.user)
        retweeted = True
        
        # Create notification
        if original_post.user != request.user:
            Notification.objects.create(
                recipient=original_post.user,
                sender=request.user,
                notification_type='retweet',
                content_type=ContentType.objects.get_for_model(original_post),
                object_id=original_post.id
            )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
      
        return JsonResponse({'retweeted': retweeted, 'count': original_post.retweet_count})
    return redirect('home')

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('home')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user