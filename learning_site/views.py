from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from . import forms
import courses.models as models

def home_view(request):
    return render(request, 'home.html')


def suggestion_view(request):
    form = forms.SuggestionForm()
    context = {'form': form}
    if request.method == 'POST':
        form = forms.SuggestionForm(request.POST)
        if form.is_valid():
            send_mail(
                'Suggestion from {}'.format(form.cleaned_data['name']),
                form.cleaned_data['suggestion'],
                '{name} <{email}>'.format(**form.cleaned_data),
                ['hirotoaoyama@example.com'],
            )
            messages.add_message(request, messages.SUCCESS, 'Thanks for your suggestion!')
            return HttpResponseRedirect(reverse('suggestion view'))

    return render(request, 'suggestion_form.html', context)


# login view
def login_view(request):
    next = request.GET.get('next')
    form = forms.UserLoginForm(request.POST or None)
    if form.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('/')

    context = {'form': form}
    return render(request, 'login.html', context)


# register view
def register_view(request):
    next = request.GET.get('next')
    form = forms.UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = request.POST['password']

        try:
            staff_status = request.POST['staff_status']
        except KeyError:
            staff_status = False
        if staff_status:
            user.is_staff = True

        user.set_password(password)
        user.save()
        new_user = authenticate(request, username=user.username, password=password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect('/')

    context = {'form': form}
    return render(request, 'register.html', context)


# logout view
@login_required
def logout_view(request):
    logout(request)
    return redirect('/')


# profile view
@login_required
def profile_view(request):
    curr_user = request.user
    taken_quizzes = curr_user.quiztaker_set.filter(completed=True)
    context = {'taken_quizzes': taken_quizzes}
    return render(request, 'user_profile.html', context)
