import datetime
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
from django.views.generic import TemplateView

from weather.forms import UserCreationForm, MyAuthenticationForm
from weather.models import *
from weather.utils import send_email_verify

User = get_user_model()


class MyLoginView(LoginView):
    form_class = MyAuthenticationForm


class AddStation(TemplateView):
    template_name = 'add_station.html'

    def get(self, request, *args, **kwargs):
        data = Meteostations.objects.all()
        try:
            user_stations = UserMeteostations.objects.filter(user_id=request.user.pk)
        except:
            context = {'data': data}
            return self.render_to_response(context)
        no_needs = []
        for i in user_stations:
            no_needs.append(data.get(pk=i.meteostation_id))
        needs = [x for x in data if x not in no_needs]
        context = {'stations': [x.pk for x in needs]}
        return self.render_to_response(context)

class MyStations(TemplateView):
    # Отображает страницу "Мои станции"
    template_name = 'my_stations.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            context['stations'] = UserMeteostations.objects.get(pk=request.user.pk)
        except Exception as ex:
            context['stations'] = None
        return self.render_to_response(context)
        # return render(request, self.template_name, context)


@csrf_exempt
def add_indicators(request):
    if request.method == 'POST':
        data = request.POST
        try:
            station = Meteostations.objects.get(pk=data['thisMeteoID'])
            print('\n', station, '\n')
        except:
            new_station = Meteostations(id=data['thisMeteoID'])
            new_station.save()
        if data['error'] == '0':
            try:
                data_int = list(map(float, (data['thisMeteoID'], data['uaccum'], data['photolight'], data['humground'], data['humair'],
                                          data['tair'], data['airpressure'], data['tgroundsurface'], data['tgrounddeep'],
                                          data['wingspeed'], data['wingdir'])))
                dt = datetime.datetime(int('20' + data['year']),
                            int(data['month']),
                            int(data['day']),
                            int(data['hour']),
                            int(data['minute']),
                            int(data['second']))
                print(dt, data_int)
                new_indicator = Indicators(meteostation_id = Meteostations.objects.get(pk=int(data_int[0])), dt=dt, uaccum=data_int[1], photolight=data_int[2], humground=data_int[3], humair=data_int[4], tair=data_int[5],
                    airpressure=data_int[6], tgroundsurface=data_int[7], tgrounddeep=data_int[8], wingspeed=data_int[9],
                    wingdir=data_int[10])
                new_indicator.save()

                return JsonResponse({'success': '1', 'error': '', 'err_message': ''})
            except KeyError:
                return JsonResponse({'success': '0', 'error': '1', 'err_message': 'Not a valid keys'})
            except Exception as ex:
                return JsonResponse({'success': '0', 'error': '1', 'err_message': f'{ex}'})
        else:
            return redirect('home')
    else:
        return JsonResponse({'success': '0', 'error': '1', 'err_message': f'Only POST requests is valid'})


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
