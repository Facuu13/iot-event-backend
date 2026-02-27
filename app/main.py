from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="IoT Event Backend")

app.include_router(router)