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
      writer = csv.writer(file, delimiter=';')
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

    # Timezone data for ical based off tzurl.org
    timezone = '\n'.join(
        ['BEGIN:VTIMEZONE', 'TZID:Europe/Riga', 'LAST-MODIFIED:20220816T024022Z',
         'TZURL:http://tzurl.org/zoneinfo-outlook/Europe/Riga',
         'X-LIC-LOCATION:Europe/Riga',
         'BEGIN:DAYLIGHT',
         'TZNAME:EEST',
         'TZOFFSETFROM:+0200',
         'TZOFFSETTO:+0300',
         'DTSTART:19700329T030000',
         'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU',
         'END:DAYLIGHT',
         'BEGIN:STANDARD',
         'TZNAME:EET',
         'TZOFFSETFROM:+0300',
         'TZOFFSETTO:+0200',
         'DTSTART:19701025T040000',
         'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU',
         'END:STANDARD',
         'END:VTIMEZONE']
    )

    footer = '\n'.join(['END:VCALENDAR'])

    datetime_format = "%Y%m%dT%H%M00"

    with open(f'{self.filename}.ics', mode='w', encoding="utf-8") as file:

      file.write(header + '\n')
      file.write(timezone + '\n')

      for event in self.data.events:
        time_stamp = datetime.datetime.now().strftime(datetime_format)
        start_time = event.start_datetime.strftime(datetime_format)
        end_time = event.end_datetime.strftime(datetime_format)
        row = [
            f'BEGIN:VEVENT',
            f'UID:{uuid.uuid4()}',
            f'DTSTAMP:{time_stamp}',
            f'DTSTART;TZID=Europe/Riga:{start_time}',
            f'DTEND;TZID=Europe/Riga:{end_time}',
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
