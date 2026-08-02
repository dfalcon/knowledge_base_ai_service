from fastapi import FastAPI

from app.api.routers import health

app = FastAPI()
app.include_router(health.router)
