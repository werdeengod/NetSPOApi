# NetSPOApi

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Библиотека для работы с сетевым городом от АО "ИРТех"

### Вход через контекст
```python
from netspoapi import NetSPOApi

async def main():
    url = 'https://spo.cit73.ru'

    async with NetSPOApi('login', 'password', base_url=url) as api:
        data = await api.student_client.dashboard()
        print(data)
```

### Обычный вход
```python
from netspoapi import NetSPOApi

async def main():
    url = 'https://spo.cit73.ru'

    api = await NetSPOApi('зверев27', '11111', base_url=url).login()
    data = await api.student_client.dashboard()
    print(data)
```