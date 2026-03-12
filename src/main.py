import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import settings
from routers import client, pages, server

logging.basicConfig(level=settings.log_level.upper())

BASE_DIR = Path(__file__).parent

app = FastAPI(title="USBIP GUI", version="1.0.0")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(pages.router)
app.include_router(server.router)
app.include_router(client.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=False,
    )
