from netspoapi.loader import HttpLoader
from netspoapi.schemas import TargetLogin, Marks, DebtLesson, MarksInfo
from netspoapi.utils import split_date_from_string, get_legit_type_tasks


class NetSPOApi:
    def __init__(self, target: 'TargetLogin'):
        self.target = target

    @classmethod
    async def login(cls, login: str, password: str) -> 'NetSPOApi':
        response = await HttpLoader().login(login, password)

        spo_30 = response.json['tenants']['spo_30']
        organization = spo_30['settings']['organization']['abbreviation']

        students = spo_30['studentRole']['students'][0]

        student_name_keys = ('lastName', 'firstName', 'middleName')
        student_name = " ".join(
            [students[key] for key in student_name_keys]
        )

        return cls(
            TargetLogin(
                web_user_id=students['id'],
                student_name=student_name.strip(),
                group_name=students['groupName'],
                college_name=organization,
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
                        marks=[MarksInfo(**mark) for mark in subject['daysWithMarks']],
                    )
                )

        return list_marks

    async def get_debts_lesson(self) -> list['DebtLesson']:
        response = await HttpLoader().performance(self.target)

        date_lessons = []
        for dates in response.json['monthsWithDays']:
            date_lessons.extend(dates['daysWithLessons'])

        begin, end = (
            split_date_from_string(date_lessons[0]),
            split_date_from_string(date_lessons[-1])
        )

        response = await HttpLoader().lessons_for_period(
            self.target, str(begin.date()), str(end.date())
        )

        list_debt_lessons = []

        for days in response.json:
            for lesson in days['lessons']:

                if not (lesson.get('name') and lesson.get('gradebook')):
                    continue

                if not lesson['gradebook'].get('tasks'):
                    continue

                legit_type = get_legit_type_tasks()

                type_lesson = lesson['gradebook']['lessonType']
                tasks_lesson = lesson['gradebook']['tasks']

                for task_lesson in tasks_lesson:
                    type_task = task_lesson['type']
                    is_debt, marks = False, []

                    if task_lesson['isRequired'] is True:
                        if not task_lesson.get('mark') and (type_task in legit_type or type_lesson in legit_type):
                            marks.append('Точка')
                            is_debt = True

                        elif task_lesson.get('mark') and task_lesson['mark'] == 'Two':
                            marks.append('2')
                            is_debt = True

                    if is_debt:
                        list_debt_lessons.append(
                            DebtLesson(
                                subject=lesson['name'],
                                theme=lesson['gradebook']['themes'][0],
                                marks=MarksInfo(
                                    markValues=marks,
                                    day=split_date_from_string(days['date'])
                                )
                            )
                        )

        return list_debt_lessons

    async def get_attestation(self):
        pass
