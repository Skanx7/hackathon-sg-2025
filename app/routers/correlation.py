from fastapi import APIRouter, HTTPException
from app.models import SessionLocal
from sqlalchemy import text
from datetime import date
from typing import Optional
import logging


router = APIRouter(
    prefix="/correlation",
    tags=["correlation"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{ticker}")
def get_correlation_by_ticker(ticker: str, start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Get correlation records for a specific ticker, optionally filtered by date range.
    """
    query = """
        SELECT * FROM correlation_records
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
        correlations = result.fetchall()
    
    if not correlations:
        raise HTTPException(status_code=404, detail="No correlation data found for the given ticker.")
    
    return [dict(row._mapping) for row in correlations]

@router.get("/{ticker}/{query_date}")
def get_correlation_by_ticker_and_date(ticker: str, query_date: date):
    """
    Get correlation record for a specific ticker on a specific date.
    """
    query = text("""
        SELECT * FROM correlation_records
        WHERE ticker = :ticker AND date = :query_date
    """)
    params = {"ticker": ticker, "query_date": query_date}
    
    with SessionLocal() as session:
        result = session.execute(query, params)
        correlation = result.fetchone()
    
    if not correlation:
        raise HTTPException(status_code=404, detail="No correlation data found for the given ticker and date.")
    
    return dict(correlation._mapping)
