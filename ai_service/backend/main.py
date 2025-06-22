import dotenv
from fastapi import FastAPI

from src.api import all_routers

dotenv.load_dotenv()

app = FastAPI()


for router in all_routers:
    app.include_router(router)
