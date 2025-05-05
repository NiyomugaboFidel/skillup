from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Avg, Count, Sum, F, ExpressionWrapper, fields
from django.db.models.functions import Round

from .models import Quiz, Question, Choice, QuizAttempt, Answer
from .forms import QuizForm, AIQuizGenerationForm, TakeQuizForm
from .ai_utils import generate_quiz, generate_quiz_feedback

@login_required
def dashboard(request):
    user_quizzes = Quiz.objects.filter(creator=request.user).order_by('-created_at')
    user_attempts = QuizAttempt.objects.filter(user=request.user).order_by('-start_time')
    
    context = {
        'user_quizzes': user_quizzes,
        'user_attempts': user_attempts
    }
    return render(request, 'quiz/dashboard.html', context)

@login_required
def generate_ai_quiz(request):
    if request.method == 'POST':
        form = AIQuizGenerationForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            content_file = form.cleaned_data['content_file']
            num_questions = form.cleaned_data['num_questions']
            
            # Process uploaded file if present
            file_content = ""
            source_description = ""
            
            if content_file:
                source_description = f"Uploaded file: {content_file.name}"
                try:
                    from .file_utils import process_uploaded_file
                    file_content = process_uploaded_file(content_file)
                except ImportError as e:
                    messages.error(request, str(e))
                    return render(request, 'quiz/generate_quiz.html', {'form': form})
                except Exception as e:
                    messages.error(request, f"Error processing file: {str(e)}")
                    return render(request, 'quiz/generate_quiz.html', {'form': form})
            
            # Combine pasted content and file content
            combined_content = content
            if file_content:
                if combined_content:
                    combined_content += "\n\n" + file_content
                else:
                    combined_content = file_content
            
            # Generate the quiz using the combined content
            quiz_data = generate_quiz(combined_content, title, num_questions)
            
            if quiz_data:
                # Create the quiz
                quiz = Quiz.objects.create(
                    title=quiz_data['title'],
                    creator=request.user,
                    is_ai_generated=True,
                    source_content=combined_content,
                    description=source_description if source_description else "Generated from pasted content"
                )
                
                # Create the questions and choices
                for i, q_data in enumerate(quiz_data['questions']):
                    question = Question.objects.create(
                        quiz=quiz,
                        text=q_data['text'],
                        explanation=q_data['explanation'],
                        order=i+1
                    )
                    
                    for choice_data in q_data['choices']:
                        Choice.objects.create(
                            question=question,
                            text=choice_data['text'],
                            is_correct=choice_data['is_correct']
                        )
                
                messages.success(request, f"Successfully generated quiz '{title}' with {len(quiz_data['questions'])} questions!")
                return redirect('quiz_detail', quiz_id=quiz.id)
            else:
                messages.error(request, "Failed to generate quiz. Please try again or adjust your content.")
    else:
        form = AIQuizGenerationForm()
    
    return render(request, 'quiz/generate_quiz.html', {'form': form})


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().prefetch_related('choices')
    
    # Check if user has already taken this quiz
    user_attempts = QuizAttempt.objects.filter(quiz=quiz, user=request.user)
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'user_attempts': user_attempts
    }
    return render(request, 'quiz/quiz_detail.html', context)

