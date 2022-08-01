import datetime
import json
from calendar import monthrange

from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
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


class StationMonthView(TemplateView):
    template_name = 'station_month.html'
    def get(self, request, *args, **kwargs):
        # print(Indicators.objects.values('dt'))

        return self.render_to_response(context=kwargs)

class StationView(TemplateView):
    template_name = 'station.html'

    def get(self, request, *args, **kwargs):
        date_now = datetime.datetime.now(datetime.timezone.utc)
        available_years = set([x['dt'].year for x in Indicators.objects.values('dt')])
        kwargs['months'] = [['Январь', 1], ["Февраль", 2], ["Март", 3], ["Апрель", 4], ["Май", 5], ["Июнь", 6], ["Июль", 7], ["Август", 8], ["Сентябрь", 9],
                            ["Октябрь", 10], ["Ноябрь", 11], ["Декабрь", 12]]
        kwargs['years'] = available_years

        if request.GET:
            try:
                data_sort = request.GET['type']
                # если есть параметр type - отрабатывает все, что после except данного блока try
            except:
                try:
                    year = request.GET['year']
                    month = request.GET['month']
                except:
                    return self.render_to_response(context=kwargs)
                # если есть параметры года и месяца - построение графика за месяц такого-то года.
                days = monthrange(int(year), int(month))[1]

                indicators = Indicators.objects.filter(dt__year=year,
                                                       dt__month=month)

                # Чтобы брало даты только дней
                # Выборка максимальной, минимальной и средней температуры по дням
                temp = {
                    'min': [],
                    'max': [],
                    'average': []
                }

                for i in range(1, days+1):
                    try:
                        if request.GET['ind'] == 'photolight':
                            kwargs['ind'] = 'Уровень света'
                            cur_day = [x.photolight for x in indicators if x.dt.day == i]
                        elif request.GET['ind'] == 'airpressure':
                            kwargs['ind'] = 'Атмосферное давление'
                            cur_day = [x.airpressure for x in indicators if x.dt.day == i]
                        elif request.GET['ind'] == 'humair':
                            kwargs['ind'] = 'Влажность'
                            cur_day = [x.humair for x in indicators if x.dt.day == i]
                        else:
                            kwargs['ind'] = 'Температура воздуха'
                            cur_day = [x.tair for x in indicators if x.dt.day == i]
                    except:
                        cur_day = [x.tair for x in indicators if x.dt.day == i]
                    if cur_day:
                        temp['min'].append(min(cur_day))
                        temp['max'].append(max(cur_day))
                        temp['average'].append(sum(cur_day)/len(cur_day))
                date = [f'{x}/{month}/{year}' for x in range(1, len(temp['min'])+1)]

                kwargs['date'] = date
                kwargs['temp'] = temp
                return self.render_to_response(context=kwargs)


            needed = []
            if data_sort == 'day':
                indicators = Indicators.objects.filter(meteostation_id=kwargs['station_id'],
                                                        dt__gte=date_now-datetime.timedelta(days=1))
                needed = [x for x in indicators if x.dt.minute == 0 and x.dt.day == date_now.day]
            elif data_sort == 'week':
                indicators = Indicators.objects.filter(meteostation_id=kwargs['station_id'],
                                                        dt__gte=date_now - datetime.timedelta(days=7))
                needed = [x for x in indicators if x.dt.hour in [9, 15, 21] and x.dt.minute==0]

            date = [[x.dt.day, x.dt.month, x.dt.year, x.dt.hour] for x in needed]

            try:
                if request.GET['ind'] == 'photolight':
                    kwargs['ind'] = 'Уровень света'
                    temp = [x.photolight for x in needed]
                elif request.GET['ind'] == 'airpressure':
                    temp = [x.airpressure for x in needed]
                    kwargs['ind'] = 'Атмосферное давление'
                elif request.GET['ind'] == 'humair':
                    temp = [x.humair for x in needed]
                    kwargs['ind'] = 'Влажность'
                elif request.GET['ind'] == 'tair':
                    temp = [x.tair for x in needed]
                    kwargs['ind'] = 'Температура воздуха'
            except:
                temp = [x.tair for x in needed]
                kwargs['ind'] = 'Температура воздуха'

            kwargs['date'] = date
            kwargs['temp'] = temp

        else:
            indicators = Indicators.objects.filter(meteostation_id=kwargs['station_id'],
                                                   dt__gte=date_now - datetime.timedelta(days=1))
            needed = [x for x in indicators if x.dt.minute == 0]
            date = [[x.dt.day, x.dt.month, x.dt.year, x.dt.hour] for x in needed]

            temp = [x.tair for x in needed]
            kwargs['ind'] = 'Температура воздуха'
            kwargs['date'] = date
            kwargs['temp'] = temp

        return self.render_to_response(context=kwargs)


class MyStations(TemplateView):
    # Отображает страницу "Мои станции"
    template_name = 'my_stations.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            st_list = []
            for station in UserMeteostations.objects.filter(user=request.user):
                st_list.append(station.meteostation)
            st_list.sort()
            context['user_stations'] = st_list
        except:
            context['user_stations'] = None

        all_stations = Meteostations.objects.all()
        try:
            user_stations = UserMeteostations.objects.filter(user_id=request.user.pk)
            no_needs = []
            for i in user_stations:
                no_needs.append(all_stations.get(pk=i.meteostation_id))
            needs = [x for x in all_stations if x not in no_needs]
            context['all_stations'] = [x.pk for x in needs]
            return self.render_to_response(context)
        except:
            context['all_stations'] = all_stations.pk
            return self.render_to_response(context)


    def post(self, request):
        for key in request.POST:
            user = User.objects.get(pk=request.user.pk)
            if key.startswith('delete_'):
                UserMeteostations.objects.get(user=request.user.pk, meteostation_id=int(key.split('_')[-1])).delete()
            elif key.startswith('add_number_'):
                meteo_number = key.split('_')[-1]
                station = Meteostations.objects.get(pk=meteo_number)
                um = UserMeteostations(user=request.user, meteostation=station)
                um.save()
        return redirect('my_stations')


@csrf_exempt
def add_indicators(request):
    if request.method == 'POST':
        data = request.POST
        try:
            station = Meteostations.objects.get(pk=data['thisMeteoID'])
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
