import os

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from starlette.responses import FileResponse

from app_context import get_current_user_context, user_contexts
from user_context import UserContext

router = APIRouter()


class FCMTokenRequest(BaseModel):
    token: str


@router.post("/api/fcm/register")
async def register_fcm_token(request: FCMTokenRequest, user_context: UserContext = Depends(get_current_user_context)):
    try:
        if user_context.data.fcm_token is None:
            user_context.data.fcm_token = set()
        user_context.data.fcm_token.add(request.token)
        user_contexts.set(user_context)

        return {"status": "success", "message": "FCM token registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register FCM token: {str(e)}")


# Serve Firebase service worker from root path (required for security scope)
@router.get("/firebase-messaging-sw-{suffix}")
async def firebase_service_worker(suffix: str = Path(...)):
    filename = f"firebase-messaging-sw-{suffix}"
    filepath = os.path.join("static", "dist", filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Service worker file not found")
    return FileResponse(filepath, media_type="application/javascript")
