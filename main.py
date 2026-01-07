# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.scholarship import router as scholarships_router

app = FastAPI(
    title="Scholarship Tracker API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "It Works!"}


app.include_router(scholarships_router)
