from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta, timezone, date

from app.config import settings
from app.models import *
from app.services import DatabaseService
import logging

router = APIRouter(
    prefix="/news",
    tags=["news"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{ticker}")
def get_news_average_articles(ticker: str, query_date: date):
    start_of_day = datetime.combine(query_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_of_day = datetime.combine(query_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    articles = list(news_collection.find({"ticker": ticker, "published_at": {"$gte": start_of_day, "$lt": end_of_day}}))
    if not articles:
        raise HTTPException(status_code=404, detail="Articles not found")
    keywords = []
    for query in articles:
        keywords.extend(query.get("keywords", []))
    good_keywords = [kw for kw in keywords if isinstance(kw, dict) and kw.get('label') == 'positive']
    bad_keywords = [kw for kw in keywords if isinstance(kw, dict) and kw.get('label') == 'negative']
    good_small_keywords = sorted(good_keywords, key=lambda x: len(str(x)))[:2]
    bad_small_keywords = sorted(bad_keywords, key=lambda x: len(str(x)))[:2]

    average_sentiment = sum(article.get("sentiment", {}).get("confidence", 0) for article in articles) / len(articles)
    return {"ticker": ticker, "average_sentiment": average_sentiment,
            "good_keywords": good_small_keywords,
            "bad_keywords": bad_small_keywords}
