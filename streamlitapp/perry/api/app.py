from fastapi import FastAPI
from perry.api.endpoints.user import user_router

app = FastAPI()

app.include_router(user_router)
