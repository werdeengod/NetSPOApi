from typing import TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    import datetime


@dataclass
class TargetLogin:
    web_user_id: int
    student_name: str
    group_name: str
    college_name: str
    cookies: str


@dataclass
class Marks:
    subject: str
    marks: list['MarksInfo']


@dataclass
class MarksInfo:
    markValues: list[str]
    day: 'datetime.datetime' = None
    absenceType: str | None = None


@dataclass
class DebtLesson:
    subject: str
    theme: str
    marks: 'MarksInfo'



