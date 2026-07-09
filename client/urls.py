
from django.urls import path, include

from client import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_user, name='login_user'),
    path('forgotpassword/', views.forgot_password, name='forgot_password'),

    path('signup/', views.signup_user, name='signup_user'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('trivia/', views.trivia, name='trivia'),
    path('spectator/', views.spectator, name='spectator'),
]
