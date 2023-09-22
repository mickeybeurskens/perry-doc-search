from fastapi import FastAPI
from perry.api.endpoints.user import user_router
from perry.api.endpoints.document import document_router, file_router

app = FastAPI()

USERS_URL = "/users"
DOCUMENTS_URL = "/documents/info"
FILES_URL = "/documents/file"

app.include_router(user_router, prefix=USERS_URL)
app.include_router(file_router, prefix=FILES_URL)
app.include_router(document_router, prefix=DOCUMENTS_URL)
