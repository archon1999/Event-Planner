"""В этом файле описаны модели для представления таблиц базы данных"""

from django.db import models


class CalendarEvent(models.Model):
    class EventType(models.IntegerChoices):
        ONCE = 1, 'Единожды'
        DAILY = 2, 'Ежедневно'
        WEEKLY = 3, 'Ежеденельно'
        YEARLY = 4, 'Ежегодно'

    datetime = models.DateTimeField()
    event_type = models.IntegerField(choices=EventType.choices)
    notes = models.TextField()
