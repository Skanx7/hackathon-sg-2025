from fastapi import APIRouter, HTTPException
from app.models import SessionLocal
from sqlalchemy import text
from datetime import date
from typing import Optional
import logging


router = APIRouter(
    prefix="/sentiment",
    tags=["sentiment"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{ticker}/{query_date}")
def get_sentiment_by_ticker_and_date(ticker: str, query_date: date):
    """
    Get sentiment record for a specific ticker on a specific date.
    """
    query = text("""
        SELECT * FROM sentiment_records
        WHERE ticker = :ticker AND date = :query_date
    """)
    params = {"ticker": ticker, "query_date": query_date}
    
    with SessionLocal() as session:
        result = session.execute(query, params)
        sentiment = result.fetchone()
    
    if not sentiment:
        raise HTTPException(status_code=404, detail="No sentiment data found for the given ticker and date.")
    
    return dict(sentiment._mapping)

@router.get("/{ticker}")
def get_sentiment_by_ticker(ticker: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Get sentiment records for a specific ticker, optionally filtered by date range.
    """
    query = """
        SELECT * FROM sentiment_records
        WHERE ticker = :ticker
    """
    params = {"ticker": ticker}
    
    if start_date:
        query += " AND date >= :start_date"
        params["start_date"] = start_date
    
    if end_date:
        query += " AND date <= :end_date"
        params["end_date"] = end_date
    
    query += " ORDER BY date ASC"
    
    with SessionLocal() as session:
        result = session.execute(text(query), params)
        sentiments = result.fetchall()
    
    if not sentiments:
        raise HTTPException(status_code=404, detail="No sentiment data found for the given ticker.")
    
    return [dict(row._mapping) for row in sentiments]

