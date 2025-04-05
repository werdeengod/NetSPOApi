from typing import Optional, Union
from aiohttp import ClientSession

from netspoapi.exceptions import APIErrorFactory
from netspoapi.utils import BaseUrlJoiner


class BaseClient:
    def __init__(self, user_agent: Union[str, None], base_url: Union[str, None]):
        self._user_agent = user_agent
        self._session: Optional[ClientSession] = None
        self.base_url = base_url

    def _get_session(self) -> 'ClientSession':
        """Создание единой сессии для request запросов"""
        if isinstance(self._session, ClientSession) and not self._session.closed:
            return self._session

        self._session = ClientSession()

        if self._user_agent:
            self._session.headers.add('User-Agent', self._user_agent)

        self._session.headers.add('Accept', 'application/json')
        self._session.headers.add('Content-Type', 'application/json')

        return self._session

    async def make_request(self, url: str, method: str, **kwargs) -> dict:
        """Создание request запроса"""
        url = BaseUrlJoiner(self.base_url).join(url)
        session = self._get_session()

        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    raise APIErrorFactory(response.status, response.reason)

                response = await response.json()

        except Exception as e:
            raise APIErrorFactory(400, e)

        return response

    async def close(self) -> None:
        """Закрытие единой сессии"""
        if not isinstance(self._session, ClientSession):
            return

        if self._session.closed:
            return

        await self._session.close()
