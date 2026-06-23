import atexit
from datetime import datetime, timedelta

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
    registered_animes: list[dict[str, RegisteredAnime]]
    finished_animes: dict[str, RegisteredAnime]

    def add_new_anime(self, anime_url: str, image: str, title: str, lang: str, season: str, week_episode: int,
                      release_date: datetime):
        weekday: int = release_date.weekday()
        unique_key = self.construct_anime_key(title, season, lang)

        anime = RegisteredAnime(
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
        )

        self.registered_animes[weekday][unique_key] = anime
        self.registered_animes_keys.add(unique_key)

    def has_been_registered(self, title: str, season: str, lang: str) -> bool:
        unique_key = self.construct_anime_key(title, season, lang)
        return unique_key in self.registered_animes_keys

    def animes_from_day(self, day: int) -> list[RegisteredAnime]:
        return list(self.registered_animes[day].values())

    def save(self):
        with open(animes_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))

    def unregister_anime(self, title: str, season: str, lang: str):
        unique_key = self.construct_anime_key(title, season, lang)
        if unique_key not in self.registered_animes_keys:
            raise ValueError(f"Anime {unique_key} is not registered")

        self.registered_animes_keys.remove(unique_key)

        for day_dict in self.registered_animes:
            day_dict.pop(unique_key, None)

    def finish_anime(self, title: str, season: str, lang: str, day: int):
        unique_key = self.construct_anime_key(title, season, lang)
        if unique_key not in self.registered_animes_keys:
            raise ValueError(f"Anime {unique_key} is not registered")

        anime = self.registered_animes[day].pop(unique_key, None)

        if anime:
            anime_key = self.construct_anime_key_from_object(anime)
            self.finished_animes[anime_key] = anime
            self.unregister_anime(title, season, lang)
            self.save()

    def switch_anime_day(self, title: str, season: str, lang: str, old_day: int, new_day: int):
        unique_key = self.construct_anime_key(title, season, lang)
        if unique_key not in self.registered_animes_keys:
            raise ValueError(f"Anime {unique_key} is not registered")

        anime = self.registered_animes[old_day].pop(unique_key, None)
        if anime:
            anime.release_day = new_day
            self.registered_animes[new_day][unique_key] = anime

    def get_pending_scheduled_animes(self, current_time: datetime) -> list[RegisteredAnime]:
        pending_animes = []

        for day_dict in self.registered_animes:
            for anime in day_dict.values():
                days_since_release = (current_time.weekday() - anime.release_day) % 7

                last_theoretical_release = current_time - timedelta(days=days_since_release)
                last_theoretical_release = last_theoretical_release.replace(
                    hour=anime.release_hour,
                    minute=anime.release_min,
                    second=0,
                    microsecond=0
                )

                if last_theoretical_release > current_time:
                    last_theoretical_release -= timedelta(days=7)

                if anime.last_download_date < last_theoretical_release:
                    pending_animes.append(anime)

        return pending_animes

    def mark_as_downloaded(self, title: str, season: str, lang: str):
        unique_key = self.construct_anime_key(title, season, lang)
        if unique_key not in self.registered_animes_keys:
            return

        for day_dict in self.registered_animes:
            if unique_key in day_dict:
                anime = day_dict[unique_key]
                anime.last_download_date = datetime.now()
                anime.downloaded_episodes.add(anime.week_episode)
                anime.week_episode += 1

                self.save()
                return

    @property
    def anime_of_week(self) -> list[RegisteredAnime]:
        animes_of_week = []
        for day_dict in self.registered_animes:
            for anime in day_dict.values():
                animes_of_week.append(anime)
        return animes_of_week

    @staticmethod
    def construct_anime_key_from_object(anime: RegisteredAnime) -> str:
        return f"{anime.title}-{anime.season}-{anime.lang}"

    @staticmethod
    def construct_anime_key(title: str, season: str, lang: str) -> str:
        return f"{title}-{season}-{lang}"


def _load_animes(path: str) -> AnimeData:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return AnimeData.model_validate_json(f.read())
    except FileNotFoundError:
        return AnimeData(
            registered_animes_keys=set(),
            registered_animes=[{} for _ in range(7)],
            finished_animes={}
        )


animes_path = "anime_data.json"
app_datas: AnimeData = _load_animes(animes_path)

atexit.register(app_datas.save)
