import atexit

from datetime import datetime

from pydantic import BaseModel


class RegisteredAnime(BaseModel):
    anime_url: str
    image: str
    title: str
    lang: str
    season: str
    week_episode: int
    release_day: int
    release_hour: int
    release_min: int
    downloaded_episodes: set[int]
    last_download_date: datetime


class AnimeData(BaseModel):
    registered_animes_keys: set[str]
    registered_animes: list[list[RegisteredAnime]]

    def add_new_anime(self, anime_url: str, image: str, title: str, lang: str, season: str, week_episode: int,
                      release_date: datetime):
        weekday: int = release_date.weekday()

        self.registered_animes[weekday].append(RegisteredAnime(
            anime_url=anime_url,
            image=image,
            title=title,
            lang=lang,
            season=season,
            week_episode=week_episode,
            release_day=weekday,
            release_hour=release_date.hour,
            release_min=release_date.minute,
            downloaded_episodes=set(),
            last_download_date=datetime.now()
        ))

        unique_key = f"{title}-{season}-{lang}"
        self.registered_animes_keys.add(unique_key)

    def has_been_registered(self, title: str, season: str, lang: str) -> bool:
        unique_key = f"{title}-{season}-{lang}"
        return unique_key in self.registered_animes_keys

    def animes_from_day(self, day: int) -> list[RegisteredAnime]:
        return self.registered_animes[day]

    def save(self, _, __, ___):
        with open(animes_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    def remove_anime(self, title: str, season: str, lang: str):
        if not self.has_been_registered(title, season, lang):
            raise ValueError(f"Anime {title} - {season} - {lang} is not registered")
        unique_key = f"{title}-{season}-{lang}"
        self.registered_animes_keys.remove(unique_key)

        for weekday, animes in enumerate(self.registered_animes):
            self.registered_animes[weekday] = [
                anime for anime in animes
                if anime.title != title or anime.season != season or anime.lang != lang
            ]


def _load_animes(path: str) -> AnimeData:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return AnimeData.model_validate_json(f.read())
    except FileNotFoundError:
        return AnimeData(
            registered_animes_keys=set(),
            registered_animes=[[] for _ in range(7)]
        )


animes_path = "anime_data.json"
app_datas: AnimeData = _load_animes(animes_path)

atexit.register(app_datas.save, None, None, None)
