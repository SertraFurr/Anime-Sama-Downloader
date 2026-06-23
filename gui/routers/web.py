from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from gui.utils.cached import get_cached_planning
from gui.utils.cloudflare import get_headers
from gui.utils import normalize_catalog_url
from utils.fetch.detail import fetch_anime_details
from utils.search.expand_catalogue import expand_catalogue_url

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="gui/templates")


@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request}
    )


@router.get("/planning")
async def planning_page(request: Request):
    planning_data = get_cached_planning()

    lang_mapping = {
        "VOSTFR": "jp",
        "VF": "fr",
        "VCN": "ch",
        "VA": "en"
    }

    return templates.TemplateResponse(
        request=request,
        name="planning.html",
        context={
            "request": request,
            "planning": planning_data,
            "lang_map": lang_mapping
        }
    )


@router.get("/detail", response_class=HTMLResponse)
async def detail_page(request: Request, url: str):
    complete_url = normalize_catalog_url(url)

    anime_details = fetch_anime_details(complete_url, headers=get_headers())

    season_options = expand_catalogue_url(complete_url, headers=get_headers())

    anime_season_options = filter(lambda x: x["name"] != "Scans", season_options)

    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={
            "request": request,
            "anime": anime_details,
            "seasons": anime_season_options
        }
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={"request": request}
    )
