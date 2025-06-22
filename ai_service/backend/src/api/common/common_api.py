from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src import redis_client

router = APIRouter()


@router.get("/")
def read_root():
    return RedirectResponse(url="/docs")


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/clear_cache")
def clear_cache():
    """
    Endpoint to clear the Redis cache.
    """
    redis_client.flushdb()
    return {"status": "Cache cleared"}
