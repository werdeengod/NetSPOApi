from typing import TYPE_CHECKING

from netspoapi.models import Marks, DebtLesson, MarksInfo, StudentData
from netspoapi.utils import split_date_from_string, get_legit_type_tasks

if TYPE_CHECKING:
    from netspoapi import NetSPOApi
    from datetime import datetime


class StudentClient:
    def __init__(self, api: 'NetSPOApi', student_data: 'StudentData'):
        self._api = api
        self.student_data = student_data

    async def dashboard_marks(self) -> list['Marks']:
        """Средние баллы по предметам

        Return:
             Список предметов
        """
        target_id = self.student_data.student_id
        response = await self._api.make_request(
            url=f'/services/students/{target_id}/dashboard',
            method="get"
        )

        list_marks = [
            Marks(subject=subject['name'], marks=subject['mark'])
            for subject in response['subjects']
        ]

        return list_marks

    async def performance(self) -> list['Marks']:
        """Дневник с начала учебного полугодия

        Return:
             Список предметов с оценками
        """
        target_id = self.student_data.student_id
        response = await self._api.make_request(
            url=f'/services/reports/current/performance/{target_id}',
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

    async def debts(self, begin: 'datetime' = None, end: 'datetime' = None) -> list['DebtLesson']:
        """Студенческие долги

        Args:
            begin: Optional[datetime]
            end: Optional[datetime]

        Return:
            Список долгов
        """
        target_id = self.student_data.student_id

        if not begin or not end:
            response = await self._api.make_request(
                url=f'/services/reports/current/performance/{target_id}',
                method="get"
            )

            date_lessons = [date for month in response['monthsWithDays'] for date in month['daysWithLessons']]
            begin, end = (
                split_date_from_string(date_lessons[0]),
                split_date_from_string(date_lessons[-1])
            )

        response = await self._api.make_request(
            url=f'/services/students/{target_id}/lessons/{str(begin.date())}/{str(end.date())}',
            method="get",
        )

        return self._parse_debt_lessons(response)

    def _parse_debt_lessons(self, lessons_data) -> list['DebtLesson']:
        legit_type = get_legit_type_tasks()
        student_debts = []

        for days in lessons_data:
            for lesson in days['lessons']:
                if not lesson.get('name') or not lesson.get('gradebook') or not lesson['gradebook'].get('tasks'):
                    continue

                for task in lesson['gradebook']['tasks']:
                    if not task['isRequired']:
                        continue

                    marks = self._determine_debt_marks(task, lesson, legit_type)
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
    def _determine_debt_marks(task, lesson, legit_type) -> list[str]:
        marks = []
        if not task.get('mark') and (task['type'] in legit_type or lesson['gradebook']['lessonType'] in legit_type):
            marks.append('Точка')
        elif task.get('mark') == 'Two':
            marks.append('2')

        return marks
