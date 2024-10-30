import httpx
from geopy.distance import great_circle


def calculate_distance(lat1, lon1, lat2, lon2) -> float:
    """Вычисляет расстояние в километрах между двумя точками на земном шаре."""
    return great_circle((lat1, lon1), (lat2, lon2)).km


async def get_location(client_ip: str) -> tuple:
    """
    Функция получает широту и долготу по ip, если запрос неудачен,
    возвращает пустой кортеж
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://ip-api.com/json/{client_ip}")
        if response.status_code == 200:
            data = response.json()
            latitude = data.get("lat")
            longitude = data.get("lon")
            return latitude, longitude
        return None, None


def my_key_builder(func, *args, **kwargs):
    """Создаем динамический ключ на основе имени функции и её аргументов"""
    key_parts = (
        [func.__module__, func.__name__]
        + list(args)
        + [f"{k}={v}" for k, v in kwargs.items()]
    )
    return ":".join(map(str, key_parts))
