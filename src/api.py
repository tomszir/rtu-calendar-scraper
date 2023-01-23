import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from src.data import CalendarData, EventData, SemesterOptionData, SemesterData, DepartmentData, CourseData, GroupData


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
  def get(cls, path: str, data: CalendarData):
    """
    Makes an HTTP GET request to a specified path with some data.
    """
    return requests.get(f'{cls.BASE_URL}/{path}', data=data.for_api)

  @classmethod
  def post(cls, path: str, data: CalendarData, required_data: list[str] = []):
    """
    Makes an HTTP POST request to a specified path with some data.
    """
    cls.assert_data(data.for_api, required_data)
    return requests.post(f'{cls.BASE_URL}/{path}', data=data.for_api)

  @classmethod
  def semesters(cls, data: CalendarData):
    """
    Scrapes the semesters from the calendar.
    """
    soup = BeautifulSoup(cls.get('/', data).text, 'html.parser')
    options = soup.select('#semester-id option')
    return list(map(SemesterOptionData.from_tag, options))

  @classmethod
  def semester(cls, data: CalendarData):
    """
    Get data about an RTU semester.
    """
    required_data = ['semesterId']
    json = cls.post('getChousenSemesterStartEndDate', data, required_data).json()
    return SemesterData.from_json(json)

  @classmethod
  def departments(cls, data: CalendarData):
    """
    Get all of the departments & programs in the current semester.
    """
    required_data = ['semesterId']
    json = cls.post('findProgramsBySemesterId', data, required_data).json()
    return list(map(DepartmentData.from_json, json))

  @classmethod
  def courses(cls, data: CalendarData):
    """
    Get all of the courses in the current program.
    """
    required_data = ['semesterId', 'programId']
    json = cls.post('findCourseByProgramId', data, required_data).json()
    return list(map(CourseData.from_json, json))

  @classmethod
  def groups(cls, data: CalendarData):
    """
    Get all of the groups in the current program course.
    """
    required_data = ['semesterId', 'programId', 'courseId']
    json = cls.post('findGroupByCourseId', data, required_data).json()
    groups = list(map(GroupData.from_json, json))
    return list(filter(lambda group: int(group.id) > 0, groups))

  @classmethod
  def is_published(cls, data: CalendarData):
    """
    Check if a calendar is published for a course.
    """
    required_data = ['semesterProgramId']
    json = cls.post('isSemesterProgramPublished', data, required_data).json()
    return not not json

  @classmethod
  def events(cls, data: CalendarData):
    """
    Returns all of the calendar events for a course.
    """
    required_data = ['year', 'month', 'semesterProgramId']
    events: list[EventData] = []

    while data.semester.start_date.month <= data.semester.end_date.month:
      try:
        json = cls.post('getSemesterProgEventList', data, required_data).json()
      except:
        break

      if len(json) == 0:
        break

      data.semester.start_date = data.semester.start_date + relativedelta(months = 1)

      events.extend(list(map(EventData.from_json, json)))
    return events
