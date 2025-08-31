from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from .models import Question, SecurityQuestion, Choice, Votes
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
import traceback

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def search(request):
    # The following line uses a param instead of inserting the user supplied value directly into the query
    # latest_question_list = Question.objects.raw("SELECT * FROM polls_question WHERE question_text = %s", [str(request.POST['keyword'])])
    latest_question_list = Question.objects.raw("SELECT * FROM polls_question WHERE question_text ='" + str(request.POST['keyword']) + "'")
    if len(latest_question_list) == 0:
        latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    owner = request.user.is_authenticated and request.user == question.owner
    return render(request, 'polls/detail.html', {'question': question, 'owner' : owner})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    #update vote totals
    i = 1
    for choice in question.choice_set.all():
        total = 0
        for vote in question.votes_set.all():
            if vote.option_id == i:
                total += 1
        choice.votes = total
        choice.save()
        i += 1
    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/polls")
    question = get_object_or_404(Question, pk=question_id)
    if int(request.POST['choice']) < 1 or int(request.POST['choice']) > 2:
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    for v in question.votes_set.all():
        if v.user_id == request.user.id:
            v.delete()
    vote_entry = Votes()
    vote_entry.question = question
    vote_entry.user_id = request.user.id
    vote_entry.option_id = request.POST['choice']
    vote_entry.username = request.user.username
    vote_entry.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def add_poll_page(request):
    return render(request, 'polls/add_poll.html')

def add_poll(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/polls")
    print(request.POST)
    _polltext = request.POST["polltext"]
    _polldesc = request.POST["pollcontext"]
    _option1 = request.POST["option1"]
    _option2 = request.POST["option2"]
    try:
        q = Question(question_text = _polltext, question_desc = _polldesc, owner = request.user)
        q.save()
        c1 = Choice(question = q, choice_text = _option1)
        c2 = Choice(question = q, choice_text = _option2)
        c1.save()
        c2.save()
    except:
        print(traceback.format_exc())
        HttpResponseRedirect("/polls")
    return HttpResponseRedirect("/polls")

def registration_page(request):
    return render(request, 'polls/register.html')

def user_register(request):
    print(request.POST)
    _username = request.POST["username"]
    _password = request.POST["password"]
    _securityquestions = request.POST["securityquestions"]
    _securityquestion = request.POST["securityquestion"]
    try:
        _user = User.objects.create_user(username = _username, password = _password)
        securityquestion_entry = SecurityQuestion(owner = _user, question_text = _securityquestions, answer_text = _securityquestion)
        securityquestion_entry.save()
    except:
        HttpResponseRedirect("/polls")
    return HttpResponseRedirect("/polls")

def user_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect("/polls")
    else:
        users = User.objects.all()
        for user in users:
            if user.username == username:
                return HttpResponseRedirect("/polls/forgot/" + username)
        return HttpResponseRedirect("/polls")

def forgot(request, _username):
    user = get_object_or_404(User, username = _username)
    secq = SecurityQuestion.objects.get(pk = user.id)
    return render(request, 'polls/forgot.html', {"secq" : secq, "user" : user})

def delete_poll(request, id):
    question = get_object_or_404(Question, pk=id)
    # Here we should check if the user is the same as the creator of the poll, not only if the user is logged in
    # The fix is the check that too, so this is a case of broken access control
    if not request.user.is_authenticated:
    #if not request.user.is_authenticated or question.owner != request.user:
        return HttpResponseRedirect("/polls")
    question.delete()
    return HttpResponseRedirect("/polls")

def reset(request, _username):
    user = get_object_or_404(User, username = _username)
    secq = SecurityQuestion.objects.get(pk = user.id)
    _seqc = request.POST["secq"]
    _password = request.POST["password"]
    _password2 = request.POST["password2"]
    if _seqc == secq.answer_text and _password == _password2:
        user.set_password(_password)
        user.save()
    return HttpResponseRedirect("/polls")

def user_logout(request):
    logout(request)
    return HttpResponseRedirect("/polls")

def users(request):
    users = User.objects.all().values()
    return render(request, 'polls/users.html', {"users" : users})

def user(request, user_id):
    user = User.objects.all().values()[user_id-1]
    qs = Question.objects.all()
    votes_by_user = []
    for q in qs:
        for v in q.votes_set.all():
            if v.user_id == user_id:
                votes_by_user.append(v)
    return render(request, 'polls/user.html', {"user" : user, "votes" : votes_by_user})