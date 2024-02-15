import aiohttp

from .structures import HttpRequesterFields, HttpRequesterMethod, HttpRequesterData


class HttpRequester:
    def __init__(self):
        self._session = aiohttp.ClientSession()

        self._session.headers.add(
            'Accept', 'application/json'
        )
        self._session.headers.add(
            'Content-Type', 'application/json'
        )

    async def __call__(
            self,
            *,
            url: str,
            method: HttpRequesterMethod,
            **kwargs: HttpRequesterFields
    ) -> HttpRequesterData:

        response = await self._session.request(
            method=method.name, url=url, **kwargs
        )

        return HttpRequesterData(
            json=await response.json(),
            cookies=response.cookies
        )
