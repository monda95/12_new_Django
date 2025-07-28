from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login as django_login
from django.urls import reverse


def index(request):
    if request.user.is_authenticated:
        return redirect('todo_list')
    return render(request, 'home.html')


def sign_up(request):
#     username = request.POST.get('username')
#     password1 = request.POST.get('password1')
#     password2 = request.POST.get('password2')
#
#     print('username:',username,'password1:',password1,'password2:',password2)
# #username 중복확인작업, 패스워드가 맞는지, 패스워드 정책에 맞는지(대소문자,특수문자)

    form = UserCreationForm(request.POST or None)

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    #     if form.is_valid():
    #         form.save()
    #         return redirect('/accounts/login/')
    # else:
    #     form = UserCreationForm()

    context ={
        'form':form
    }
    return render(request, 'registration/signup.html', context)


def login(request):
    form = AuthenticationForm(request, request.POST or None)
    if form.is_valid():
        django_login(request, form.get_user())
        return redirect(reverse("todo_list"))
    context = {
        'form':form
    }
    return render(request, 'registration/login.html', context)