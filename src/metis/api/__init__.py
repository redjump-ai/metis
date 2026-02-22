"""FastAPI application for Metis."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from metis.config import settings

app = FastAPI(title="Metis API", version="0.1.0")


class FetchRequest(BaseModel):
    url: str
    save: bool = True


class FetchResponse(BaseModel):
    success: bool
    message: str
    path: str | None = None


@app.get("/")
def root():
    return {"message": "Metis API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
