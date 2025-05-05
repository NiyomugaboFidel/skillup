from django import forms
from .models import Quiz, Question, Choice

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description']

class AIQuizGenerationForm(forms.Form):
    title = forms.CharField(max_length=200)
    content = forms.CharField(widget=forms.Textarea, help_text="Paste the content to generate a quiz from", required=False)
    content_file = forms.FileField(required=False, help_text="Or upload a file with your content (.txt, .docx, .pdf)")
    num_questions = forms.IntegerField(min_value=1, max_value=20, initial=5, help_text="Number of questions to generate")
    
    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        content_file = cleaned_data.get('content_file')
        
        # Check that at least one content source is provided
        if not content and not content_file:
            raise forms.ValidationError("You must either paste content or upload a file")
        
        # Validate file type if a file is uploaded
        if content_file:
            file_name = content_file.name.lower()
            if not (file_name.endswith('.txt') or file_name.endswith('.docx') or file_name.endswith('.pdf')):
                raise forms.ValidationError("Only .txt, .docx and .pdf files are supported")
        
        return cleaned_data
    
    def clean_num_questions(self):
        num_questions = self.cleaned_data.get('num_questions')
        if num_questions < 1 or num_questions > 20:
            raise forms.ValidationError("Number of questions must be between 1 and 20")
        return num_questions

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'explanation']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']

# Form for creating a question with multiple choices at once
class QuestionWithChoicesForm(forms.Form):
    question_text = forms.CharField(widget=forms.Textarea, label="Question")
    explanation = forms.CharField(widget=forms.Textarea, required=False, label="Explanation")
    
    choice1 = forms.CharField(max_length=200, label="Choice 1")
    choice1_correct = forms.BooleanField(required=False, label="Correct?")
    
    choice2 = forms.CharField(max_length=200, label="Choice 2")
    choice2_correct = forms.BooleanField(required=False, label="Correct?")
    
    choice3 = forms.CharField(max_length=200, label="Choice 3")
    choice3_correct = forms.BooleanField(required=False, label="Correct?")
    
    choice4 = forms.CharField(max_length=200, label="Choice 4")
    choice4_correct = forms.BooleanField(required=False, label="Correct?")
    
    def clean(self):
        cleaned_data = super().clean()
        # Check that at least one choice is marked as correct
        if not any([
            cleaned_data.get('choice1_correct', False),
            cleaned_data.get('choice2_correct', False),
            cleaned_data.get('choice3_correct', False),
            cleaned_data.get('choice4_correct', False),
        ]):
            raise forms.ValidationError("At least one choice must be marked as correct")
        return cleaned_data

class TakeQuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        super(TakeQuizForm, self).__init__(*args, **kwargs)
        
        for i, question in enumerate(quiz.questions.all()):
            choices = [(choice.id, choice.text) for choice in question.choices.all()]
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=choices,
                widget=forms.RadioSelect
            )