
from typing import List



from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.config import settings
from app.models import *
from app.services import DatabaseService
from app.services.nlp_tasks import NLPTasks
import logging
import tqdm
router = APIRouter(
    prefix="/inference",
    tags=["inference"],
    responses={404: {"description": "Not found"}},
)


@router.post("/company_embeddings")
def generate_company_embeddings():
    query = text("""
        SELECT symbol, name, industry, summary FROM company_metadata
    """)
    with SessionLocal() as session:
        result = session.execute(query)
        companies = result.fetchall()
    for company in tqdm.tqdm(companies):
        industry = company.industry or ""
        summary = company.summary or ""
        emb = NLPTasks.generate_semantic_embedding(industry + " " + summary)
        keywords = NLPTasks.summarize_into_keywords(summary)
        company_document = CompanyDocument().create(
            symbol=company.symbol,
            embedding=emb,
            keywords=keywords
        )
        logging.debug(f"Generated embedding and keywords for {company.symbol}")
        logging.debug(f"Keywords: {keywords}")
        company_collection.insert_one(company_document)
    
    logging.info("Company embeddings and keywords generation complete.")
    return ["Company embeddings and keywords generated successfully."]

@router.post("/news_sentiment_analysis")
def perform_news_sentiment_analysis():
    nosql_query = { "sentiment.updated_at": None }
    news_articles = list(news_collection.find(nosql_query))
    print(f"Found {len(news_articles)} articles to process.")
    for article in tqdm.tqdm(news_articles):
        content = article.get("content", "")
        if not content:
            continue
        sentiment_dict = NLPTasks.analyze_sentiment(content)
        sentiment_confidence = sentiment_dict.get("positive", 0) - sentiment_dict.get("negative", 0) 
        semantic_embedding = NLPTasks.generate_semantic_embedding(content)
        keywords = NLPTasks.summarize_into_keywords(content)
        news_collection.update_one(
            {"_id": article["_id"]},
            {"$set": {
                "sentiment.dict": sentiment_dict,
                "sentiment.label": max(sentiment_dict, key=sentiment_dict.get),
                "sentiment.confidence": sentiment_confidence,
                "sentiment.updated_at": datetime.now(timezone.utc),
                "keywords": keywords,
                "embedding": semantic_embedding
            }}
        )

        logging.debug(f"Updated sentiment for article ID {article['_id']}: {sentiment_dict} ({sentiment_confidence})")
        logging.debug(f"Extracted keywords for article ID {article['_id']}: {keywords}")
