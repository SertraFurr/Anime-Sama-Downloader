import asyncio
import html
import json
from datetime import datetime
from typing import Iterable

from fastapi import APIRouter, Query, Form, BackgroundTasks
from starlette.requests import Request
from starlette.responses import HTMLResponse, StreamingResponse

from gui.cloudflare import get_headers
from gui.error import DownloadError
from gui.logger import log_clients, log_history, app_logger
from gui.routers.web import templates, get_cached_planning
from gui.storage.anime_data import app_datas
from gui.utils import create_datetime_from_day, get_last_episode_released, get_anime_catalog_url
from utils.download.download_gui import download_season_from_url
from utils.fetch.fetch_episodes import fetch_episodes
from utils.fetch.planning import Anime
from utils.search.search_bar import search_anime_query

router = APIRouter(tags=["Backend / Download API"])


async def log_generator(request: Request):
    for historical_msg in list(log_history):
        yield historical_msg
        await asyncio.sleep(0.01)

    client_queue = asyncio.Queue()
    log_clients.add(client_queue)

    try:
        while True:
            if await request.is_disconnected():
                break

            log_message = await client_queue.get()
            yield log_message
    finally:
        log_clients.remove(client_queue)


def run_download_task(season_url: str, anime_name: str, episodes: Iterable[int], full_season: bool):
    try:
        download_season_from_url(season_url, episodes, full_season, True, True)
    except DownloadError as e:
        app_logger.error(f"Erreur de téléchargement pour {anime_name} : {str(e)}")
    except Exception as e:
         app_logger.error(f"Erreur inattendue pour {anime_name} : {str(e)}")
    else:
        app_logger.info(f"Téléchargement de {anime_name} terminé avec succès !")


@router.get("/stream-logs")
async def stream_logs(request: Request):
    return StreamingResponse(log_generator(request), media_type="text/event-stream")


@router.get("/search", response_class=HTMLResponse)
async def search_anime(q: str = Query("")):
    if not q or len(q.strip()) < 2:
        return ""

    results = search_anime_query(q, headers=get_headers())

    if not results:
        return "<div style='padding: 1rem; text-align: center; color: #94a3b8;'>Aucun résultat trouvé.</div>"

    html_content = ""
    for item in results:
        html_content += f"""
        <a href="/detail?url={item['url']}" class="search-item">
            <img src="{item['img']}" alt="{item['title']}" class="search-img">
            <div class="search-info">
                <p class="search-title">{item['title']}</p>
            </div>
        </a>
        """

    return html_content


@router.post("/schedule", response_class=HTMLResponse)
async def schedule_anime(
    anime: str = Form(...), season: str = Form(...), lang: str = Form(...),
    day: str = Form(...), hour: int = Form(...), minute: int = Form(...),
    anime_url: str = Form(...), image: str = Form(...)
):
    anime_date = create_datetime_from_day(day, hour, minute)
    available_episodes = fetch_episodes(get_anime_catalog_url(anime_url), headers=get_headers())
    last_episode_released: int = get_last_episode_released(available_episodes) if available_episodes else 0

    week_episode = last_episode_released + 1 if anime_date > anime_date.now() else last_episode_released

    app_datas.add_new_anime(anime_url, image, anime, lang, season, week_episode, anime_date)
    app_logger.info(f"Ajout au planning : {anime} ({season} - {lang})")
    app_datas.save(None, None, None)

    payload = {
        "anime": anime, "season": season, "lang": lang, "day": day,
        "hour": hour, "minute": minute, "anime_url": anime_url,
        "image": image
    }
    safe_hx_vals = html.escape(json.dumps(payload))

    return f"""
    <button class="btn-schedule"
            style="background-color: var(--btn-success);"
            title="Cliquez pour annuler la programmation"
            hx-post="/api/v1/schedule/delete"
            hx-vals="{safe_hx_vals}"
            hx-swap="outerHTML"
            onclick="event.stopPropagation();">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="display:inline; vertical-align: text-bottom; margin-right: 4px;">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
        Programmé
    </button>
    """


@router.post("/schedule/delete", response_class=HTMLResponse)
async def unschedule_anime(
    anime: str = Form(...), season: str = Form(...), lang: str = Form(...),
    day: str = Form(...), hour: int = Form(...), minute: int = Form(...),
    anime_url: str = Form(...), image: str = Form(...)
):
    try:
        app_datas.remove_anime(anime, season, lang)
    except ValueError:
        app_logger.error(f"Anime introuvable : {anime} ({season} - {lang})")

    app_logger.info(f"Retrait du planning : {anime} ({season} - {lang})")
    app_datas.save(None, None, None)

    payload = {
        "anime": anime, "season": season, "lang": lang, "day": day,
        "hour": hour, "minute": minute, "anime_url": anime_url,
        "image": image
    }
    safe_hx_vals = html.escape(json.dumps(payload))

    return f"""
    <button class="btn-schedule"
            hx-post="/api/v1/schedule"
            hx-vals="{safe_hx_vals}"
            hx-swap="outerHTML"
            onclick="event.stopPropagation();">
        Programmer
    </button>
    """


