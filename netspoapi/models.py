from typing import Union, Optional
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


class Lesson(BaseModel):
    id: int
    name: str
    teacher: str
    cabinet: str
    start_time: str
    end_time: str
    themes: Optional[list[str]]
    tasks: Optional[list[str]]


class Timetable(BaseModel):
    lessons: list['Lesson']
    date: 'datetime.datetime'


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


class AttestationSemesterMark(BaseModel):
    course_number: int
    semester_number: int
    mark: Union[str, None]


class Attestation(BaseModel):
    subject_name: str
    final_mark: Union[str, None]
    semester_marks: list['AttestationSemesterMark']



