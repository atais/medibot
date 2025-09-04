import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

from app_context import templates, get_current_user_context, user_contexts
from routes.book import router as book_router
from routes.job import router as job_router
from routes.login import router as login_router
from routes.search import router as search_router
from scheduler import scheduler, get_jobs

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    user_contexts.load_from_disk()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.include_router(login_router)
app.include_router(book_router)
app.include_router(search_router)
app.include_router(job_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user_context=Depends(get_current_user_context)):
    jobs = get_jobs(user_context)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": user_context.username,
        "jobs": jobs
    })
