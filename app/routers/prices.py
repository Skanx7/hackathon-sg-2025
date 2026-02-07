from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta

from app.models import *

router = APIRouter(
    prefix="/prices",
    tags=["prices"],
    responses={404: {"description": "Not found"}},
)
@router.get("/historical/{ticker}")
def fetch_historical_prices(ticker: str, start_date: date, end_date: date):
    query = text("""
        SELECT * FROM stock_prices
        WHERE ticker = :ticker
        AND date >= :start_date
        AND date <= :end_date
        ORDER BY date ASC
    """)
    params = {
        "ticker": ticker,
        "start_date": start_date,
        "end_date": end_date
    }

    with SessionLocal() as session:
        result = session.execute(query, params)
        prices = result.fetchall()

    if not prices:
        raise HTTPException(status_code=404, detail="No price data found for the given ticker and date range.")

    return [dict(row._mapping) for row in prices]

@router.get("/latest/{ticker}")
def fetch_latest_price(ticker: str):
    query = text("""
        SELECT * FROM stock_prices
        WHERE ticker = :ticker
        ORDER BY date DESC
        LIMIT 1
    """)
    params = {"ticker": ticker}

    with SessionLocal() as session:
        result = session.execute(query, params)
        price = result.fetchone()

    if not price:
        raise HTTPException(status_code=404, detail="No price data found for the given ticker.")

    return dict(price._mapping)