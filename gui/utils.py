from datetime import datetime, timedelta

from gui.config import settings


DAY_INDEX = {
    "Lundi": 0, "Mardi": 1, "Mercredi": 2,
    "Jeudi": 3, "Vendredi": 4, "Samedi": 5, "Dimanche": 6
}


def get_domain() -> str:
    return settings.domain


def get_anime_catalog_url(catalog_url: str) -> str:
    return f"https://{get_domain()}{catalog_url}"


def create_datetime_from_day(day: str | int, hour: int, minute: int):
    if isinstance(day, str):
        target_index = day_name_to_index(day)
    else:
        target_index = day

    now = datetime.now()
    current_index = now.weekday()

    days_to_target = target_index - current_index

    target_date = now + timedelta(days=days_to_target)

    return target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def day_name_to_index(day_capitalized: str) -> int:
    return DAY_INDEX[day_capitalized.capitalize()]


def get_last_episode_released(episodes: dict[str, list[str]]) -> int:
    return max(len(episodes[season]) for season in episodes)


def normalize_catalog_url(url: str) -> str:
    splitted_url: list[str] = url.split("/")
    i = len(splitted_url) - 1
    while i >= 0 and splitted_url[i-1] != "catalogue":
        i -= 1

    catalog_url = "/".join(splitted_url[:i+1])

    if not catalog_url.startswith(f"https://{get_domain()}"):
        return get_anime_catalog_url(catalog_url)
    return catalog_url
