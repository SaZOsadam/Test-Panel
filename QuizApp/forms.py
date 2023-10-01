# forms.py

from collections import UserDict
from django import forms
from .models import Choice
from .models import CustomUser
from .models import Quiz, Question, Choice
from django.contrib.auth.forms import UserCreationForm

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['name', 'description', 'duration']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'score']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']



class AllQuestionsForm(forms.Form):
    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        if questions:
            for index, question in enumerate(questions):
                field_name = f'question_{index}'
                self.fields[field_name] = forms.ModelChoiceField(
                    queryset=Choice.objects.filter(question=question),
                    widget=forms.RadioSelect,
                    empty_label=None,
                    label=question.text
                )

class ExtendedUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='*')
    last_name = forms.CharField(max_length=30, required=True, help_text='*')
    email = forms.EmailField(max_length=254, help_text='Required. Input a valid email address.')

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email','password1', 'password2', )


# forms.py

class InstructorRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'is_instructor',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_instructor = True
        if commit:
            user.save()
        return user

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2',)  # add any additional fields you have

    def save(self, commit=True):
        user = super().save(commit=False)
        # add any additional processing here
        if commit:
            user.save()
        return user
