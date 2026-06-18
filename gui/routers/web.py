from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

from gui.cloudflare import get_headers
from utils.fetch.planning import fetch_planning
from cachetools import TTLCache, cached

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="gui/templates")

planning_cache = TTLCache(maxsize=1, ttl=3600)

@cached(planning_cache)
def get_cached_planning():
    return fetch_planning(get_headers())


@router.get("/", response_class=HTMLResponse)
async def detail_page(request: Request):
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
async def detail_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"request": request}
    )

@router.get("/settings", response_class=HTMLResponse)
async def detail_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={"request": request}
    )
