
import os
from typing import Callable
from src.api import CalendarAPI
from src.data import CalendarData
from src.writer import CalendarWriter


class CalendarScraper:
  """
  Main class for scraping the RTU calendar, handles the program flow.
  """
  data: CalendarData = CalendarData()
  prompts: list[Callable] = []

  def __init__(self):
    self.prompts = [
      self.prompt_semesters,
      self.prompt_departments,
      self.prompt_programs,
      self.prompt_courses,
      self.prompt_groups,
    ]

  def run(self):
    """
    Runs all of the calendar scrapers steps.
    """
    for prompt in self.prompts:
      prompt()

    if not CalendarAPI.is_published(self.data.for_api):
      return print('Programma vēl nav publicēta.')

    self.data.events = CalendarAPI.events(2022, 9, self.data.for_api)

    writer = CalendarWriter(self.data)
    writer.write()

  def prompt_semesters(self):
    """
    Prompts the user to select a semester.
    """
    semesters = CalendarAPI.semesters()
    message = "Lūdzu izvēlies semestri"
    self.data.semester = self.get_from_option(semesters, message)

  def prompt_departments(self):
    """
    Prompts the user to select a department.
    """
    departments = CalendarAPI.departments(self.data.for_api)
    message = "Lūdzu izvēlies departamentu"
    self.data.department = self.get_from_option(departments, message)

  def prompt_programs(self):
    """
    Prompts the user to select a program.
    """
    programs = self.data.department.programs
    message = "Lūdzu izvēlies programmu"
    self.data.program = self.get_from_option(programs, message)

  def prompt_courses(self):
    """
    Prompts the user to select a course.
    """
    courses = CalendarAPI.courses(self.data.for_api)
    message = "Lūdzu izvēlies kursu"
    self.data.course = self.get_from_option(courses, message)

  def prompt_groups(self):
    """
    Prompts the user to select a group.
    """
    groups = CalendarAPI.groups(self.data.for_api)
    message = "Lūdzu izvēlies grupu"
    self.data.group = self.get_from_option(groups, message)

  def get_from_option(self, options: list, message: str = 'Lūdzu izvēlies opciju'):
    """
    Prompts the user to make a selection from options.
    """
    if len(options) == 1:
      return options[0]
    while True:
      os.system('cls||clear')

      for index, option in enumerate(options):
        print(f'#{str(index + 1)}: {option.label}')

      index = int(input(f'{message}: '))

      if index <= 0 or index > len(options):
        continue
      return options[index - 1]
