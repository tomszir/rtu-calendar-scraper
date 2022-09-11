from dataclasses import dataclass
from datetime import datetime
from typing import Any
from bs4 import Tag


@dataclass
class SemesterData:
  """
  Represents the data of an RTU calendar semester.
  """
  id: str
  label: str

  @staticmethod
  def from_tag(tag: Tag):
    """
    Creates a SemesterData object from a BeautifulSoup tag.
    """
    return SemesterData(
      id=str(tag['value']),
      label=tag.text
    )


@dataclass
class ProgramData:
  """
  Represents the data of an RTU study program.
  """
  id: str
  title: str
  code: str

  @property
  def label(self):
    return f'{self.code} - {self.title}'

  @staticmethod
  def from_json(json: Any):
    """
    Creates a ProgramData object from a json response.
    """
    return ProgramData(
        id=json['programId'],
        title=json['titleLV'],
        code=json['code']
      )


@dataclass
class DepartmentData:
  """
  Represents the data of an RTU department.
  """
  id: str
  title: str
  code: str
  programs: list[ProgramData]

  @property
  def label(self):
    return self.title

  @staticmethod
  def from_json(json: Any):
    """
    Creates a DepartmentData object from a json response.
    """
    return DepartmentData(
        id=json['departmentId'],
        title=json['titleLV'],
        code=json['code'],
        programs=list(map(ProgramData.from_json, json['program']))
      )


@dataclass
class CourseData:
  """
  Represents the course data of an RTU study program.
  """
  id: str
  label: str

  @staticmethod
  def from_json(json: Any):
    """
    Creates a CourseData object from a json response.
    """
    return CourseData(
      id=json,
      label=f'{json}. kurss'
    )


@dataclass
class GroupData:
  """
  Represents the group data of an RTU course.
  """
  id: str
  semester_program_id: str
  label: str

  @staticmethod
  def from_json(json: Any):
    """
    Creates a GroupData object from a json response.
    """
    return GroupData(
      id=json['group'],
      label=f'{json["group"]}. grupa',
      semester_program_id=json['semesterProgramId']
    )


@dataclass
class EventData:
  """
  Represents of an RTU calendar event for a semester program.
  """
  subject: str
  location: str
  date: datetime
  start_datetime: datetime
  end_datetime: datetime

  @staticmethod
  def from_json(json: Any):
    """
    Creates an EventData object from a json response.
    """
    date = datetime.fromtimestamp(json['eventDate'] // 1000)

    start_time = json['customStart']
    start_time = date.replace(
      hour=start_time['hour'], minute=start_time['minute'])

    end_time = json['customEnd']
    end_time = date.replace(
      hour=end_time['hour'], minute=end_time['minute'])

    return EventData(
      subject=json['eventTempName'],
      location=json['roomInfoText'],
      date=date,
      start_datetime=start_time,
      end_datetime=end_time
    )


class CalendarData:
  """
  Stores all data related to working with the calendar API.
  """
  semester: SemesterData
  department: DepartmentData
  program: ProgramData
  course: CourseData
  group: GroupData
  events: list[EventData]

  @property
  def for_api(self):
    """
    Create a data dictionary for passing to the api.
    """
    data: dict[str, str | int] = {}

    if hasattr(self, 'semester') and self.semester is not None:
      data['semesterId'] = self.semester.id
    if hasattr(self, 'program') and self.program is not None:
      data['programId'] = self.program.id
    if hasattr(self, 'course') and self.course is not None:
      data['courseId'] = self.course.id
    if hasattr(self, 'group') and self.group is not None:
      data['semesterProgramId'] = self.group.semester_program_id
    return data
