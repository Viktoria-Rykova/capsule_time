from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm, ProfileUserForm, UserPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin  
from django.contrib.auth import get_user_model             
from django.urls import reverse_lazy                       
from django.views.generic.edit import UpdateView          
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import get_backends
from django.contrib.auth.views import PasswordResetView


def register_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = get_backends()[0].__class__.__module__ + '.' + get_backends()[0].__class__.__name__
            login(request, user)
            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # здесь 'username' — имя поля формы
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)  # email вместо username
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or 'index'
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль.')
    return render(request, 'users/login.html')


def logout_user(request):
    logout(request)
    return redirect('users:login')


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {'title': "Профиль пользователя"}

    def get_success_url(self):
        return reverse_lazy('users:profile', args=[self.request.user.pk])
    
    def get_object(self, queryset=None):
        return self.request.user
    

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url=reverse_lazy("users:password_reset_complete")
    template_name = "users/password_change_form.html"
    extra_context = {'title': "Изменение пароля"}

