import json

from netspoapi.exceptions import APIErrorFactory
from netspoapi.client import BaseClient, StudentClient, TeacherClient
from netspoapi.models import StudentData, TeacherData
from netspoapi.utils import password_hash, get_fullname_client


class NetSPOApi(BaseClient):
    def __init__(self, login: str, password: str, *, base_url: str, user_agent: str = None):
        super().__init__(user_agent=user_agent, base_url=base_url)

        self._login = login
        self._password = password_hash(password)

        self._student_client = None
        self._teacher_client = None

    async def __aenter__(self) -> 'NetSPOApi':
        return await self.login()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    @property
    def student_client(self) -> 'StudentClient':
        """Методы для работы с API студента"""

        if not self._student_client:
            raise APIErrorFactory(403, 'Forbidden')

        return self._student_client

    @property
    def teacher_client(self) -> 'TeacherClient':
        """Методы для работы с API учителя"""

        if not self._teacher_client:
            raise APIErrorFactory(403, 'Forbidden')

        return self._teacher_client

    async def login(self) -> 'NetSPOApi':
        """Вход в учетную запись сетевого города

        Return:
            Объект NetSPOApi
        """
        data = {"login": self._login, "password": self._password}

        response = await self.make_request(
            url='/services/security/login',
            method="post",
            data=json.dumps(data)
        )

        organization = response['tenants']['spo_30']['settings']['organization']['abbreviation']

        if response['tenants']['spo_30'].get('studentRole'):
            students = response['tenants']['spo_30']['studentRole']['students'][0]
            student_name = get_fullname_client(students)

            self._student_client = StudentClient(
                api=self,
                student_data=StudentData(
                    student_id=students['id'],
                    student_name=student_name.strip(),
                    group_name=students['groupName'],
                    college_name=organization
                )
            )

        return self
