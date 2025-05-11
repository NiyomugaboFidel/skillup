from django import forms
from django.forms import inlineformset_factory
from .models import Course, Module, Content, Review, Enrollment

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'cover_image', 'difficulty', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and Course.objects.filter(title__iexact=title).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A course with this title already exists.")
        return title


class ModuleForm(forms.ModelForm):
 class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Module title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Brief description',
                'rows': 3
            }),
            'order': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': '0'
            }),
        }

ModuleFormSet = inlineformset_factory(
    Course, Module,
    form=ModuleForm,
    extra=1,
    can_delete=True
)


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'content_type', 'text_content', 'video_url', 'file', 'order']
        widgets = {
            'text_content': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        text_content = cleaned_data.get('text_content')
        video_url = cleaned_data.get('video_url')
        file = cleaned_data.get('file')
        
        if content_type == 'text' and not text_content:
            self.add_error('text_content', 'This field is required for text content.')
        elif content_type == 'video' and not video_url:
            self.add_error('video_url', 'This field is required for video content.')
        elif content_type == 'file' and not file and not self.instance.pk:
            self.add_error('file', 'This field is required for file content.')
        
        return cleaned_data


ContentFormSet = inlineformset_factory(
    Module, Content,
    form=ContentForm,
    extra=1,
    can_delete=True
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['status']