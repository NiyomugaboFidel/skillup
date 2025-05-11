from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_quizzes')
    created_at = models.DateTimeField(auto_now_add=True)
    is_ai_generated = models.BooleanField(default=False)
    source_content = models.TextField(blank=True, help_text="Original content used for AI quiz generation")
    
    def __str__(self):
        return self.title
    
    def question_count(self):
        return self.questions.count()
    
    def get_average_score(self):
        attempts = self.attempts.all()
        if not attempts:
            return 0
        total_score = sum(attempt.score for attempt in attempts)
        return total_score / len(attempts)
    
    def get_completion_count(self):
        return self.attempts.count()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    explanation = models.TextField(blank=True, help_text="Explanation of the correct answer")
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"
    
    class Meta:
        ordering = ['order']

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0)
    max_score = models.IntegerField(default=0)
    
    @property
    def is_completed(self):
        return self.end_time is not None
    
    @property
    def duration(self):
        if not self.end_time:
            return None
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def score_percentage(self):
        if self.max_score == 0:
            return 0
        return (self.score / self.max_score) * 100
    
    def __str__(self):
        return f"{self.user.username}'s attempt on {self.quiz.title}"

class Answer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.is_correct = self.selected_choice.is_correct
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Answer for {self.question}"