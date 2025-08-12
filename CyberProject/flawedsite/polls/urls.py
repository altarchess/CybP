from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('login', views.user_login, name="login"),
    path('registrationpage', views.registration_page, name="registrationpage"),
    path('register', views.user_register, name="register"),
    path('logout', views.user_logout, name="logout"),
    path('addpollpage', views.add_poll_page, name="addpollpage"),

]
