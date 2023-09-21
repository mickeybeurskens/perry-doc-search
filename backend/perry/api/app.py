from fastapi import FastAPI
from perry.api.endpoints.user import user_router
from perry.api.endpoints.document import document_router, file_router

app = FastAPI()

app.include_router(user_router, prefix="/users")
app.include_router(document_router, prefix="/documents/info")
app.include_router(file_router, prefix="/documents/file")
