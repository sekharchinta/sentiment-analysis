from django.shortcuts import render
from django.contrib import messages
from users.models import UserRegistrationModel


def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        if usrid == 'admin' and pswd == 'admin':
            return AdminHome(request)
        messages.error(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})


def AdminHome(request):
    users = UserRegistrationModel.objects.all()
    context = {
        'total_users': users.count(),
        'active_users': users.filter(status='activated').count(),
        'pending_users': users.filter(status='waiting').count(),
    }
    return render(request, 'admins/AdminHome.html', context)


def RegisterUsersView(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/viewregisterusers.html', {'data': data})


def ActivaUsers(request):
    if request.method == 'GET':
        uid = request.GET.get('uid')
        if uid:
            UserRegistrationModel.objects.filter(id=uid).update(status='activated')
        return RegisterUsersView(request)
    return RegisterUsersView(request)


def ChangePassword(request):
    uid = request.GET.get('uid')
    user = UserRegistrationModel.objects.filter(id=uid).first() if uid else None

    if request.method == 'POST':
        uid = request.POST.get('uid')
        user = UserRegistrationModel.objects.filter(id=uid).first()
        new_password = request.POST.get('new_password', '').strip()
        if user and new_password:
            user.password = new_password
            user.save()
            messages.success(request, f'Password updated successfully for {user.loginid}')
            return render(request, 'admins/ChangePassword.html',
                          {'user': user, 'updated': True,
                           'all_users': UserRegistrationModel.objects.all()})
        messages.error(request, 'Please enter a valid password and select a user.')

    return render(request, 'admins/ChangePassword.html',
                  {'user': user, 'all_users': UserRegistrationModel.objects.all()})
