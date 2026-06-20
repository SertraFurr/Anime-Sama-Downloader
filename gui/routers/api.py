import asyncio

from fastapi import APIRouter, Query, Form
from starlette.requests import Request
from starlette.responses import HTMLResponse, StreamingResponse

from gui.cloudflare import get_headers
from gui.logger import log_clients, log_history, app_logger
from gui.routers.web import templates, get_cached_planning
from utils.fetch.fetch_episodes import fetch_episodes

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


@router.post("/api/download/episode")
async def start_download(
        anime: str = Form(...),
        saison: str = Form(...),
        episode: str = Form(...)
):
    app_logger.info(f"Initialisation du téléchargement pour {anime} (S{saison} E{episode})")

    try:
        # Simulation d'un travail (ex: appel à ta CLI)
        await asyncio.sleep(2)

        # Astuce : Dans notre HTMXConsoleHandler, on a codé une règle qui passe le log
        # en VERT (.log-success) s'il contient le mot "succès" ou "terminé".
        app_logger.info(f"[{anime}] Épisode {episode} téléchargé avec succès !")

    except ConnectionError:
        # .warning() -> S'affichera en jaune/orange (classe .log-warning)
        app_logger.warning(f"[{anime}] Latence détectée, changement de miroir...")

    except Exception as e:
        app_logger.error(f"[{anime}] Échec critique du téléchargement : {str(e)}")

    return "<button class='btn-download-ep' style='background: var(--btn-success)'>Ajouté !</button>"

@router.post("/schedule", response_class=HTMLResponse)
async def schedule_anime(
    anime: str = Form(...),
    saison: str = Form(...),
    langue: str = Form(...)
):
    app_logger.info(f"Ajout au planning : {anime} ({saison} - {langue})")

    return f"""
    <button class="btn-schedule" style="background-color: var(--btn-success); cursor: default;" disabled>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" style="display:inline; vertical-align: text-bottom; margin-right: 4px;">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
        Programmé
    </button>
    """

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Working API !"}


@router.get("/planning-content")
async def get_planning_content(request: Request, lang: str = Query("all")):
    full_planning = get_cached_planning()

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
        for jour, animes in full_planning.items():
            animes_filtres = [
                anime for anime in animes
                if lang_mapping.get(anime.language, "all") == lang
            ]
            if animes_filtres:
                filtered_planning[jour] = animes_filtres

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
