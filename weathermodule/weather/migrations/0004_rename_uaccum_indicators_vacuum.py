# Generated by Django 4.0.6 on 2022-08-09 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weather', '0003_meteostations_user_stations_counter_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='indicators',
            old_name='uaccum',
            new_name='vacuum',
        ),
    ]
