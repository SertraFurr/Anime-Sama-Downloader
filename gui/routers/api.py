from fastapi import APIRouter, Query
from starlette.requests import Request
from starlette.responses import HTMLResponse

from gui.cloudflare import get_headers
from gui.routers.web import templates, get_cached_planning
from utils.fetch.fetch_episodes import fetch_episodes

router = APIRouter(tags=["Backend / Download API"])

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
