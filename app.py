import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app_context import templates, get_current_user_context
from routes.book import router as book_router
from routes.job import router as job_router
from routes.login import router as login_router
from routes.search import router as search_router
from routes.fcm import router as fcm_router
from routes.home import router as home_router

from scheduler import scheduler, get_jobs

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(login_router)
app.include_router(book_router)
app.include_router(search_router)
app.include_router(job_router)
app.include_router(fcm_router)
app.include_router(home_router)
