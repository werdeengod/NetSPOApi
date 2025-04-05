from typing import TYPE_CHECKING
import datetime

from netspoapi.models import Marks, DebtLesson, MarksInfo, StudentData, Timetable, Lesson, Attestation, \
    AttestationSemesterMark
from netspoapi.utils import split_date_from_string, get_legit_type_tasks, get_fullname_client

if TYPE_CHECKING:
    from netspoapi import NetSPOApi


class StudentClient:
    def __init__(self, api: 'NetSPOApi', student_data: 'StudentData'):
        self._api = api

        self.target_id = student_data.student_id
        self.student_data = student_data

    async def dashboard(self) -> list['Marks']:
        """Средние баллы по предметам

        Return:
             Список предметов
        """
        response = await self._api.make_request(
            url=f'/services/students/{self.target_id}/dashboard',
            method="get"
        )

        list_marks = [
            Marks(subject=subject['name'], marks=subject['mark'])
            for subject in response['subjects']
        ]

        return list_marks

    async def performance(self) -> list['Marks']:
        """Дневник оценок с начала учебного полугодия

        Return:
             Список предметов с оценками
        """
        response = await self._api.make_request(
            url=f'/services/reports/current/performance/{self.target_id}',
            method="get"
        )

        list_marks = [
            Marks(
                subject=subject['subjectName'],
                marks=[MarksInfo(**mark) for mark in subject['daysWithMarks']],
            )
            for subject in response['daysWithMarksForSubject']
            if subject['daysWithMarks']
        ]

        return list_marks

    async def debts(self, begin: 'datetime.date' = None, end: 'datetime.date' = None) -> list['DebtLesson']:
        """Студенческие долги

        Args:
            begin: Optional[datetime]
            end: Optional[datetime]

        Return:
            Список долгов
        """
        if not begin or not end:
            date = datetime.datetime.now()

            if date.month > 7:
                begin, end = (
                    datetime.date(date.year, 9, 1),
                    datetime.date(date.year, 12, 31)
                )

            else:
                begin, end = (
                    datetime.date(date.year, 1, 1),
                    datetime.date(date.year, 8, 1)
                )

        response = await self._api.make_request(
            url=f'/services/students/{self.target_id}/lessons/{str(begin)}/{str(end)}',
            method="get",
        )

        return self._parse_debt_lessons(response)

    def _parse_debt_lessons(self, lessons_data: list) -> list['DebtLesson']:
        student_debts = []

        for days in lessons_data:
            for lesson in days['lessons']:
                if not lesson.get('name') or not lesson.get('gradebook') or not lesson['gradebook'].get('tasks'):
                    continue

                for task in lesson['gradebook']['tasks']:
                    if not task['isRequired']:
                        continue

                    marks = self._determine_debt_marks(task, lesson)
                    if marks:
                        student_debts.append(
                            DebtLesson(
                                subject=lesson['name'],
                                theme=lesson['gradebook']['themes'][0],
                                marks=MarksInfo(markValues=marks, day=split_date_from_string(days['date']))
                            )
                        )

        return student_debts

    @staticmethod
    def _determine_debt_marks(task: dict, lesson: str) -> list[str]:
        legit_type = get_legit_type_tasks()
        marks = []

        if not task.get('mark') and (task['type'] in legit_type or lesson['gradebook']['lessonType'] in legit_type):
            marks.append('Точка')

        elif task.get('mark') == 'Two':
            marks.append('2')

        return marks

    async def lessons(self, begin: 'datetime.date', end: 'datetime.date') -> list['Timetable']:
        """Получение уроков за определенный промежуток

        Args:
            begin: Optional[datetime]
            end: Optional[datetime]

        Return:
            Список из расписаний
        """
        response = await self._api.make_request(
            url=f'/services/students/{self.target_id}/lessons/{str(begin)}/{str(end)}',
            method="get",
        )

        timetables = []

        for date in response:

            lessons = []

            for index, lesson in enumerate(date['lessons']):
                if not lesson.get('name'):
                    continue

                tasks, themes = None, None

                if lesson.get('gradebook'):
                    tasks = [task['topic'] for task in lesson['gradebook']['tasks']]
                    themes = [theme for theme in lesson['gradebook']['themes']]

                lessons.append(
                    Lesson(
                        id=index + 1,
                        name=lesson['name'],
                        teacher=get_fullname_client(lesson['timetable']['teacher']),
                        cabinet=lesson['timetable']['classroom']['name'],
                        start_time=lesson['startTime'],
                        end_time=lesson['endTime'],
                        tasks=tasks,
                        themes=themes
                    )
                )

            timetables.append(
                Timetable(
                    date=split_date_from_string(date['date']),
                    lessons=lessons
                )
            )

        return timetables

    async def attestation(self, course_number: int = None, semester: int = None) -> list['Attestation']:
        """Получение аттестации студента

        Args:
            course_number: Курс оценок
            semester: Семестр оценок

        Return:
            Список учебных предметов с аттестационными оценками

        """
        if semester and not course_number:
            raise ValueError("Specify a course to indicate the semester!")

        response = await self._api.make_request(
            url=f'/services/students/{self.target_id}/attestation',
            method="get",
        )

        semester_data = self._extract_semester_data(response['academicYears'], course_number, semester)
        attestation = []

        for subject in response['subjects']:

            semester_marks = [
                AttestationSemesterMark(
                    course_number=course,
                    semester_number=sem_number,
                    mark=subject['marks'].get(str(term_id), {}).get('value', None)
                )
                for course, term_id, sem_number in semester_data
                if str(term_id) in subject['marks']
            ]

            if not semester_marks and course_number:
                continue

            attestation.append(
                Attestation(
                    subject_name=subject['name'],
                    final_mark=subject['finalMark'].get('value', None),
                    semester_marks=semester_marks
                )
            )

        return attestation

    @staticmethod
    def _extract_semester_data(academic_years: list, course_number: int = None, semester: int = None) -> list:
        semester_data = []

        if course_number:
            year_index = course_number - 1
            if year_index >= len(academic_years):
                return []

            terms = academic_years[year_index]['terms']

            if semester:
                if semester - 1 < len(terms):
                    term = terms[semester - 1]
                    semester_data.append((course_number, term['id'], term['number']))

            else:
                for term in terms:
                    semester_data.append((course_number, term['id'], term['number']))

        else:
            for academic_year in academic_years:
                for term in academic_year['terms']:
                    semester_data.append((academic_year['number'], term['id'], term['number']))

        return semester_data


