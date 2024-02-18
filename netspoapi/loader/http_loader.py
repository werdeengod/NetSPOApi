import hashlib
import base64
import json

from netspoapi.requester import HttpRequester, HttpRequesterMethod, HttpRequesterData
from netspoapi.utils import BaseUrlJoiner
from netspoapi.schemas import TargetLogin

from .errors import AuthenticationError


class HttpLoader:
    def __init__(self):
        self._requester = HttpRequester()
        self.base_url = 'http://spo.cit73.ru'

    async def login(self, login: str, password: str) -> HttpRequesterData:
        sha256 = hashlib.sha256(password.encode('utf-8')).digest()
        password = base64.b64encode(sha256).decode()

        data = {
            "login": login, "password": password
        }

        response = await self._requester(
            url=BaseUrlJoiner(self.base_url).join(
                '/services/security/login'
            ),
            method=HttpRequesterMethod.post,
            data=json.dumps(data)
        )

        if response.json.get('responseStatus'):
            raise AuthenticationError("[Error] Invalid username or password.")

        return response

    async def dashboard_marks(self, target: TargetLogin) -> HttpRequesterData:
        response = await self._requester(
            url=BaseUrlJoiner(self.base_url).join(
                f'/services/students/{target.web_user_id}/dashboard'
            ),
            method=HttpRequesterMethod.get,
            cookies=target.cookies
        )

        return response

    async def performance(self, target: TargetLogin) -> HttpRequesterData:
        response = await self._requester(
            url=BaseUrlJoiner(self.base_url).join(
                f'/services/reports/current/performance/{target.web_user_id}'
            ),
            method=HttpRequesterMethod.get,
            cookies=target.cookies
        )

        return response

    async def lessons_for_period(self, target: TargetLogin, begin: str, end: str) -> HttpRequesterData:
        response = await self._requester(
            url=BaseUrlJoiner(self.base_url).join(
                f'/services/students/{target.web_user_id}/lessons/{begin}/{end}'
            ),
            method=HttpRequesterMethod.get,
            cookies=target.cookies
        )

        return response

    async def attestation(self, target: TargetLogin) -> HttpRequesterData:
        response = await self._requester(
            url=BaseUrlJoiner(self.base_url).join(
                f'services/students/{target.web_user_id}/attestation'
            ),
            method=HttpRequesterMethod.get,
            cookies=target.cookies
        )
        return response

