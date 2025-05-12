from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-2 border rounded focus:outline-none focus:ring focus:border-blue-300',
                'placeholder': "What's happening?",
                'rows': 3,
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-2 border rounded focus:outline-none focus:ring focus:border-blue-300',
                'placeholder': 'Add a comment...',
                'rows': 2,
            }),
        }