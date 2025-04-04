from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from netspoapi import NetSPOApi
    from netspoapi.models import TeacherData


class TeacherClient:
    def __init__(self, api: 'NetSPOApi', teacher_data: 'TeacherData'):
        self._api = api
        self.teacher_data = teacher_data
