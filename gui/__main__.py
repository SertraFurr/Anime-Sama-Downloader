import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from gui.daemon import check_and_download_scheduled, scheduler
from gui.routers import web, api


load_dotenv()


@asynccontextmanager
async def lifespan(_):
    daemon_task = asyncio.create_task(check_and_download_scheduled())

    scheduler.start()

    yield

    daemon_task.cancel()
    scheduler.shutdown()

app = FastAPI(title="Anime-Sama Downloader GUI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="gui/static"), name="static")
app.include_router(web.router)
app.include_router(api.router, prefix="/api/v1")

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", 8000))
    reload = os.getenv("APP_RELOAD", "true").lower() == "true"

    uvicorn.run("gui.__main__:app", host=host, port=port, reload=reload)
