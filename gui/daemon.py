import asyncio

from datetime import datetime, timedelta
from urllib.parse import urljoin

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from gui.cached import get_cached_planning
from gui.error import DownloadError, FetchError
from gui.logger import app_logger
from gui.storage.anime_data import app_datas, AnimeData
from gui.utils import get_domain
from utils.download.download_gui import download_episodes_from_url
from utils.fetch.planning import Anime


async def run_single_check():
    now = datetime.now()
    pending_animes = app_datas.get_pending_scheduled_animes(current_time=now)

    if not pending_animes:
        app_logger.info("Aucun anime trouvé à télécharger.")
        return

    for anime in pending_animes:
        catch_up = True

        while catch_up:
            app_logger.info(
                f"Le moment est venu pour {anime.title} ({anime.season} E{anime.week_episode}) ! Lancement du téléchargement...")

            try:
                anime_path = urljoin(f"https://{get_domain()}", anime.anime_url)
                await asyncio.to_thread(
                    download_episodes_from_url,
                    season_url=anime_path,
                    episode_to_download={anime.week_episode},
                    download_all=False,
                    use_threading=True,
                    automatic_mp4=True
                )

                app_datas.mark_as_downloaded(anime.title, anime.season, anime.lang)
                app_datas.save()
                app_logger.info(
                    f"Téléchargement automatique terminé pour {anime.title} (E{anime.week_episode - 1}).")

            except FetchError:
                app_logger.warning(
                    f"Épisode {anime.week_episode} de {anime.title} non disponible. Nouvelle tentative plus tard.")
                catch_up = False
            except DownloadError as e:
                app_logger.warning(
                    f"Téléchargement de l'épisode {anime.week_episode} de {anime.title} échoué : {e}. Nouvelle tentative plus tard.")
                catch_up = False


async def check_and_download_scheduled():
    app_logger.info("Daemon de téléchargement démarré. En attente de tâches...")

    while True:
        try:
            await run_single_check()
        except Exception as e:
            app_logger.error(f"Erreur globale dans le daemon de vérification : {str(e)}")

        await asyncio.sleep(900)


async def verify_planning_integrity():
    app_logger.info("Début de la vérification hebdomadaire du planning...")

    planning = get_cached_planning()
    if not planning:
        app_logger.error("Erreur en récupérant le planning.")
        return

    planning_animes = {AnimeData.construct_anime_key(anime.title, anime.season, anime.lang): anime
                       for animes in planning.values()
                       for anime in animes
                       }
    await _verify_finished_anime(planning_animes)

    app_datas.save()

    await _verify_release_day(planning_animes)

    app_datas.save()

    await _verify_finished_anime_age()

    app_datas.save()

    app_logger.info("Fin de vérification du planning.")


async def _verify_finished_anime_age():
    now = datetime.now()
    to_delete = []
    for title, anime in app_datas.finished_animes.items():
        if anime.last_download_date < now - timedelta(days=8):
            anime_key = AnimeData.construct_anime_key_from_object(anime)
            to_delete.append(anime_key)
    for anime_key in to_delete:
        app_datas.finished_animes.pop(anime_key)


async def _verify_release_day(planning_animes: dict[str, Anime]):
    for anime in app_datas.anime_of_week:
        anime_key = AnimeData.construct_anime_key(anime.title, anime.season, anime.lang)
        planning_anime = planning_animes[anime_key]
        if planning_anime.release_day != anime.release_day:
            app_datas.switch_anime_day(anime.title, anime.season, anime.lang, anime.release_day,
                                       planning_anime.release_day)


async def _verify_finished_anime(planning_animes: dict[str, Anime]):
    for anime in app_datas.anime_of_week:
        if AnimeData.construct_anime_key_from_object(anime) not in planning_animes:
            app_datas.finish_anime(anime.title, anime.season, anime.lang, anime.release_day)


scheduler = AsyncIOScheduler()

scheduler.add_job(
    verify_planning_integrity,
    CronTrigger(day_of_week='mon', hour=20, minute=0)
)

scheduler.add_job(verify_planning_integrity)
