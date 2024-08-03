from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.messages.models import create_tables
from api.routers import messages, tests

# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(messages.router, prefix="/api")
app.include_router(tests.router, prefix="/tests")


@app.get("/db")
async def start_db():
    return await create_tables()
