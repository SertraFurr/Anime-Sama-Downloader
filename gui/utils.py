from datetime import datetime, timedelta

from gui.config import settings


DAY_INDEX = {
    "Lundi": 0, "Mardi": 1, "Mercredi": 2,
    "Jeudi": 3, "Vendredi": 4, "Samedi": 5, "Dimanche": 6
}

SOURCE_CONFIG = [
    "vidmoly.net",
    "vidmoly.to",
    "video.sibnet.ru",
    "sendvid.com",
    "embed4me.com",
    "movearnpre.com",
    "smoothpre.com",
    "mivalyo.com",
    "dingtezuni.com",
]


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


def is_from_unknown_source(url: str) -> bool:
    for source in SOURCE_CONFIG:
        if source.lower() in url:
            return False
    return True


def order_episodes_sources(sources: list[str]) -> list[str]:
    config_ranks = {config: index for index, config in enumerate(SOURCE_CONFIG)}

    linked_sources = {}
    for source in sources:
        for config_source in SOURCE_CONFIG:
            if config_source in source and not is_from_unknown_source(source):
                linked_sources[source] = config_source
                break
    print(sources)
    sorted_sources = sorted(
        linked_sources.keys(),
        key=lambda x: config_ranks[linked_sources[x]]
    )
    print(sorted_sources)

    return sorted_sources
