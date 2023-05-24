from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator
from askme.models import Question, Profile, Tag, Answer
from askme.forms import RegForm, LoginForm, EditProfileForm, AnswerForm, QuestionForm
from askme.models import User, Profile, Question, Answer, UsersLikes
from django.utils import translation  
from django.contrib import auth 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

context = {'top_tags': Tag.objects.get_top_tags(), 'top_users': Profile.objects.get_users_top()}

def paginator(object_list, request, objects_per_page, last=False):
    paginator = Paginator(list(object_list), objects_per_page)
    page = request.GET.get('page')
    if last:
        objects_page = paginator.get_page(paginator.num_pages)
    else:
        objects_page = paginator.get_page(page)
    return objects_page


def index(request):
    translation.activate("ru")
    questions = Question.objects.get_newest()
    context['questions'] = paginator(questions, request, 10)
    context['new'] = True
    return render(request, 'index.html', context)


def actual(request):
    questions = Question.objects.get_hottest()
    context['questions'] = paginator(questions, request, 10)
    context['new'] = False
    return render(request, 'index.html', context)


@login_required(login_url='/login')
def newq(request):
    translation.activate("ru")
    form = QuestionForm(request.POST)
    context['form'] = form
    if request.POST:
        qid = form.save(author=request.user.profile)
        return redirect(reverse('question', args=[qid]))    
    return render(request, 'newquestion.html', context)


def register(request):
    translation.activate("ru")
    form = RegForm(request.POST)

    if request.POST:
        if form.is_valid():
                user = form.save()
                if user is not None:
                    auth.login(request, user)
                    return redirect(reverse('index'))


    context['form'] = form
    return render(request, 'registration.html', context)


def login(request):
    form = LoginForm(request.POST)
    context['form'] = form
    if request.POST:
        if form.is_valid():
            login = form.cleaned_data.get('login')
            password = form.cleaned_data.get('password')
            user = auth.authenticate(username=login,password= password)
            if user is None:
                form.add_error(None, 'Неправильный логин или пароль')
            else:
                auth.login(request, user)
                if(request.GET.get('continue')):
                    return redirect(request.GET.get('continue'))
                else:
                    return redirect(reverse('index'))    
    return render(request, 'login.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('next', '/'))


def question(request, q_id):
    question = Question.objects.get(pk=q_id)
    answers = Answer.objects.filter(question=q_id)
    form = AnswerForm(request.POST)
    context['question'] = question
    context['answers'] = paginator(answers, request, 5)
    cnt = answers.count()
    context['form'] = form
    if request.POST:
        form.save(question=context['question'], author=request.user.profile)
        answers = Answer.objects.filter(question=q_id)
        context['answers'] = paginator(answers, request, 5, True)
        return render(request, 'question.html', context)
    return render(request, 'question.html', context)


def tag(request, tag_name):
    questions = Question.objects.get_by_tag(tag_name)
    context['questions'] = paginator(questions, request, 10)
    context['tag_name'] = tag_name
    return render(request, 'tag.html', context)


@login_required(login_url='/login')
def editProfile(request):
    translation.activate("ru")
    form = EditProfileForm(request.POST, files=request.FILES)

    if request.POST:
        if form.is_valid():   
            if form.save(user = request.user):
                return redirect('/profile/edit')


    context['form'] = form
    return render(request, 'settings.html', context)



def vote_question(request):
    question_id = request.POST['question_id']
    is_like = request.POST['is_like']
    question = Question.objects.get(id=question_id)
    print('voteq')    
    if not (UsersLikes.objects.rating_exists(request.user.profile, question_id)):
        if (is_like == "True"):
            rating = 1
        else:
            rating = -1
        print('voteq')    
        urate, qrate = UsersLikes.objects.rate_object(object=question, user=request.user, rate=rating)
        print (urate)
        return JsonResponse({
            'new_rating': qrate,
            'user_rating': urate,
        })
    return JsonResponse({'new_rating': question.rating,
                         'user_rating': question.author.rating})


def vote_answer(request):
    answer_id = request.POST['answer_id']
    is_like = request.POST['is_like']
    answer = Answer.objects.get(id=answer_id)
    if not (UsersLikes.objects.rating_exists(request.user.profile, answer_id)):
        if (is_like == "True"):
            rating = 1
        else:
            rating = -1
        UsersLikes.objects.rate_object(object=question, user=request.user, rate=rating)
        return JsonResponse({
            'new_rating': answer.rating
        })
    return JsonResponse({'new_rating': answer.rating})   


def verify_answer(request):
    answer_id = request.POST['answer_id']
    is_right = request.POST['is_right']
    if (is_right=='true'):
        Answer.objects.verify_answer(answer_id, True)
    else:
        Answer.objects.verify_answer(answer_id, False)
