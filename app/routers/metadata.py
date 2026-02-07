from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy import text
from app.config import settings
from app.models import *
from app.services import MetadataScraper
import logging

router = APIRouter(
    prefix="/metadata",
    tags=["metadata"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{ticker}")
def get_metadata(ticker: str):
    query = text("""
        SELECT * FROM company_metadata
        WHERE symbol = :ticker
    """)
    params = {"ticker": ticker}
    with SessionLocal() as session:
        result = session.execute(query, params)
        metadata = result.fetchone()
    if not metadata:
        raise HTTPException(status_code=404, detail="No metadata found for the given ticker.")
    return dict(metadata._mapping)


