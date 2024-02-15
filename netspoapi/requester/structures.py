from typing import TypedDict, TYPE_CHECKING
from enum import Enum
from dataclasses import dataclass

if TYPE_CHECKING:
    from http.cookies import SimpleCookie
    from json.encoder import JSONEncoder


@dataclass(frozen=True)
class HttpRequesterData:
    json: dict
    cookies: 'SimpleCookie'


class HttpRequesterFields(TypedDict, total=False):
    data: 'JSONEncoder'
    cookies: 'SimpleCookie'


class HttpRequesterMethod(Enum):
    post = 1
    get = 2
    put = 3
