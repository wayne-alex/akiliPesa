from django.shortcuts import render

# Create your views here.
def login_admin(request):
    return render(request, 'superadmin/login.html')


def customer_support(request):
    return render(request, 'superadmin/customersupport.html')