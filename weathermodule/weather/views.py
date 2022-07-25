import json

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from weather.forms import UserCreationForm, MyAuthenticationForm
from weather.utils import send_email_verify

User = get_user_model()


class MyLoginView(LoginView):
    form_class = MyAuthenticationForm


@csrf_exempt
def add_indicators(request):
    data = request.POST
    if data['error'] == '0':
        try:
            id = data['thisMeteoID']
            dt = str('20'+data['year']+'-'+data['month']+'-'+data['day']+' '+data['hour']+':'+data['minute']+':'+data['second'])
            uaccum = data['uaccum']
            photolight = data['photolight']
            humground = data['humground']
            humair = data['humair']
            tair = data['tair']
            airpressure = data['airpressure']
            tgroundsurface = data['tgroundsurface']
            tgrounddeep = data['tgrounddeep']
            wingspeed = data['wingspeed']
            wingdir = data['wingdir']

            answer = [
                id,dt,uaccum,photolight,humground,humair,tair,
                airpressure,tgroundsurface, tgrounddeep,wingspeed,
                wingdir
            ]
            print(answer)
            return JsonResponse({'success': '1', 'error': '', 'err_message': ''})
        except KeyError:
            return JsonResponse({'success': '0', 'error': '1', 'err_message': 'Not a valid keys'})
        except Exception as ex:
            return JsonResponse({'success': '0', 'error': '1', 'err_message': f'{ex}'})
    else:
        return redirect('home')

class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            return redirect('home')
        return redirect('invalid_verify')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
            ValidationError,
        ):
            user = None
        return user

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
            send_email_verify(request, user)
            return redirect('confirm_email')
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