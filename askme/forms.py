from django import forms
from askme.models import User, Profile, Question, Answer, UsersLikes, Tag
from django.core.validators import RegexValidator, validate_email
import re

#логин начинается с буквы, содержит в себе буквы,цифры, символы _ и -
loginValidator = RegexValidator(re.compile("^[A-z0-9_-]{2,19}$"))
#пароль должен включать латинские буквы разных регистров, цифры, специальные символы (!#$%&?".
passwordValidator = RegexValidator(r"^.*(?=.{8,})(?=.*[a-zA-Z])(?=.*\d)(?=.*[!#$%&?\"\.]).*$")

class RegForm(forms.Form):
    login = forms.CharField(validators=[loginValidator], min_length=3, max_length=20,
                            label='Логин', 
                            widget=forms.TextInput(attrs={'class': 'form-control'}), 
                            required=True)
    email = forms.CharField(validators=[validate_email], label='Почта', widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    password = forms.CharField(validators=[passwordValidator], min_length=8, label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    repeatPassword = forms.CharField(validators=[passwordValidator], label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    avatar = forms.ImageField(label='ava', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def save(self):
        login = self.cleaned_data.get('login')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        repeated_password = self.cleaned_data.get('repeatPassword')
        if password != repeated_password:
            self.add_error(RegForm.repeatPassword, 'Пароли не совпадают!')
            return None
        elif Profile.objects.check_user(login, email):
            self.add_error(RegForm.login, 'Пользователь с таким именем уже существует!')
            return None
        else:
            user = User.objects.create_user(login, email, password) 
            profile = Profile.objects.create(user=user)
            return user


class LoginForm(forms.Form):
    login = forms.CharField(validators=[loginValidator], min_length=3, max_length=20,
                            label='Логин', 
                            widget=forms.TextInput(attrs={'class': 'form-control'}), 
                            required=True)
    password = forms.CharField(validators=[passwordValidator], min_length=8, label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)   


class EditProfileForm(forms.Form):    
    login = forms.CharField(validators=[loginValidator], min_length=3, max_length=20,
                            label='Логин', 
                            widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, )
    email = forms.CharField(validators=[validate_email], label='Почта', widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    avatar = forms.ImageField(label='ava', required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def save(self, user):
        login = self.cleaned_data.get('login')
        email = self.cleaned_data.get('email')
        avatar = self.cleaned_data.get('avatar')
        if Profile.objects.check_user(login, email):
                self.add_error(EditProfileForm.login, 'Пользователь с таким именем уже существует!')
                return False
        else: 
            if (login):
                user.username = login
            if (email):    
                user.email = email 
            if (avatar):    
                user.profile.avatar = avatar
            user.profile.save() 
            user.save()
            return True
    

class AnswerForm(forms.Form):
    answer = forms.CharField(max_length=400, widget=forms.Textarea(attrs={'class': 'form-control'}), required=True, label='Ответ')

    def save(self, question, author):
       if self.is_valid():
            answerText = self.cleaned_data.get('answer')
            Answer.objects.create(question=question, text=answerText, author=author)

class QuestionForm(forms.Form):
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True, label='Заголовок')
    text = forms.CharField(max_length=100, widget=forms.Textarea(attrs={'class': 'form-control'}), required=True, label='Текст вопроса')
    tags = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}), required=True, label='Теги (через запятую)')
    
    def save(self, author):
        if self.is_valid():
            tags = self.cleaned_data.get('tags')
            title = self.cleaned_data.get('title')
            text = self.cleaned_data.get('text')
            if tags:
                tags = tags.split(",")
                Tag.objects.create_with_list(tags)

            question = Question.objects.create(title=title, text=text, author=author)
            question.add_tags(tags)
            return question.id