import requests
from bs4 import BeautifulSoup
from typing import Optional

from src.data import EventData, SemesterData, DepartmentData, CourseData, GroupData


class CalendarAPI:
  """
  Fetches calendar-related data from the RTU calendar API.
  """
  BASE_URL: str = 'https://nodarbibas.rtu.lv'

  @classmethod
  def assert_data(cls, data: dict[str, str | int], required_data: list[str]):
    """
    Throws an exception if required data is missing.
    """
    for key in required_data:
      if key not in data:
        raise Exception(
          f'Required API data-key "{key}" is not set!')

  @classmethod
  def get(cls, path: str, data: Optional[dict[str, str | int]] = {}):
    """
    Makes an HTTP GET request to a specified path with some data.
    """
    return requests.get(f'{cls.BASE_URL}/{path}', data=data)

  @classmethod
  def post(cls, path: str, data: dict[str, str | int] = {}, required_data: list[str] = []):
    """
    Makes an HTTP POST request to a specified path with some data.
    """
    cls.assert_data(data, required_data)
    return requests.post(f'{cls.BASE_URL}/{path}', data=data)

  @classmethod
  def semesters(cls):
    """
    Scrapes the semesters from the calendar.
    """
    soup = BeautifulSoup(cls.get('/').text, 'html.parser')
    options = soup.select('#semester-id option')
    return list(map(SemesterData.from_tag, options))

  @classmethod
  def departments(cls, data: dict[str, str | int] = {}):
    """
    Get all of the departments & programs in the current semester.
    """
    required_data = ['semesterId']
    json = cls.post('findProgramsBySemesterId', data, required_data).json()
    return list(map(DepartmentData.from_json, json))

  @classmethod
  def courses(cls, data: dict[str, str | int] = {}):
    """
    Get all of the courses in the current program.
    """
    required_data = ['semesterId', 'programId']
    json = cls.post('findCourseByProgramId', data, required_data).json()
    return list(map(CourseData.from_json, json))

  @classmethod
  def groups(cls, data: dict[str, str | int] = {}):
    """
    Get all of the groups in the current program course.
    """
    required_data = ['semesterId', 'programId', 'courseId']
    json = cls.post('findGroupByCourseId', data, required_data).json()
    groups = list(map(GroupData.from_json, json))
    return list(filter(lambda group: int(group.id) > 0, groups))

  @classmethod
  def is_published(cls, data: dict[str, str | int] = {}):
    """
    Check if a calendar is published for a course.
    """
    required_data = ['semesterProgramId']
    json = cls.post('isSemesterProgramPublished', data, required_data).json()
    return not not json

  @classmethod
  def events(cls, year: int, month: int, data: dict[str, str | int] = {}):
    """
    Returns all of the calendar events for a course.
    """
    data['year'] = year
    data['month'] = month
    required_data = ['year', 'month', 'semesterProgramId']
    events: list[EventData] = []

    while True:
      try:
        json = cls.post('getSemesterProgEventList', data, required_data).json()
      except:
        break

      if len(json) == 0:
        break

      data['month'] = int(data['month']) + 1

      if data['month'] > 12:
        data['year'] = int(data['year']) + 1
        data['month'] = 1

      events.extend(list(map(EventData.from_json, json)))
    return events
