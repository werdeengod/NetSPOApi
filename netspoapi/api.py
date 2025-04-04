from typing import TYPE_CHECKING

import hashlib
import base64
import json

from netspoapi.base import BaseClient
from netspoapi.models import Marks, DebtLesson, MarksInfo, StudentData
from netspoapi.utils import split_date_from_string, get_legit_type_tasks

if TYPE_CHECKING:
    from datetime import datetime
    from http.cookies import SimpleCookie


class NetSPOApi(BaseClient):
    def __init__(
        self,
        target_id: int = None,
        cookies: 'SimpleCookie' = None
    ):
        super().__init__()

        self.target_id = target_id
        self.cookies = cookies

        self.student_data: 'StudentData' = None

    async def __aenter__(self) -> 'NetSPOApi':
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def login(self, login: str, password: str) -> 'NetSPOApi':
        sha256 = hashlib.sha256(password.encode('utf-8')).digest()
        password = base64.b64encode(sha256).decode()
        data = {"login": login, "password": password}

        response = await self._make_request(
            url='/services/security/login',
            method="post",
            data=json.dumps(data)
        )

        organization = response.json['tenants']['spo_30']['settings']['organization']['abbreviation']
        students = response.json['tenants']['spo_30']['studentRole']['students'][0]
        student_name = " ".join([students[key] for key in ('lastName', 'firstName', 'middleName')]).strip()

        self.target_id = students['id']
        self.cookies = response.cookies

        self.student_data = StudentData(
            student_name=student_name.strip(),
            group_name=students['groupName'],
            college_name=organization
        )

        return self

    async def dashboard_marks(self) -> list['Marks']:
        response = await self._make_request(
            url=f'/services/students/{self.target_id}/dashboard',
            method="get",
            cookies=self.cookies
        )

        list_marks = [
            Marks(
                subject=subject['name'],
                marks=subject['mark']
            )
            for subject in response.json['subjects']
        ]

        return list_marks

    async def performance(self) -> list['Marks']:
        response = await self._make_request(
            url=f'/services/reports/current/performance/{self.target_id}',
            method="get",
            cookies=self.cookies
        )

        list_marks = [
            Marks(
                subject=subject['subjectName'],
                marks=[MarksInfo(**mark) for mark in subject['daysWithMarks']],
            )
            for subject in response.json['daysWithMarksForSubject']
            if subject['daysWithMarks']
        ]

        return list_marks

    async def student_debts(
        self,
        begin_datetime: 'datetime' = None,
        end_datetime: 'datetime' = None
    ) -> list['DebtLesson']:

        if not begin_datetime or not end_datetime:
            response = await self._make_request(
                url=f'/services/reports/current/performance/{self.target_id}',
                method="get",
                cookies=self.cookies
            )

            date_lessons = [date for month in response.json['monthsWithDays'] for date in month['daysWithLessons']]
            begin_datetime, end_datetime = (
                split_date_from_string(date_lessons[0]),
                split_date_from_string(date_lessons[-1])
            )

        response = await self._make_request(
            url=f'/services/students/{self.target_id}/lessons/{str(begin_datetime.date())}/{str(end_datetime.date())}',
            method="get",
            cookies=self.cookies
        )

        return self._parse_debt_lessons(response.json)

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
