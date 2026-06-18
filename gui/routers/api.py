from fastapi import APIRouter
from starlette.requests import Request

from gui.routers.web import templates, get_cached_planning

router = APIRouter(tags=["Backend / Download API"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Working API !"}


@router.get("/planning-content")
async def get_planning_content(request: Request):
    planning_data = get_cached_planning()

    lang_mapping = {
        "VOSTFR": "jp", "VF": "fr", "VCN": "ch", "VA": "en"
    }

    return templates.TemplateResponse(
        request=request,
        name="planning_cards.html",
        context={
            "request": request,
            "planning": planning_data,
            "lang_map": lang_mapping
        }
    )
