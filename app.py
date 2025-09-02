import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse

import medicover
from app_context import user_contexts, templates
from routes.book import router as book_router
from routes.login import router as login_router
from routes.search import router as search_router
from scheduler import scheduler

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

@asynccontextmanager
async def lifespan(app):
    scheduler.start()
    yield
    scheduler.shutdown()

logging.basicConfig(level=logging.INFO)
app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.include_router(login_router)
app.include_router(book_router)
app.include_router(search_router)


@app.get("/", response_class=HTMLResponse)
async def hello(request: Request):
    try:
        region_ids = request.query_params.get("region_ids")
        specialty_ids = request.query_params.get("specialty_ids")
        start_time = request.query_params.get("start_time")

        session_id = request.session.get("session_id")
        context = user_contexts.get(session_id)
        me = medicover.me(context.session)

        if not session_id or not context or not me:
            return RedirectResponse(url="/login", status_code=302)
        elif not region_ids or not specialty_ids or not start_time:
            return RedirectResponse(
                url=f"/?region_ids=204&specialty_ids=76798&start_time=2025-09-03",
                status_code=302
            )
        else:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "name": session_id,
                "region_ids": region_ids,
                "specialty_ids": specialty_ids,
                "start_time": start_time,
            })
    except Exception as e:
        logging.error(e)
        return RedirectResponse(url="/login", status_code=302)
