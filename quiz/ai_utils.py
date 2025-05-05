import google.generativeai as genai
import json
import os
from django.conf import settings

# Initialize the Gemini AI client
def init_gemini():
    api_key = settings.GEMINI_API_KEY
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-pro')

def generate_quiz(content, title, num_questions=5):
    """
    Generate a quiz using Gemini AI from the provided content
    
    Returns:
        dict: A dictionary containing quiz data in the following format:
        {
            'title': 'Quiz Title',
            'questions': [
                {
                    'text': 'Question text',
                    'explanation': 'Explanation for the correct answer',
                    'choices': [
                        {'text': 'Choice 1', 'is_correct': True},
                        {'text': 'Choice 2', 'is_correct': False},
                        ...
                    ]
                },
                ...
            ]
        }
    """
    model = init_gemini()
    
    prompt = f"""
    Generate a multiple-choice quiz based on the following content. The quiz should test comprehension and understanding of the key concepts in the material.
    
    Content: {content}
    
    Create {num_questions} multiple-choice questions with 4 options each, where only one option is correct.
    
    For each question:
    1. Provide the question text
    2. Provide 4 choices (only one should be correct)
    3. Indicate which choice is correct
    4. Include a brief explanation for the correct answer
    
    Format your response as valid JSON in the following format:
    {{
        "title": "{title}",
        "questions": [
            {{
                "text": "Question text goes here?",
                "explanation": "Explanation for the correct answer",
                "choices": [
                    {{"text": "Choice 1", "is_correct": false}},
                    {{"text": "Choice 2", "is_correct": true}},
                    {{"text": "Choice 3", "is_correct": false}},
                    {{"text": "Choice 4", "is_correct": false}}
                ]
            }},
            ...more questions...
        ]
    }}
    
    Ensure you respond ONLY with the JSON object, no other text.
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Try to extract the JSON part from the response
        try:
            # Sometimes the model might return code blocks, so let's handle that
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
                
            quiz_data = json.loads(json_text)
            
            # Basic validation
            if "title" not in quiz_data or "questions" not in quiz_data:
                raise ValueError("Invalid quiz format returned from AI")
                
            return quiz_data
            
        except json.JSONDecodeError:
            # If JSON parsing fails, we'll return an error state
            print(f"Failed to parse JSON response: {response_text}")
            return None
            
    except Exception as e:
        print(f"Error generating quiz: {str(e)}")
        return None

def generate_quiz_feedback(user_responses, quiz_data):
    """
    Generate feedback for a completed quiz using Gemini AI
    
    Args:
        user_responses: List of user's answers with correctness
        quiz_data: Original quiz data
        
    Returns:
        str: Personalized feedback with study recommendations
    """
    model = init_gemini()
    
    # Create a summary of the user's performance
    correct_count = sum(1 for resp in user_responses if resp['is_correct'])
    total_questions = len(user_responses)
    score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0
    
    # Create a detailed breakdown of questions, correct answers, and user's answers
    questions_summary = []
    for i, resp in enumerate(user_responses):
        question_data = {
            'question': resp['question_text'],
            'correct_answer': resp['correct_choice_text'],
            'user_answer': resp['selected_choice_text'],
            'is_correct': resp['is_correct'],
            'explanation': resp['explanation']
        }
        questions_summary.append(question_data)
    
    prompt = f"""
    You are an educational assistant providing feedback on a quiz. The user completed a quiz with the following results:
    
    Score: {correct_count}/{total_questions} ({score_percentage:.1f}%)
    
    Here are the questions, with the user's answers and the correct answers:
    
    {json.dumps(questions_summary, indent=2)}
    
    Based on this performance, please provide:
    1. A brief personalized assessment of their performance
    2. Specific recommendations for topics they should study more based on their incorrect answers
    3. Some encouragement and next steps
    
    Keep your response concise but helpful, between 150-300 words.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating feedback: {str(e)}")
        return "Sorry, we couldn't generate personalized feedback at this time."