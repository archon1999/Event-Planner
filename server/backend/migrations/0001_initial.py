# Generated by Django 4.0.4 on 2022-12-22 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CalendarEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('event_type', models.IntegerField(choices=[(1, 'Once'), (2, 'Daily'), (3, 'Weekly'), (4, 'Yearly')])),
                ('notes', models.TextField()),
            ],
        ),
    ]
