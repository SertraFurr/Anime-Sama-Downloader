from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from gui.cloudflare import get_headers
from gui.utils import get_domain, get_anime_catalog_url
from utils.fetch.detail import fetch_anime_details
from utils.fetch.planning import fetch_planning
from cachetools import TTLCache, cached
from utils.search.expand_catalogue import expand_catalogue_url

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="gui/templates")

planning_cache = TTLCache(maxsize=1, ttl=3600)

@cached(planning_cache)
def get_cached_planning():
    return fetch_planning(get_headers())


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
    catalog_url: str = "/".join(url.split("/")[:3])
    complete_url: str = get_anime_catalog_url(catalog_url)

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
