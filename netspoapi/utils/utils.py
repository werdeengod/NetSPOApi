from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from netspoapi.requester import HttpRequesterData


def split_date_from_string(date: str) -> datetime:
    date_string = date.split('T')[0]
    return datetime.strptime(date_string, "%Y-%m-%d")


def get_legit_type_tasks() -> list:
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
    return legit_type