from fastapi import APIRouter

router = APIRouter(tags=["Backend / Download API"])

@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Working API !"}
