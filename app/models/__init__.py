# Export MongoDB models and collections
from app.models.mongo_models import (
    news_collection,
    company_collection,
    NewsDocument,
    CompanyDocument
)

# Export SQL models and session
from app.models.sql_models import (
    SessionLocal,
    Base,
    StockPrice,
    CompanyMetadata,
    SentimentRecord,
    CorrelationRecord,
    engine
)

__all__ = [
    # MongoDB
    "news_collection",
    "company_collection",
    "NewsDocument",
    "CompanyDocument",
    # SQL
    "SessionLocal",
    "Base",
    "StockPrice",
    "CompanyMetadata",
    "SentimentRecord",
    "CorrelationRecord",
    "engine"
]
