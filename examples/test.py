import datetime
from netspoapi import NetSPOApi


async def from_context():
    url = 'https://spo.cit73.ru'

    async with NetSPOApi('зверев27', '11111', base_url=url) as api:
        print(await api.student_client.attestation(course_number=3, semester=1))


async def default():
    url = 'https://spo.cit73.ru'

    api = await NetSPOApi('зверев27', '11111', base_url=url).login()
    print(await api.student_client.lessons(
        begin=datetime.date(2025, 1, 1),
        end=datetime.date(2025, 4, 13)
    ))

