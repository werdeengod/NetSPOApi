from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netspoapi.requester import HttpRequesterData


async def get_debts(response: 'HttpRequesterData') -> list:
    # TODO: выглядит пиздец.

    list_debt_lessons = []

    for days in response.json:
        for lesson in days['lessons']:
            if lesson.get('name') and lesson.get('gradebook'):
                if lesson['gradebook'].get('tasks') and lesson['gradebook']['tasks']:
                    legit_type = [
                        'Control',
                        'Test',
                        'PracticalWork',
                        'Laboratory',
                        'Home',
                        'Independent',
                        'Slice',
                        'Lesson',
                        'Self'
                    ]
                    type_lesson = lesson['gradebook']['lessonType']

                    tasks_lesson = lesson['gradebook']['tasks']
                    for task_lesson in tasks_lesson:
                        type_task = task_lesson['type']

                        is_debt, mark = False, ''
                        if task_lesson['isRequired'] is True:
                            if not task_lesson.get('mark') and type_task in legit_type:
                                is_debt = True
                                mark = 'Точка'

                            elif not task_lesson.get('mark') and type_lesson in legit_type:
                                is_debt = True
                                mark = 'Точка'

                            elif task_lesson.get('mark') and task_lesson['mark'] == 'Two':
                                is_debt = True
                                mark = '2'

                        if is_debt:
                            list_debt_lessons.append(
                                [
                                    lesson['name'],
                                    lesson['gradebook']['themes'][0],
                                    [mark],
                                    days['date'].split('T')[0]
                                ]
                            )

    return list_debt_lessons
