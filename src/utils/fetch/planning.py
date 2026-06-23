from dataclasses import dataclass
from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import RequestException

from gui.utils import get_domain, day_name_to_index


@dataclass
class Anime:
    title: str
    release_hour: int
    release_minute: int
    release_day: int
    lang: str
    image: str
    season: str
    url: str
    has_been_programmed: bool = False


def _parse_anime_card(card: Tag, day: str) -> Optional[Anime]:
    card_classes = card.get('class')

    if not card_classes or "Anime" not in card_classes:
        return None

    link_elem = card.find('a')
    url = link_elem.get('href') if isinstance(link_elem, Tag) else ""

    title_elem = card.find('h2', class_='card-title')
    name = title_elem.text.strip() if isinstance(title_elem, Tag) else "Unknown"

    img_elem = card.find('img', class_='card-image')
    image_url = img_elem.get('src') if isinstance(img_elem, Tag) else ""

    lang_elem = card.find('div', class_='language-badge-top')
    language = "Unknown"
    if isinstance(lang_elem, Tag):
        img_tag = lang_elem.find('img')
        if isinstance(img_tag, Tag):
            alt_text = img_tag.get('alt', 'Unknown')
            language = str(alt_text[0] if isinstance(alt_text, list) else alt_text)

    info_texts = card.find_all('span', class_='info-text')
    release_hour = "Unknown"
    season = "N/A"

    if len(info_texts) > 0:
        release_hour = info_texts[0].text.strip()
    if len(info_texts) > 1:
        season = info_texts[1].text.strip()

    hour_minute: list[str] = release_hour.split('h')
    try:
        release_hour = int(hour_minute[0])
        release_minute = int(hour_minute[1]) if len(hour_minute) > 1 else 0
    except ValueError:
        release_hour = 12
        release_minute = 0

    return Anime(
        name,
        release_hour,
        release_minute,
        day_name_to_index(day),
        language,
        str(image_url),
        season,
        str(url)
    )


def fetch_planning(headers: Optional[Dict[str, str]] = None) -> Optional[Dict[str, List[Anime]]]:
    url = f"https://{get_domain()}/planning"

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except RequestException as _:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    planning_schedule: Dict[str, List[Anime]] = {}

    days = soup.find_all('div', class_='selectedRow')

    for day in days:
        if not isinstance(day, Tag):
            continue

        day_header = day.find('h2', class_='titreJours')
        if not isinstance(day_header, Tag):
            continue

        day_name = day_header.text.strip()

        planning_schedule[day_name] = []

        cards = day.find_all('div', class_='planning-card')

        for card in cards:
            if not isinstance(card, Tag):
                continue

            parsed_anime = _parse_anime_card(card, day_name)
            if parsed_anime:
                planning_schedule[day_name].append(parsed_anime)

    return planning_schedule
