import os
import csv
import requests
from bs4 import BeautifulSoup
from typing import Callable
from datetime import date, datetime

def option(data: list, msg: str, label: Callable[..., str]):
  if len(data) == 1:
    return data[0]
  while True:
    os.system('cls')

    for i, o in enumerate(data):
      print(f"#{i + 1}: {label(o)}")

    index = int(input(msg))

    if index <= 0 or index > len(data):
      continue

    return data[index - 1]

class CalendarEvent:
  def __init__(self, data: dict):
    self.subject = data['eventTempName']
    self.start_date = self.get_date_string(data['eventDate'])
    self.start_time = self.get_time_string(data['customStart'])
    self.end_date = self.get_ics_date_string(data['eventDate'])
    self.end_time = self.get_time_string(data['customEnd'])
    self.location = data['roomInfoText']

  def get_date_string(self, milliseconds: int):
    return datetime.fromtimestamp(milliseconds // 1000).strftime('%d/%m/%Y')

  def get_ics_date_string(self, milliseconds: int):
    return datetime.fromtimestamp(milliseconds // 1000).strftime('%Y%m%d')

  def get_time_string(self, time: dict):
    hour = str(time['hour']).zfill(2)
    minute = str(time['minute']).zfill(2)
    return datetime.strptime(f"{hour}:{minute}", "%H:%M").strftime("%I:%M %p")

  def get_ics_time_string(self, time: dict):
    hour = str(time['hour']).zfill(2)
    minute = str(time['minute']).zfill(2)
    return datetime.strptime(f"{hour}:{minute}", "%H:%M").strftime("T%H%M00Z")

  def get_csv_data(self):
    return [self.subject, self.start_date, self.start_time, self.end_date, self.end_time, self.location]

  def get_ics_data(self):
    return [f'BEGIN:VEVENT\nDTSTART:{self.start_date}{self.start_time}\nDTEND:{self.end_date}{self.end_time}\nDESCRIPTION:\nLOCATION:{self.location}\nSEQUENCE:0\nSTATUS:CONFIRMED\nSUMMARY:{self.subject}\nEND:VEVENT']

  @classmethod
  def get_csv_header_data(cls):
    return ['SUBJECT', 'START DATE', 'START TIME', 'END DATE', 'END TIME', 'LOCATION']

  @classmethod
  def get_ics_header_data(cls):
    return ['BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN']

  @classmethod
  def get_ics_footer_data(cls):
    return ['END:VCALENDAR']

class CalendarScraper:
  BASE_URL = 'https://nodarbibas.rtu.lv'

  def __init__(self):
    self.semester_id = 0
    self.program_id = 0
    self.course_id = 0
    self.group_id = 0
    self.semester_program_id = 0
    self.year = 2022
    self.month = 9

  def scrape(self):
    semesters = self._get_semesters()
    semester = option(semesters, 'Izvēlies semestri: ', lambda o: o['label'])
    self.semester_id = semester['id']

    departments = self._get_departments()
    department = option(departments, 'Izvēlies departamentu: ',
                        lambda o: o['titleLV'])
    program = option(department['program'], 'Izvēlies programmu: ',
                     lambda o: f'{o["code"]} - {o["titleLV"]}')
    self.program_id = program['programId']

    courses = self._get_courses()
    course = option(courses, 'Izvēlies kursu: ', lambda o: f'{o}. kurss')
    self.course_id = course

    groups = self._get_groups()
    group = option(groups, 'Izvēlies grupu: ',
                   lambda o: f'{o["group"]}. grupa')
    self.group_id = group['group']
    self.semester_program_id = group['semesterProgramId']

    if not self._is_published():
      print("Programma vēl nav publicēta")
      return

    fileFormats = [{"id": 0, "label": ".csv"}, {"id": 1, "label": ".ics"}, {"id": 2, "label": ".csv un .ics"}]
    fileFormat = option(fileFormats, 'Izvēlies formatu: ', lambda o: o['label'])

    if(fileFormat['label'] == ".csv"):
      self._save_to_csv()
    elif(fileFormat['label'] == ".ics"):
      self._save_to_ics()
    else:
      self._save_to_csv()
      self._save_to_ics()

  def _save_to_csv(self):
    events = []

    for month in range(9, 13):
      self.month = month
      events.extend(self._get_event_list())

    with open('./data.csv', mode='w', encoding='UTF-8') as file:
      writer = csv.writer(file)
      writer.writerow(CalendarEvent.get_csv_header_data())

      for event in events:
        writer.writerow(event.get_csv_data())

    print("Kalendārs ir izveidots 'data.csv' failā!")

  def _save_to_ics(self):
    events = []

    for month in range(9, 13):
      self.month = month
      events.extend(self._get_event_list())

    with open('./data.ics', mode='w', newline='', encoding='UTF-8') as file:
      writer = csv.writer(file, escapechar=' ', quoting=csv.QUOTE_NONE)
      writer.writerow(CalendarEvent.get_ics_header_data())

      for event in events:
        writer.writerow(event.get_ics_data())

      writer.writerow(CalendarEvent.get_ics_footer_data())

    print("Kalendārs ir izveidots 'data.ics' failā!")

  def _get(self, path: str, data: dict = {}):
    return requests.get(f'{self.BASE_URL}/{path}', data=data)

  def _post(self, path: str, data: dict = {}):
    return requests.post(f'{self.BASE_URL}/{path}', data={
        'semesterId': self.semester_id,
        'programId': self.program_id,
        'courseId': self.course_id,
        'semesterProgramId': self.semester_program_id,
        'year': self.year,
        'month': self.month
    })

  def _get_semesters(self):
    s = BeautifulSoup(self._get('/').text, "html.parser")

    semester_options = s.select('#semester-id option')
    semesters = []

    for option in semester_options:
      semesters.append({
        'id': option['value'],
        'label': option.text
      })

    return semesters

  def _get_departments(self):
    return self._post('findProgramsBySemesterId').json()

  def _get_courses(self):
    return self._post('findCourseByProgramId').json()

  def _get_groups(self):
    return list(filter(lambda g: int(g['group']) > 0, self._post('findGroupByCourseId').json()))

  def _is_published(self):
    return self._post('isSemesterProgramPublished').json()

  def _get_event_list(self):
    return list(map(lambda e: CalendarEvent(e), self._post('getSemesterProgEventList').json()))

if __name__ == '__main__':
  scraper = CalendarScraper()
  scraper.scrape()
