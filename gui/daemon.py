import asyncio
from datetime import datetime
from urllib.parse import urljoin

from gui.error import DownloadError, FetchError
from gui.logger import app_logger
from gui.storage.anime_data import app_datas
from gui.utils import get_domain
from utils.download.download_gui import download_episodes_from_url


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
