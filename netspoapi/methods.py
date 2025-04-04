from typing import TYPE_CHECKING
from functools import wraps

from netspoapi.exceptions import APIErrorFactory

if TYPE_CHECKING:
    from netspoapi import NetSPOApi


def student_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self: 'NetSPOApi' = args[0]

        if not self.student:
            raise APIErrorFactory(403, 'Forbidden. You auth like teacher')

        return func(*args, **kwargs)

    return wrapper


def teacher_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self: 'NetSPOApi' = args[0]

        if not self.teacher:
            raise APIErrorFactory(403, 'Forbidden. You auth like student')

        return func(*args, **kwargs)

    return wrapper
