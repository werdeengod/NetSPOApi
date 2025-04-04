from typing import Optional
from aiohttp import ClientSession

from netspoapi.exceptions import APIErrorFactory
from netspoapi.utils import BaseUrlJoiner


class BaseClient:
    def __init__(self, user_agent: str | None):
        self._user_agent = user_agent
        self._session: Optional[ClientSession] = None
        self.base_url = 'http://spo.cit73.ru'

    def _get_session(self) -> 'ClientSession':
        if isinstance(self._session, ClientSession) and not self._session.closed:
            return self._session

        self._session = ClientSession()

        if self._user_agent:
            self._session.headers.add('User-Agent', self._user_agent)

        self._session.headers.add('Accept', 'application/json')
        self._session.headers.add('Content-Type', 'application/json')

        return self._session

    async def make_request(self, url: str, method: str, **kwargs) -> dict:
        url = BaseUrlJoiner(self.base_url).join(url)
        session = self._get_session()

        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    raise APIErrorFactory(response.status, response.reason)

                response = await response.json()

        except Exception as e:
            raise APIErrorFactory(name=e)

        return response

    async def close(self) -> None:
        if not isinstance(self._session, ClientSession):
            return

        if self._session.closed:
            return

        await self._session.close()
