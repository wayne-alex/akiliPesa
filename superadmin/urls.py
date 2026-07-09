from django.urls import path

from superadmin import views

urlpatterns = [
    path('', views.login_admin, name='login_admin'),
    path('customersupport/', views.customer_support, name='custommer_support'),

]


