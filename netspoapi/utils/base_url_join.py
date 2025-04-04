from urllib.parse import urljoin


class BaseUrlJoiner:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def join(self, path: str):
        """Присоединение к основному URL пути"""
        return urljoin(self.base_url, path)
