from typing import Optional, TYPE_CHECKING, Union
from dataclasses import dataclass

from aiohttp import ClientSession
from netspoapi.utils import BaseUrlJoiner

if TYPE_CHECKING:
    from http.cookies import SimpleCookie


@dataclass(frozen=True)
class HttpRequesterData:
    json: dict
    cookies: 'SimpleCookie'


class BaseClient:
    def __init__(self):
        self._session: Optional[ClientSession] = None
        self.base_url = 'http://spo.cit73.ru'

    def get_session(self):
        if isinstance(self._session, ClientSession) and not self._session.closed:
            return self._session

        self._session = ClientSession()
        self._session.headers.add('Accept', 'application/json')
        self._session.headers.add('Content-Type', 'application/json')

        return self._session

    async def _make_request(self, url: str, method: str, **kwargs) -> 'HttpRequesterData':
        url = BaseUrlJoiner(self.base_url).join(url)
        session = self.get_session()

        async with session.request(method, url, **kwargs) as response:
            response_json = await response.json()
            cookies = response.cookies

        if self._validate_response(response_json) is False:
            raise

        return HttpRequesterData(
            json=response_json,
            cookies=cookies
        )

    @staticmethod
    def _validate_response(response: Union[dict, list]) -> bool:
        return False if isinstance(response, dict) and response.get('error') else True

    async def close(self):
        if not isinstance(self._session, ClientSession):
            return

        if self._session.closed:
            return

        await self._session.close()
