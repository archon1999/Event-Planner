import datetime
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk

from tkcalendar import Calendar, DateEntry
from tktimepicker import SpinTimePickerModern, constants
from django.utils import timezone
from django.db.models import Q

import config
from backend.models import CalendarEvent

MAIN_COLOR = '#f9f9f9'


class Window(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        master.title('Планировщик событий')
        master.geometry('600x600+100+100')

        ttk.Button(text='Управление событиями',
                   command=self.manage_events_window).pack(padx=10, pady=10)
        self.calendar = Calendar(selectmode='day', weekenddays=[7, 7],
                                 locale='ru_RU')
        self.calendar.pack(fill="both", expand=True)
        self.calendar.bind('<<CalendarSelected>>', self.on_calendar_selected)
        self.calendar.bind('<<CalendarMonthChanged>>', self.on_month_changed)
        self.detail_for_day_var = tk.StringVar()
        tk.Label(textvariable=self.detail_for_day_var).pack(padx=10, pady=20)
        self.calendar_events_reload()

    def on_calendar_selected(self, _):
        dt = datetime.datetime.strptime(self.calendar.get_date(),
                                        '%d.%m.%Y')
        calendar_events = self.get_calendar_events_for_day(dt)
        text = 'События на: ' + dt.strftime('%d/%m/%Y') + '\n'
        for calendar_event in calendar_events:
            time = calendar_event.datetime.strftime('%H:%M')
            text += f'{time} - {calendar_event.notes.strip()}\n'

        self.detail_for_day_var.set(text)

    def on_month_changed(self, _):
        month, year = self.calendar.get_displayed_month()
        dt = datetime.datetime(year, month, 1)
        self.calendar.calevent_remove('all')
        while dt.month == month:
            calendar_events = self.get_calendar_events_for_day(dt)
            for index, calendar_event in enumerate(calendar_events):
                tags = f'{calendar_event.pk}-{index}'
                text = calendar_event.notes.strip()
                self.calendar.calevent_create(date=dt.date(),
                                              text=text,
                                              tags=tags)
            dt += datetime.timedelta(days=1)

    def calendar_events_reload(self):
        self.on_month_changed(None)

    @staticmethod
    def get_calendar_events_for_day(dt: datetime.datetime):
        return CalendarEvent.objects.filter(
            datetime__date__lte=dt.date()
        ).filter(
            Q(datetime__iso_week_day=dt.isoweekday(),
              event_type=CalendarEvent.EventType.WEEKLY) |
            Q(datetime__date=dt.date(),
              event_type=CalendarEvent.EventType.ONCE) |
            Q(datetime__month=dt.month,
              datetime__day=dt.day,
              event_type=CalendarEvent.EventType.YEARLY) |
            Q(event_type=CalendarEvent.EventType.DAILY)
        )

    def manage_events_window(self):
        top = tk.Toplevel(background=MAIN_COLOR)
        top.geometry('780x600+400+100')
        label = tk.Label(top,
                         text='Управление событиями',
                         font=tk.font.Font(size=20),
                         background=MAIN_COLOR)
        label.place(x=240, y=60)
        events_table = ttk.Treeview(top, height=20)
        events_table.column("#0", width=0,  stretch=tk.NO)
        events_table['columns'] = ('datetime', 'event_type', 'notes')
        events_table.heading('datetime', text='Дата и время', anchor=tk.CENTER)
        events_table.heading('event_type', text='Тип', anchor=tk.CENTER)
        events_table.heading('notes', text='Заметки', anchor=tk.CENTER)
        events_table.column('datetime', width=200, anchor=tk.CENTER)
        events_table.column('event_type', anchor=tk.CENTER, width=100)
        events_table.column('notes', anchor=tk.CENTER, width=350)
        events_table.place(x=60, y=120)

        calendar_events = CalendarEvent.objects.all()
        for event in calendar_events:
            dt = timezone.localtime(event.datetime)
            values = [dt.strftime('%d/%m/%Y %H:%M'),
                      event.get_event_type_display(),
                      event.notes]
            events_table.insert(parent='', index=tk.END, iid=event.pk,
                                text='', values=values)

        def edit_button_click():
            if not events_table.selection():
                return

            pk = int(events_table.selection()[0])
            calendar_event = CalendarEvent.objects.get(pk=pk)
            self.event_edit_window(calendar_event, top)
            self.calendar_events_reload()

        def add_button_click():
            self.event_add_window(top)
            self.calendar_events_reload()

        def delete_button_click():
            if not events_table.selection():
                return

            pk = int(events_table.selection()[0])
            calendar_event = CalendarEvent.objects.get(pk=pk)
            calendar_event.delete()
            self.calendar_events_reload()
            top.destroy()
            self.manage_events_window()

        ttk.Button(top, text='Удалить',
                   command=delete_button_click).place(x=465, y=560)
        ttk.Button(top, text='Изменить',
                   command=edit_button_click).place(x=550, y=560)
        ttk.Button(top, text='Добавить',
                   command=add_button_click).place(x=635, y=560)

    def event_add_window(self, top_frame):
        top = tk.Toplevel()
        top_datetime = tk.Frame(top)
        tk.Label(top_datetime,
                 text='Дата и время:').pack(side=tk.LEFT, padx=50)
        date_entry = DateEntry(top_datetime, width=12, borderwidth=2)
        date_entry.pack(side=tk.LEFT, padx=10, pady=10)
        time_picker = SpinTimePickerModern(top_datetime)
        time_picker.addAll(constants.HOURS24)
        time_picker.configureAll(height=2, fg="#ffffff",
                                 font=("Times", 16))
        time_picker.pack(side=tk.LEFT, padx=10, pady=10)
        top_datetime.pack()

        top_event_type = tk.Frame(top)
        tk.Label(top_event_type, text='Тип:').pack(side=tk.LEFT, padx=55)
        event_type_values = ['Единожды', 'Ежедневно',
                             'Еженедельно', 'Ежегодно']
        event_type_var = tk.StringVar(value=event_type_values[0])
        event_type_combobox = ttk.Combobox(top_event_type,
                                           textvariable=event_type_var,
                                           values=event_type_values)
        event_type_combobox.pack(side=tk.LEFT, padx=10, pady=10)
        top_event_type.pack()

        top_notes = tk.Frame(top)
        tk.Label(top_notes, text='Заметки:').pack(side=tk.LEFT, padx=50)
        notes_entry = tk.Text(top_notes, height=5, width=20)
        notes_entry.pack(padx=10, pady=10)
        top_notes.pack()

        def add_button_click():
            date = date_entry.get_date()
            hour, minute, _ = time_picker.time()
            dt = datetime.datetime(date.year, date.month, date.day,
                                   hour, minute)
            dt = dt.replace(tzinfo=timezone.get_default_timezone())
            event_type = event_type_values.index(event_type_var.get())+1
            notes = notes_entry.get('0.0', tk.END)
            CalendarEvent.objects.create(
                datetime=dt,
                event_type=event_type,
                notes=notes,
            )
            messagebox.showinfo('Успешно', 'Событие добавлено')
            top.destroy()
            top_frame.destroy()
            self.manage_events_window()

        ttk.Button(top, text='Добавить',
                   command=add_button_click).pack(pady=10)

    def event_edit_window(self, event: CalendarEvent, top_frame):
        top = tk.Toplevel()
        top_datetime = tk.Frame(top)
        tk.Label(top_datetime,
                 text='Дата и время:').pack(side=tk.LEFT, padx=50)
        date_entry = DateEntry(top_datetime, width=12, borderwidth=2)
        dt = timezone.localtime(event.datetime)
        date = dt.date()
        date_entry.set_date(date)
        date_entry.pack(side=tk.LEFT, padx=10, pady=10)
        time_picker = SpinTimePickerModern(top_datetime)
        time_picker.addAll(constants.HOURS24)
        time_picker.set24Hrs(dt.hour)
        time_picker.setMins(dt.minute)
        time_picker.configureAll(height=2, fg="#ffffff",
                                 font=("Times", 16))
        time_picker.pack(side=tk.LEFT, padx=10, pady=10)
        top_datetime.pack()

        top_event_type = tk.Frame(top)
        tk.Label(top_event_type, text='Тип:').pack(side=tk.LEFT, padx=55)
        event_type_values = ['Единожды', 'Ежедневно',
                             'Еженедельно', 'Ежегодно']
        event_type_var = tk.StringVar(
            value=event_type_values[event.event_type-1])
        event_type_combobox = ttk.Combobox(top_event_type,
                                           textvariable=event_type_var,
                                           values=event_type_values)
        event_type_combobox.pack(side=tk.LEFT, padx=10, pady=10)
        top_event_type.pack()

        top_notes = tk.Frame(top)
        tk.Label(top_notes, text='Заметки:').pack(side=tk.LEFT, padx=50)
        notes_entry = tk.Text(top_notes, height=5, width=20)
        notes_entry.pack(padx=10, pady=10)
        notes_entry.insert('0.0', event.notes)
        top_notes.pack()

        def save_button_click():
            date = date_entry.get_date()
            hour, minute, _ = time_picker.time()
            dt = datetime.datetime(date.year, date.month, date.day,
                                   hour, minute)
            dt = dt.replace(tzinfo=timezone.get_default_timezone())
            event_type = event_type_values.index(event_type_var.get())+1
            notes = notes_entry.get('0.0', tk.END)
            event.datetime = dt
            event.event_type = event_type
            event.notes = notes
            event.save()
            messagebox.showinfo('Успешно', 'Событие сохранено')
            top.destroy()
            top_frame.destroy()
            self.manage_events_window()

        ttk.Button(top, text='Сохранить',
                   command=save_button_click).pack(pady=10)


def main():
    app = Window(tk.Tk())
    app.master.mainloop()


if __name__ == '__main__':
    main()
