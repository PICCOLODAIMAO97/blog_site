import string
import random
import time
from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm
from .forms import ChangeNicknameForm
from .forms import BindEmailForm
from .forms import ChangePasswordForm
from .forms import ForgetPassword
from .forms import RegForm
from .models import Profile


def login_for_modal(request):
    login_form = LoginForm(request.POST)
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data = {
            'status': 'SUCCESS'
        }
    else:
        data = {
            'status': 'ERROR'
        }
    return JsonResponse(data)


def login(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()
    data = {
        'login_form': login_form,
    }
    return render(request, 'user/login.html', context=data)


def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password_again']
            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            # 清除session
            del request.session['register_code']
            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        reg_form = RegForm()
    data = {
        'reg_form': reg_form,
    }
    return render(request, 'user/register.html', context=data)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    data = {

    }
    return render(request, 'user/user_info.html', context=data)


def change_nickname(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    data = {
        'form_title': '修改昵称',
        'page_title': '修改昵称',
        'submit_text': '修改',
        'form': form,
        'return_back_url': redirect_to,
    }
    return render(request, 'form.html', context=data)


def bind_email(request):
    redirect_to = request.GET.get('from', reverse('home'))

    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    data = {
        'form_title': '绑定邮箱',
        'page_title': '绑定邮箱',
        'submit_text': '绑定',
        'form': form,
        'return_back_url': redirect_to,
    }
    return render(request, 'user/bind_email.html', context=data)


def send_verification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_email_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code
            request.session['send_email_time'] = now
            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码: %s' % code,
                '565804165@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    data = {
        'form_title': '修改密码',
        'page_title': '修改密码',
        'submit_text': '修改',
        'form': form,
        'return_back_url': redirect_to,
    }
    return render(request, 'form.html', context=data)


def forget_password(request):
    redirect_to = reverse('user:login')

    if request.method == 'POST':
        form = ForgetPassword(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # 清除session
            del request.session['forget_password_code']
            return redirect(redirect_to)
    else:
        form = ForgetPassword()

    data = {
        'form_title': '重置密码',
        'page_title': '重置密码',
        'submit_text': '重置',
        'form': form,
        'return_back_url': redirect_to,
    }
    return render(request, 'user/forget_password.html', context=data)