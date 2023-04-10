from django.shortcuts import render
from django.core.paginator import Paginator
from askme.models import Question, Profile, Tag, Answer

context = {'auth': True, 'top_tags': Tag.objects.get_top_tags(), 'top_users': Profile.objects.get_users_top()}

def paginator(object_list, request, objects_per_page):
    paginator = Paginator(list(object_list), objects_per_page)
    page = request.GET.get('page')
    objects_page = paginator.get_page(page)
    return objects_page


def index(request):
    questions = Question.objects.get_newest()
    context['questions'] = paginator(questions, request, 10)
    context['new'] = True
    return render(request, 'index.html', context)


def actual(request):
    questions = Question.objects.get_hottest()
    context['questions'] = paginator(questions, request, 10)
    context['new'] = False
    return render(request, 'index.html', context)


def newq(request):
    return render(request, 'newquestion.html', context)


def register(request):
    return render(request, 'registration.html', context)


def login(request):
    return render(request, 'login.html', context)


def question(request, q_id):
    question = Question.objects.get(pk=q_id)
    answers = Answer.objects.filter(question=q_id)
    context['question'] = question
    context['answers'] = paginator(answers, request, 5)
    return render(request, 'question.html', context)


def tag(request, tag_name):
    questions = Question.objects.get_by_tag(tag_name)
    context['questions'] = paginator(questions, request, 10)
    context['tag_name'] = tag_name
    return render(request, 'tag.html', context)