from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import UpdateView, DetailView

from accounts.models import Token, Profile
from blog.settings import HOST_NAME

from accounts.forms import SignUpForm, UserChangeForm, UserChangePasswordForm, UserPasswordResetForm


def send_token(user, subject, message, redirect_url):
    token = Token.objects.create(user=user)
    url = HOST_NAME + reverse(redirect_url, kwargs={'token': token})
    print(url)
    try:
        user.email_user(subject, message.format(url=url))
    except ConnectionRefusedError:
        print('Could not send email. Server error.')


def register_view(request):
    if request.method == 'GET':
        form = SignUpForm()
        return render(request, 'register.html', context={'form': form})
    elif request.method == 'POST':
        form = SignUpForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Profile.objects.create(user=user)
            send_token(user,
                       'Вы зарегистрировались на сайте localhost:8000.',
                       'Для активации перейдите по ссылке: {url}',
                       redirect_url='accounts:user_activate')
            return redirect('webapp:index')
        else:
            return render(request, 'register.html', context={'form': form})


def user_activate_view(request, token):
    token = get_object_or_404(Token, token=token)
    user = token.user
    user.is_active = True
    user.save()
    token.delete()
    login(request, user)
    return redirect('webapp:index')


class UserDetailView(DetailView):
    model = User
    template_name = 'user_detail.html'
    context_object_name = 'user_obj'


class UserChangeView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'user_update.html'
    context_object_name = 'user_obj'
    form_class = UserChangeForm

    def test_func(self):
        return self.get_object() == self.request.user

    def get_success_url(self):
        return reverse('accounts:user_detail', kwargs={'pk': self.object.pk})


class UserChangePasswordView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'user_change_password.html'
    form_class = UserChangePasswordForm
    context_object_name = 'user_obj'

    def test_func(self):
        return self.get_object() == self.request.user

    def get_success_url(self):
        return reverse('accounts:login')


def password_reset_email_view(request):
    if request.method == 'GET':
        return render(request, 'password_reset_email.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if len(users) > 0:
            user = users[0]
            send_token(user,
                       'Вы запросили восстановление пароля на сайте localhost:8000.',
                       'Для ввода нового пароля перейдите по ссылке: {url}',
                       redirect_url='accounts:password_reset_form')
        return render(request, 'password_reset_confirm.html')


class PasswordResetFormView(UpdateView):
    model = User
    template_name = 'password_reset_form.html'
    form_class = UserPasswordResetForm
    context_object_name = 'user_obj'

    def get_object(self, queryset=None):
        token = self.get_token()
        return token.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = self.kwargs.get('token')
        return context

    def form_valid(self, form):
        token = self.get_token()
        token.delete()
        return super().form_valid(form)

    def get_token(self):
        token_value = self.kwargs.get('token')
        return get_object_or_404(Token, token=token_value)

    def get_success_url(self):
        return reverse('accounts:login')
