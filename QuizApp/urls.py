from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('instructor_register/', views.instructor_register, name='instructor_register'),  # For instructor registration
    path('instructor_login/', views.custom_login, name='instructor_login'),  # For instructor login
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('create_question/<int:quiz_id>/', views.create_question, name='create_question'),
    path('instructor_quizzes/', views.instructor_quizzes, name='instructor_quizzes'),
    path('edit_quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('edit_question/<int:quiz_id>/', views.edit_question, name='edit_question'),
    path('delete_quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('register/', views.register, name='register'), 
    path('login/', views.custom_login, name='login'),  # For login
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('take_quiz/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz_results/<int:score>/<str:quiz_session>/', views.quiz_results, name='quiz_results'),
    path('download_pdf/<str:quiz_session>/', views.download_pdf, name='download_pdf'),
    path('logout/', LogoutView.as_view(), name='logout')
]
