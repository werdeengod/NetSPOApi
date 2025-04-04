import asyncio
from netspoapi import NetSPOApi


async def from_context():
    async with NetSPOApi() as api:
        await api.login('зверев27', 'd7f0e794')
        print(await api.dashboard_marks())


async def default():
    api2 = NetSPOApi()

    await api2.login('зверев27', 'd7f0e794')
    print(await api2.debts())


asyncio.run(default())

