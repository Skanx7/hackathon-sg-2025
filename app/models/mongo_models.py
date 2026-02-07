from datetime import timezone, datetime
from typing import List, Dict, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

from app.config import settings

import logging
from pymongo import TEXT
from pymongo.errors import PyMongoError

try:
    client = MongoClient(settings.MONGODB_URL,
                            serverSelectionTimeoutMS=5000,
                            connectTimeOutMS=5000)
    db = client[settings.MONGODB_DB]

    news_collection = db["news"]
    company_collection = db["companies"]
    logging.info(f"Connected to MongoDB at {settings.MONGODB_URL}, using database '{settings.MONGODB_DB}'")
except ConnectionFailure as e:
    logging.error(f"Could not connect to MongoDB: {e}")
    client = None
    db = None
    news_collection = None
    company_collection = None

class NewsDocument:
    @staticmethod
    def create(
        ticker: str,
        title: str,
        content: str,
        medium: str,
        source: str,
        published_at: datetime,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        url: Optional[str] = None,
        sentiment_dict: Optional[Dict] = None,
        sentiment_label: Optional[str] = None,
        sentiment_confidence: Optional[float] = None,
        embedding: Optional[List[float]] = None
    ) -> Dict:
        return {
            "ticker": ticker,
            "title": title,
            "content": content,
            "medium": medium,
            "source": source,
            "description": description,
            "keywords": keywords or [],
            "url": url,
            "published_at": published_at,
            "created_at": datetime.now(timezone.utc),
            "embedding": embedding,
            # snapshot
            "sentiment": {
                "dict" : sentiment_dict,
                "label": sentiment_label,       # 'positive' | 'neutral' | 'negative'
                "confidence": sentiment_confidence,       # e.g. -1..1
                "updated_at": datetime.now(timezone.utc) if sentiment_label else None,
            }
        }
    
news_collection.create_index([("ticker", ASCENDING)])
news_collection.create_index([("published_at", DESCENDING)])

class CompanyDocument:
    @staticmethod
    def create(
        symbol: str,
        embedding : Optional[List[float]] = None,
        keywords: Optional[List[str]] = []

    ) -> Dict:
        return {
            "symbol": symbol,
            "embedding": embedding,
            "keywords": keywords or [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    

company_collection.create_index([("symbol", ASCENDING)], unique=True)

logging.info("MongoDB indexes created successfully")