@router.get("/today-anime", response_class=HTMLResponse)
async def get_today_anime():
    now = datetime.now()
    animes_day = app_datas.animes_from_day(now.weekday())

    if not animes_day:
        return """
        <div style='grid-column: 1 / -1; text-align: center; padding: 2rem; color: var(--text-muted); font-style: italic;'>
            Aucun téléchargement prévu pour aujourd'hui.
        </div>
        """

    animes_day = sorted(animes_day, key=lambda a: (int(a.release_hour), int(a.release_min)))

    anime_cards = ""
    for anime in animes_day:
        release_date = create_datetime_from_day(anime.release_day, anime.release_hour, anime.release_min)

        if release_date <= now:
            status_html = """
                <div class="card-status done">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg>
                    Téléchargé
                </div>
            """
        else:
            minute_str = str(anime.release_min).zfill(2)
            status_html = f"""
                <div class="card-status pending">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Prévu à {anime.release_hour}h{minute_str}
                </div>
            """

        anime_cards += f"""
            <div class="anime-card">
                <a href="/detail?url={anime.anime_url}" style="text-decoration: none; color: inherit; display: block;">
                    <div class="card-image-wrapper">
                        <img src="{anime.image}" alt="{anime.title}">
                        <span class="badge badge-type">Anime</span>
                        <span class="badge badge-lang">{anime.lang}</span>
                    </div>
                </a>
                <div class="card-content">
                    <a href="/detail?url={anime.anime_url}" style="text-decoration: none; color: inherit;">
                        <h3 class="card-title" title="{anime.title}">{anime.title}</h3>
                    </a>
                    <div class="card-info">
                        <span>Épisode {anime.week_episode}</span>
                        <span>{anime.season}</span>
                    </div>
                    {status_html}
                </div>
            </div>
        """

    return anime_cards


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Working API !"}


@router.get("/planning-content")
async def get_planning_content(request: Request, lang: str = Query("all")):
    full_planning: dict[str, list[Anime]] | None = get_cached_planning()

    if full_planning is None:
        app_logger.error("Failed to fetch planning data")
        return None

    lang_mapping = {
        "VOSTFR": "jp",
        "VF": "fr",
        "VCN": "ch",
        "VA": "en"
    }

    filtered_planning = {}

    if lang == "all":
        filtered_planning = full_planning
    else:
        for day, animes in full_planning.items():
            anime_filter = [
                anime for anime in animes
                if lang_mapping.get(anime.language, "all") == lang
            ]
            if anime_filter:
                filtered_planning[day] = anime_filter

    for animes in filtered_planning.values():
        for anime in animes:
            anime.has_been_programmed = app_datas.has_been_registered(anime.name, anime.season, anime.language)

    return templates.TemplateResponse(
        request=request,
        name="planning_cards.html",
        context={
            "request": request,
            "planning": filtered_planning
        }
    )


@router.get("/episodes", response_class=HTMLResponse)
async def get_episodes(_: Request, season_url: str, anime_name: str, season_name: str):
    episodes_data = fetch_episodes(season_url, headers=get_headers())

    episodes_count = len(list(episodes_data.values())[0]) if episodes_data else 0

    html_content = ""
    for i in range(1, episodes_count + 1):
        # 1. On crée le dictionnaire des valeurs à envoyer
        payload = {
            "season_url": season_url,
            "episode": i,
            "anime_name": anime_name
        }

        safe_hx_vals = html.escape(json.dumps(payload))

        html_content += f"""
        <div class="episode-row">
            <span class="episode-name">Épisode {i}</span>
            <button class="btn-download-ep"
                    hx-post="/api/v1/download/episode"
                    hx-vals="{safe_hx_vals}"
                    hx-swap="outerHTML">
                Télécharger
            </button>
        </div>
        """

    if not html_content:
        html_content = "<div class='episode-row'><span class='episode-name'>Aucun épisode trouvé.</span></div>"

    return html_content


@router.post("/download/season", response_class=HTMLResponse)
async def download_season(background_tasks: BackgroundTasks, season_url: str = Form(), anime_name: str = Form()):
    app_logger.info(f"Téléchargement de la saison {season_url}...")

    background_tasks.add_task(
        run_download_task,
        season_url=season_url,
        anime_name=anime_name,
        episodes=set(),
        full_season=True
    )

    return """
        <button class='btn-download' style='background: var(--btn-success); cursor: default;' disabled>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="display:inline; vertical-align: text-bottom; margin-right: 4px;">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
            Démarré
        </button>
        """


@router.post("/download/episode", response_class=HTMLResponse)
async def download_episode(
    background_tasks: BackgroundTasks,
    season_url: str = Form(...),
    episode: int = Form(...),
    anime_name: str = Form(...)
):
    app_logger.info(f"Lancement de la tâche : Épisode {episode} de {anime_name}")

    background_tasks.add_task(
        run_download_task,
        season_url=season_url,
        anime_name=anime_name,
        episodes=[episode],
        full_season=False
    )

    return """
    <button class='btn-download-ep' style='background: var(--btn-success); cursor: default;' disabled>
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="display:inline; vertical-align: text-bottom; margin-right: 4px;">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
        Démarré
    </button>
    """
