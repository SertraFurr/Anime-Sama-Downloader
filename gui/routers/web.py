from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="gui/templates")


@router.get("/", response_class=HTMLResponse)
async def detail_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request}
    )


@router.get("/planning", response_class=HTMLResponse)
async def planning_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="planning.html",
        context={"request": request}
    )


@router.get("/detail", response_class=HTMLResponse)
async def detail_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"request": request}
    )
