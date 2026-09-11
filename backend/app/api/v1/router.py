from fastapi import APIRouter


from app.api.v1 import auth, chat, events, audit, settings as settings_router


api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(settings_router.router, prefix="/settings", tags=["settings"])
