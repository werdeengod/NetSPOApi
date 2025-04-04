from typing import Union
from pydantic import BaseModel
import datetime


class StudentData(BaseModel):
    student_id: int
    student_name: str
    group_name: str
    college_name: str


class TeacherData(BaseModel):
    teacher_id: int
    teacher_name: str
    college_name: str


class MarksInfo(BaseModel):
    markValues: list[str] | str
    day: 'datetime.datetime' = None
    absenceType: str | None = None


class Marks(BaseModel):
    subject: str
    marks: Union[list['MarksInfo'], float, int]


class DebtLesson(BaseModel):
    subject: str
    theme: str
    marks: 'MarksInfo'



