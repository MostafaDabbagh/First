from django.shortcuts import redirect, render
from . import forms
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from tickets.models import Ticket
from .models import History


def redirect_to_accounts(request):
    return redirect('user_login')


class UserRegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/accounts/profile/')
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            User.objects.create_user(cd['username'], cd['email'], cd['password'])
            messages.success(request, 'User registered successfully')
            return redirect('user_login')
        return render(request, 'accounts/register.html', {'form': form})

    def get(self, request):
        form = forms.UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})


class UserLoginView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/accounts/profile/')
        else:
            return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        form = forms.UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user:
                login(request, user)
                messages.success(request, 'You logged in successfully')
                return redirect('/accounts/profile/')
            else:
                messages.error(request, 'Username or password is not correct')
        return render(request, 'accounts/login.html', {'form': form})

    def get(self, request):
        form = forms.UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form})


class UserProfileView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.session.get('has_visited', False):
            History().add(request)
            request.session['has_visited'] = True
        user = User.objects.get(id=request.user.id)
        tickets = Ticket.filter(user.id)
        return render(request, 'accounts/profile.html', {'user': user, 'tickets': tickets})


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You logged out successfully')
        return redirect('user_login')
