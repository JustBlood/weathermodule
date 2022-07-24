from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View

from weather.forms import UserCreationForm


class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=email, password=password)
            login(request, user)
            return redirect('home')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)
# def index(request):
#     return render(request, 'weather/base.html', {'title': 'Главная страница'})
#
# def about(request):
#     return render(request, 'weather/base.html', {'title': 'О нашем сайте'})
#
# def weather(request):
#     return render(request, 'weather/base.html', {'title': 'Приложение погоды'})