import asyncio
import html
import json

from fastapi import APIRouter, Query, Form
from starlette.requests import Request
from starlette.responses import HTMLResponse, StreamingResponse

from gui.cloudflare import get_headers
from gui.logger import log_clients, log_history, app_logger
from gui.routers.web import templates, get_cached_planning
from gui.storage.anime_data import app_datas
from gui.utils import create_datetime_from_day
from utils.fetch.fetch_episodes import fetch_episodes
from utils.fetch.planning import Anime

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


@router.get("/stream-logs")
async def stream_logs(request: Request):
    return StreamingResponse(log_generator(request), media_type="text/event-stream")


@router.post("/download/episode")
async def start_download(
        anime: str = Form(...),
        saison: str = Form(...),
        episode: str = Form(...)
):
    app_logger.info(f"Initialisation du téléchargement pour {anime} (S{saison} E{episode})")

    try:
        await asyncio.sleep(2)

        app_logger.info(f"[{anime}] Épisode {episode} téléchargé avec succès !")

    except ConnectionError:
        app_logger.warning(f"[{anime}] Latence détectée, changement de miroir...")

    except Exception as e:
        app_logger.error(f"[{anime}] Échec critique du téléchargement : {str(e)}")

    return "<button class='btn-download-ep' style='background: var(--btn-success)'>Ajouté !</button>"

@router.post("/schedule", response_class=HTMLResponse)
async def schedule_anime(
    anime: str = Form(...), season: str = Form(...), lang: str = Form(...),
    day: str = Form(...), hour: int = Form(...), minute: int = Form(...),
    anime_url: str = Form(...), image: str = Form(...), week_episode: int = Form(...)
):
    anime_date = create_datetime_from_day(day, hour, minute)
    app_datas.add_new_anime(anime_url=anime_url, image=image, title=anime, lang=lang, season=season, week_episode=week_episode, release_date=anime_date)
    app_logger.info(f"Ajout au planning : {anime} ({season} - {lang})")
    app_datas.save(None, None, None)

    payload = {
        "anime": anime, "season": season, "lang": lang, "day": day,
        "hour": hour, "minute": minute, "anime_url": anime_url,
        "image": image, "week_episode": week_episode
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
    anime_url: str = Form(...), image: str = Form(...), week_episode: int = Form(...)
):
    try:
        app_datas.remove_anime(title=anime, lang=lang, season=season)
    except ValueError:
        app_logger.error(f"Anime introuvable : {anime} ({season} - {lang})")

    app_logger.info(f"Retrait du planning : {anime} ({season} - {lang})")
    app_datas.save(None, None, None)

    payload = {
        "anime": anime, "season": season, "lang": lang, "day": day,
        "hour": hour, "minute": minute, "anime_url": anime_url,
        "image": image, "week_episode": week_episode
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
        html_content += f"""
        <div class="episode-row">
            <span class="episode-name">Épisode {i}</span>
            <button class="btn-download-ep"
                    hx-post="/api/download/episode"
                    hx-vals='{{"anime": "{anime_name}", "saison": "{season_name}", "episode": "{i}"}}'
                    hx-swap="outerHTML">
                Télécharger
            </button>
        </div>
        """

    if not html_content:
        html_content = "<div class='episode-row'><span class='episode-name'>Aucun épisode trouvé.</span></div>"

    return html_content
