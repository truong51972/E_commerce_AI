from fastapi import FastAPI

from src.api import all_routers

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

for router in all_routers:
    app.include_router(router, prefix="/api")
