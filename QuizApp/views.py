# views.py
from .forms import AllQuestionsForm, InstructorRegistrationForm, CustomUserCreationForm, ExtendedUserCreationForm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .forms import QuizForm, QuestionForm, ChoiceForm
from .models import Quiz, Question, Choice, UserResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.http import Http404, JsonResponse
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate, login
from reportlab.lib.pagesizes import letter
from django.contrib.auth.models import User
from django.forms import formset_factory
from QuizApp.models import CustomUser
from django.http import HttpResponse
from reportlab.lib import colors
from django import forms
from uuid import uuid4

# Create your views here.

def home(request):
    
    return render(request, 'QuizApp/home.html')

def instructor_register(request):
    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_instructor = True
            user.save()
            return redirect('instructor_login')
    else:
        form = InstructorRegistrationForm()
    return render(request, 'registration/instructor_register.html', {'form': form})


@login_required
def instructor_dashboard(request):
    quizzes = Quiz.objects.all()
    return render(request, 'QuizApp/instructor_dashboard.html', {'quizzes': quizzes})

@login_required
def create_quiz(request):
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()
            return redirect('create_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'QuizApp/create_quiz.html', {'form': form})

@login_required
def create_question(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    if request.method == "POST":
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            choices_text = [val for key, val in request.POST.items() if key.startswith('choice_text_')]
            choices_is_correct = {key.split("_")[-1]: bool(val) for key, val in request.POST.items() if key.startswith('is_correct_')}

            for index, text in enumerate(choices_text):
                is_correct = choices_is_correct.get(str(index), False)
                Choice.objects.create(
                    question=question,
                    text=text,
                    is_correct=is_correct
                )

            # Redirect to the same page to add more questions
            return redirect('create_question', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()
        choice_form = ChoiceForm()
        existing_questions = Question.objects.filter(quiz=quiz)
    
    return render(request, 'QuizApp/create_question.html', {
        'question_form': question_form, 
        'choice_form': choice_form,
        'existing_questions': existing_questions,
        'quiz': quiz
    })


@login_required
def instructor_quizzes(request):
    quizzes = Quiz.objects.filter(created_by=request.user)
    return render(request, 'QuizApp/instructor_quizzes.html', {'quizzes': quizzes})

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('edit_question', quiz_id=quiz.id)

    else:
        form = QuizForm(instance=quiz)
    return render(request, 'QuizApp/edit_quiz.html', {'form': form})

@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz = question.quiz  # Assuming 'quiz' is a ForeignKey in your 'Question' model
    choices = Choice.objects.filter(question=question)
    ChoiceFormSet = formset_factory(ChoiceForm, extra=0)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        choice_formset = ChoiceFormSet(request.POST, prefix='choices')
        
        if question_form.is_valid() and choice_formset.is_valid():
            question_form.save()
            
            # Update choices here
            for form, choice in zip(choice_formset, choices):
                if form.is_valid():
                    updated_choice = form.save(commit=False)
                    updated_choice.id = choice.id  # Maintain the same choice id
                    updated_choice.save()
            
            return redirect('instructor_dashboard')
    else:
        question_form = QuestionForm(instance=question)
        #choice_formset = ChoiceFormSet(initial=[{'choice_text': choice.choice_text, 'is_correct': choice.is_correct} for choice in choices], prefix='choices')
        choice_formset = ChoiceFormSet(initial=[{'choice_text': choice.text, 'is_correct': choice.is_correct} for choice in choices], prefix='choices')


    return render(request, 'QuizApp/edit_question.html', {'question_form': question_form, 'choice_formset': choice_formset})

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.delete()
    return redirect('quiz_list')  # Replace with your own URL pattern name



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_instructor = False
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']  # You forgot this line
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_instructor:  # Change this line to use is_instructor field
                return redirect('instructor_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            # Invalid login
            # You can add logic to handle invalid login attempts here
            pass
    else:
        form = AuthenticationForm()  # Instantiate the form for GET requests
    return render(request, 'registration/login.html', {'form': form})
                  
                  
@login_required
def student_dashboard(request):
    quizzes = Quiz.objects.all()
    return render(request, 'QuizApp/student_dashboard.html', {'quizzes': quizzes})


@login_required
def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    duration = quiz.duration  # Fetch the duration here
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        total_score = 0
        quiz_session = str(uuid4())
        
        for index, question in enumerate(questions):
            field_name = f'question_{index}'
            user_answer_id = request.POST.get(field_name, None)
            
            if user_answer_id:
                user_answer = Choice.objects.get(id=user_answer_id)
                UserResponse.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    choice=user_answer,
                    quiz_session=quiz_session
                )
                
                if user_answer.is_correct:
                    total_score += question.score
            
        return redirect('quiz_results', score=total_score, quiz_session=quiz_session)

    else:
        form = AllQuestionsForm(questions=questions)

    return render(request, 'QuizApp/take_quiz.html', {'quiz': quiz, 'form': form, 'duration': duration})

@login_required
def quiz_results(request, score, quiz_session):
    user_responses = UserResponse.objects.filter(quiz_session=quiz_session)
    quiz = user_responses.first().quiz if user_responses else None  # Assume all responses belong to the same quiz
    details = []

    if quiz:
        questions = quiz.questions.all()

        for question in questions:
            response = user_responses.filter(question=question).first()
            correct_answer = Choice.objects.get(question=question, is_correct=True)
            
            if response:
                user_answer = response.choice
                is_correct = user_answer == correct_answer
            else:
                user_answer = None
                is_correct = False
            
            details.append({
                'question': question.text,
                'user_answer': user_answer.text if user_answer else "None",
                'correct_answer': correct_answer.text,
                'is_correct': is_correct
            })

    return render(request, 'QuizApp/quiz_results.html', {'score': score, 'details': details, 'quiz_session': quiz_session})


@login_required
def download_pdf(request, quiz_session):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Quiz-Results.pdf"'

    user_responses = UserResponse.objects.filter(quiz_session=quiz_session)
    first_response = user_responses.first()
    if first_response:
        quiz = first_response.quiz
        questions = quiz.questions.all()
    else:
        return HttpResponse("No quiz found for the given session")

    details = []

    for question in questions:
        user_response = user_responses.filter(question=question).first()
        correct_answer = Choice.objects.get(question=question, is_correct=True)

        details.append({
            'question': question.text,
            'user_answer': user_response.choice.text if user_response else 'None',
            'correct_answer': correct_answer.text,
            'is_correct': user_response.choice == correct_answer if user_response else False
        })

    score = sum(1 for d in details if d['is_correct'])

    # PDF generation logic here
    pdf = SimpleDocTemplate(
        response,
        pagesize=letter
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Your Score: {}".format(score), styles['Title']))
    elements.append(Paragraph("Detailed Results:", styles['Title']))

    for detail in details:
        elements.append(Paragraph(f"Question: {detail['question']}", styles['BodyText']))
        elements.append(Paragraph(f"Your Answer: {detail['user_answer']}", styles['BodyText']))
        elements.append(Paragraph(f"Correct Answer: {detail['correct_answer']}", styles['BodyText']))
        status = "Correct" if detail['is_correct'] else "Incorrect"
        elements.append(Paragraph(f"Status: {status}", styles['BodyText']))

    pdf.build(elements)

    return response