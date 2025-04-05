import asyncio
import datetime

from netspoapi import NetSPOApi


async def from_context():
    url = 'http://spo.cit73.ru'

    async with NetSPOApi('зверев27', 'd7f0e794', base_url=url) as api:
        print(datetime.datetime.now())
        print(await api.student_client.attestation(course_number=3, semester=1))
        print(datetime.datetime.now())


async def default():
    url = 'http://spo.cit73.ru'

    api = await NetSPOApi('зверев27', 'd7f0e794', base_url=url).login()

    print(datetime.datetime.now())
    print(await api.student_client.lessons(begin=datetime.date(2025, 1, 1), end=datetime.date(2025, 4, 13)))
    print(datetime.datetime.now())


asyncio.run(from_context())