@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if an incomplete attempt exists
    existing_attempt = QuizAttempt.objects.filter(
        quiz=quiz, 
        user=request.user, 
        end_time__isnull=True
    ).first()
    
    if existing_attempt:
        # Resume the existing attempt
        attempt = existing_attempt
    else:
        # Create a new attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            max_score=quiz.questions.count()
        )
    
    if request.method == 'POST':
        form = TakeQuizForm(request.POST, quiz=quiz)
        if form.is_valid():
            score = 0
            
            # Store user responses for AI feedback
            user_responses = []
            
            # Process answers
            for question in quiz.questions.all():
                field_name = f'question_{question.id}'
                selected_choice_id = form.cleaned_data.get(field_name)
                
                if selected_choice_id:
                    selected_choice = Choice.objects.get(id=selected_choice_id)
                    correct_choice = question.choices.filter(is_correct=True).first()
                    
                    # Create Answer object
                    answer = Answer.objects.create(
                        attempt=attempt,
                        question=question,
                        selected_choice=selected_choice,
                        is_correct=selected_choice.is_correct
                    )
                    
                    if answer.is_correct:
                        score += 1
                    
                    # Store response for AI feedback
                    user_responses.append({
                        'question_text': question.text,
                        'selected_choice_text': selected_choice.text,
                        'correct_choice_text': correct_choice.text if correct_choice else "No correct answer defined",
                        'is_correct': selected_choice.is_correct,
                        'explanation': question.explanation
                    })
            
            # Complete the attempt
            attempt.end_time = timezone.now()
            attempt.score = score
            attempt.save()
            
            # Generate AI feedback if quiz was AI-generated
            feedback = None
            if quiz.is_ai_generated and user_responses:
                feedback = generate_quiz_feedback(user_responses, quiz)
            
            return redirect('quiz_results', attempt_id=attempt.id)
    else:
        form = TakeQuizForm(quiz=quiz)
    
    context = {
        'quiz': quiz,
        'form': form,
        'attempt': attempt
    }
    return render(request, 'quiz/take_quiz.html', context)

@login_required
def quiz_results(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # Ensure the user can only see their own results
    if attempt.user != request.user and attempt.quiz.creator != request.user:
        messages.error(request, "You don't have permission to view these results.")
        return redirect('dashboard')
    
    answers = Answer.objects.filter(attempt=attempt).select_related('question', 'selected_choice')
    
    # Generate AI feedback if it's an AI-generated quiz
    feedback = None
    if attempt.quiz.is_ai_generated:
        # We need to recreate the user_responses from the saved answers
        user_responses = []
        for answer in answers:
            correct_choice = answer.question.choices.filter(is_correct=True).first()
            user_responses.append({
                'question_text': answer.question.text,
                'selected_choice_text': answer.selected_choice.text,
                'correct_choice_text': correct_choice.text if correct_choice else "No correct answer defined",
                'is_correct': answer.is_correct,
                'explanation': answer.question.explanation
            })
        
        # Only generate feedback if we haven't already (could store this in the DB)
        feedback = generate_quiz_feedback(user_responses, None)
    
    context = {
        'attempt': attempt,
        'answers': answers,
        'feedback': feedback
    }
    return render(request, 'quiz/quiz_results.html', context)

@login_required
def quiz_stats(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Ensure the user is the creator of the quiz
    if quiz.creator != request.user:
        messages.error(request, "You don't have permission to view these statistics.")
        return redirect('dashboard')
    
    # Get basic stats
    total_attempts = QuizAttempt.objects.filter(quiz=quiz, end_time__isnull=False).count()
    avg_score = QuizAttempt.objects.filter(quiz=quiz, end_time__isnull=False).aggregate(
        avg_score=ExpressionWrapper(
            Round(Avg(F('score') * 100.0 / F('max_score')), 2),
            output_field=fields.FloatField()
        )
    )['avg_score'] or 0
    
    # Get performance by question
    questions = Question.objects.filter(quiz=quiz)
    question_stats = []
    
    for question in questions:
        total_answers = Answer.objects.filter(question=question).count()
        correct_answers = Answer.objects.filter(question=question, is_correct=True).count()
        
        if total_answers > 0:
            correct_percentage = (correct_answers / total_answers) * 100
        else:
            correct_percentage = 0
        
        question_stats.append({
            'question': question,
            'total_answers': total_answers,
            'correct_answers': correct_answers,
            'correct_percentage': correct_percentage
        })
    
    # Get distribution of scores
    score_distribution = QuizAttempt.objects.filter(quiz=quiz, end_time__isnull=False).values(
        'score'
    ).annotate(
        count=Count('id')
    ).order_by('score')
    
    # Convert to percentages for charting
    score_percentages = []
    for item in score_distribution:
        score_percentage = (item['score'] / quiz.questions.count()) * 100
        score_percentages.append({
            'score': f"{int(score_percentage)}%",
            'count': item['count']
        })
    
    context = {
        'quiz': quiz,
        'total_attempts': total_attempts,
        'avg_score': avg_score,
        'question_stats': question_stats,
        'score_distribution': score_percentages
    }
    
    return render(request, 'quiz/stats.html', context)