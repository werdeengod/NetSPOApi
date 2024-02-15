from netspoapi.loader import HttpLoader
from netspoapi.schemas import TargetLogin, Marks, DebtLesson, MarksInfo
from netspoapi.utils import get_debts


class NetSPOApi:
    def __init__(self, target: 'TargetLogin'):
        self.target = target

    @classmethod
    async def login(cls, login: str, password: str) -> 'NetSPOApi':
        response = await HttpLoader().login(login, password)

        spo_30 = response.json['tenants']['spo_30']
        students = spo_30['studentRole']['students'][0]

        return cls(
            TargetLogin(
                web_user_id=spo_30['studentRole']['id'],
                student_name=f"{students['lastName']} {students['firstName']} {students['middleName']}",
                group_name=students['groupName'],
                college_name=spo_30['settings']['organization']['abbreviation'],
                cookies=response.cookies
            )
        )

    async def get_dashboard_marks(self) -> list['Marks']:
        response = await HttpLoader().dashboard_marks(self.target)

        list_marks = []
        for subject in response.json['subjects']:
            list_marks.append(
                Marks(
                    subject=subject['name'],
                    marks=MarksInfo(markValues=[subject['mark']])
                )
            )

        return list_marks

    async def get_performance(self) -> list['Marks']:
        response = await HttpLoader().performance(self.target)

        list_marks = []
        for subject in response.json['daysWithMarksForSubject']:
            if subject['daysWithMarks']:
                list_marks.append(
                    Marks(
                        subject=subject['subjectName'],
                        marks=MarksInfo([MarksInfo(**mark) for mark in subject['daysWithMarks']]),
                    )
                )

        return list_marks

    async def get_debts_lesson(self) -> list['DebtLesson']:
        response = await HttpLoader().performance(self.target)

        date_lessons = []
        for dates in response.json['monthsWithDays']:
            date_lessons.extend(dates['daysWithLessons'])

        response = await HttpLoader().lessons_for_period(
            self.target,
            date_lessons[0].split('T')[0],
            date_lessons[-1].split('T')[0]
        )

        lessons = await get_debts(response)

        debt_lessons = []
        for debt in lessons:
            debt_lessons.append(
                DebtLesson(
                    subject=debt[0],
                    theme=debt[1],
                    marks=debt[2],
                    date=debt[3]
                )
            )

        return debt_lessons
