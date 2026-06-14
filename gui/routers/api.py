from fastapi import APIRouter

router = APIRouter(tags=["Backend / Download API"])

@router.get("/health")
def health_check():
    return {"status": "ok", "message": "Working API !"}
