from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="gui/templates")
