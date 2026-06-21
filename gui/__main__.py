import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from gui.cloudflare import get_headers
from gui.routers import web, api
from utils.search.search_bar import search_anime_query

load_dotenv()

print(search_anime_query("tsue", headers=get_headers()))

app = FastAPI(title="Anime-Sama Downloader GUI")

app.mount("/static", StaticFiles(directory="gui/static"), name="static")
app.include_router(web.router)
app.include_router(api.router, prefix="/api/v1")

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", 8000))
    reload = os.getenv("APP_RELOAD", "true").lower() == "true"

    uvicorn.run("gui.__main__:app", host=host, port=port, reload=reload)
