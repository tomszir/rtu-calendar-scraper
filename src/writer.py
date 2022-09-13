import datetime
import os
import csv
import uuid

from src.data import CalendarData


class CalendarWriter:
  """
  Handles the writing of calendar events to files.
  """

  def __init__(self, data: CalendarData):
    self.data = data
    os.makedirs(os.path.dirname(self.filename), exist_ok=True)

  def write(self):
    """
    Writes the calendar events to all available format files.
    """
    self.write_csv()
    self.write_ics()
    print('Pabeigts! Dati ir izvadīti "output" mapē')

  def write_csv(self):
    """
    Writes the calendar events to a csv file.
    """
    header = ['SUBJECT', 'START DATE', 'START TIME',
              'END DATE', 'END TIME', 'LOCATION']
    date_format = "%d/%m/%Y"
    time_format = "%I:%M %p"

    with open(f'{self.filename}.csv', mode='w', encoding="utf-8") as file:
      writer = csv.writer(file)
      writer.writerow(header)

      for event in self.data.events:
        date = event.date.strftime(date_format)
        start_time = event.start_datetime.strftime(time_format)
        end_time = event.end_datetime.strftime(time_format)
        row = [event.subject, date, start_time, date, end_time, event.location]
        writer.writerow(row)

  def write_ics(self):
    """
    Writes the calendar events to an iCalendar format file.
    """
    header = '\n'.join(
      ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//tomszir/rtu-calendar-scraper//LV', 'CALSCALE:GREGORIAN'])
    footer = '\n'.join(['END:VCALENDAR'])

    datetime_format = "%Y%m%dT%H%M00Z"

    with open(f'{self.filename}.ics', mode='w', encoding="utf-8") as file:
      file.write(header + '\n')
      for event in self.data.events:
        time_stamp = datetime.datetime.now().strftime(datetime_format)
        start_time = event.start_datetime.strftime(datetime_format)
        end_time = event.end_datetime.strftime(datetime_format)
        row = [
            f'BEGIN:VEVENT',
            f'UID:{uuid.uuid4()}',
            f'DTSTAMP:{time_stamp}',
            f'DTSTART:{start_time}',
            f'DTEND:{end_time}',
            f'DESCRIPTION:',
            f'LOCATION:{event.location}',
            f'SEQUENCE:0',
            f'STATUS:CONFIRMED',
            f'SUMMARY:{event.subject}',
            f'END:VEVENT'
        ]
        file.write('\n'.join(row) + '\n')
      file.write(footer)

  @property
  def filename(self):
    return f'./output/{self.data.program.code}_{self.data.course.id}_{self.data.group.id}'
