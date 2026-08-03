from django.shortcuts import render
from django.contrib import messages
from users.models import UserRegistrationModel


def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')
        messages.error(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})


def AdminHome(request):
    return render(request, 'admins/AdminHome.html', {})


def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/viewregisterusers.html', {'data': data})


def ActivaUsers(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        if uid:
            UserRegistrationModel.objects.filter(id=uid).update(status='activated')
        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/viewregisterusers.html', {'data': data})
    return RegisterUsersView(request)
