from dataclasses import dataclass
from typing import Optional, Dict, List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests import RequestException


@dataclass
class AnimeDetails:
    title: str
    alt_titles: str
    image_url: str
    trailer_url: str
    status: str
    year: str
    episodes: str
    chapters: str
    creator: str
    studio: str
    synopsis: str
    genres: List[str]


def fetch_anime_details(url: str, headers: Optional[Dict[str, str]] = None) -> Optional[AnimeDetails]:
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except RequestException:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    meta_img = soup.find('meta', property='og:image')
    image_url = meta_img.get('content') if isinstance(meta_img, Tag) else ""

    title_elem = soup.find('h1')
    title = title_elem.text.strip() if isinstance(title_elem, Tag) else "Unknown"

    alt_titles_elem = soup.find('h2', id='titreAlter')
    alt_titles = alt_titles_elem.text.strip() if isinstance(alt_titles_elem, Tag) else ""

    trailer_elem = soup.find('iframe', id='bandeannonce')
    trailer_url = trailer_elem.get('src') if isinstance(trailer_elem, Tag) else ""

    synopsis_elem = soup.find('p', id='synopsisText')
    synopsis = synopsis_elem.text.strip() if isinstance(synopsis_elem, Tag) else ""

    genres = []
    genres_wrap = soup.find('div', class_='genres-wrap')
    if isinstance(genres_wrap, Tag):
        pill_elems = genres_wrap.find_all('span', class_='genre-pill')
        genres = [pill.text.strip() for pill in pill_elems if isinstance(pill, Tag)]

    status, year, episodes, chapters, creator, studio = "", "", "", "", "", ""
    info_grid = soup.find('div', class_='info-grid')

    if isinstance(info_grid, Tag):
        labels = info_grid.find_all('span', class_='info-lbl')

        for lbl in labels:
            if not isinstance(lbl, Tag):
                continue

            lbl_text = lbl.text.strip().lower()

            val_elem = lbl.find_next_sibling(class_='info-val')
            if not isinstance(val_elem, Tag):
                continue

            val_text = val_elem.text.replace('Voir plus', '').replace('Voir moins', '').strip()

            if "état" in lbl_text:
                status = val_text
            elif "année" in lbl_text:
                year = val_text
            elif "épisodes" in lbl_text:
                episodes = val_text
            elif "chapitres" in lbl_text:
                chapters = val_text
            elif "créateur" in lbl_text:
                creator = val_text
            elif "studio" in lbl_text:
                studio_span = val_elem.find('span', id='studioText')
                studio = studio_span.text.strip() if isinstance(studio_span, Tag) else val_text

    return AnimeDetails(
        title=title,
        alt_titles=alt_titles,
        image_url=image_url,
        trailer_url=trailer_url,
        status=status,
        year=year,
        episodes=episodes,
        chapters=chapters,
        creator=creator,
        studio=studio,
        synopsis=synopsis,
        genres=genres
    )
