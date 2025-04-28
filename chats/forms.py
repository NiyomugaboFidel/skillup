from django import forms
from .models import DirectMessage

class MessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full p-2 border rounded focus:outline-none focus:ring focus:border-blue-300',
                'placeholder': 'Type your message...',
                'rows': 2,
            }),
        }