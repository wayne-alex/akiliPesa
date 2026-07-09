from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'landing.html')


def login_user(request):
    return render(request, 'login.html')


def signup_user(request):
    return render(request, 'signup.html')


def dashboard(request):
    return render(request, 'dashboard.html')


def trivia(request):
    return render(request, 'trivia.html')


def spectator(request):
    return render(request, 'spectator.html')


def forgot_password(request):
    return render(request, 'forgot_password.html')