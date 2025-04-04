from datetime import datetime
import hashlib
import base64


def split_date_from_string(date: str) -> datetime:
    """Конвертер строки в datetime

    Args:
        date: Строка

    Return:
        Формат datetime

    """
    date_string = date.split('T')[0]
    return datetime.strptime(date_string, "%Y-%m-%d")


def get_legit_type_tasks() -> list:
    """Список верных форматов

    Return:
        Список форматов, по которым могут поставить не зачет
    """
    legit_type = [
        'Control',
        'Test',
        'PracticalWork',
        'Laboratory',
        'Home',
        'Independent',
        'Slice',
        'Lesson',
        'Self'
    ]
    return legit_type


def password_hash(password: str) -> str:
    """Хеширование пароля для входа в аккаунт

    Args:
        password: Обычный пароль пользователя

    Return:
        Захешированный пароль

    """
    sha256 = hashlib.sha256(password.encode('utf-8')).digest()
    password = base64.b64encode(sha256).decode()

    return password
