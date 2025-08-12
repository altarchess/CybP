from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from .models import Question, SecurityQuestion
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'question': question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def registrationpage(request):
    return render(request, 'polls/register.html')

def register(request):
    print(request.POST)
    _username = request.POST["username"]
    _password = request.POST["password"]
    _securityquestions = request.POST["securityquestions"]
    _securityquestion = request.POST["securityquestion"]
    _user = User.objects.create_user(username = _username, password = _password)
    securityquestion_entry = SecurityQuestion()
    securityquestion_entry.question_text = _securityquestions
    securityquestion_entry.answer_text = _securityquestion
    securityquestion_entry.save()
    return HttpResponseRedirect("/polls")

def login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponseRedirect("/polls")
    else:
        return "Incorrect credentials"