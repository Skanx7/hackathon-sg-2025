from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.models import *
from app.services import DatabaseService
import logging
router = APIRouter(
    prefix="/database",
    tags=["database"],
    responses={404: {"description": "Not found"}},
)
@router.post("/populate_sql_metadata")
def populate_metadata():
    db_service = DatabaseService()
    db_service.populate_sql_metadata()
    logging.info("SQL Metadata population endpoint called.")
    return ["SQL metadata populated successfully."]

@router.post("/populate_sql_prices")
def populate_prices():
    db_service = DatabaseService()
    db_service.populate_sql_prices()
    logging.info("SQL Prices population endpoint called.")
    return ["SQL prices populated successfully."]

@router.post("/populate_sql")
def populate_sql():
    db_service = DatabaseService()
    db_service.populate_sql()
    logging.info("SQL Database population endpoint called.")
    return ["SQL database populated successfully."]

@router.post("/populate_nosql_newsapi")
def populate_nosql_newsapi(last_n_days: int = 30):
    db_service = DatabaseService()
    db_service.populate_nosql_newsapi(last_n_days=last_n_days)
    logging.info("NoSQL NewsAPI population endpoint called.")
    return ["NoSQL NewsAPI data populated successfully."]

@router.post("/populate_nosql_polygon")
def populate_nosql_polygon(start_date: str, end_date: Optional[str] = None, limit: int = 1000):
    db_service = DatabaseService()
    start_date = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    end_date = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc) if end_date else None
    db_service.populate_nosql_polygon(start_date=start_date, end_date=end_date, limit=limit)
    logging.info("NoSQL Polygon population endpoint called.")
    return ["NoSQL Polygon data populated successfully."]

@router.post("/populate_nosql_reddit")
def populate_nosql_reddit(last_n_days: int = 30, subreddits: Optional[List[str]] = None):
    db_service = DatabaseService()
    db_service.populate_nosql_reddit(last_n_days=last_n_days, subreddits=subreddits)
    logging.info("NoSQL Reddit population endpoint called.")
    return ["NoSQL Reddit data populated successfully."]

@router.post("/populate_nosql")
def populate_nosql(last_n_days: int = 30):
    db_service = DatabaseService()
    db_service.populate_nosql_newsapi(last_n_days=last_n_days)
    start_date = datetime.now(timezone.utc) - timedelta(days=last_n_days)
    db_service.populate_nosql_polygon(start_date=start_date, limit=1000)
    db_service.populate_nosql_reddit(last_n_days=last_n_days)
    return ["NoSQL database populated successfully."]
@router.post("/export_sql")
def export_sql(backup_url: Optional[str] = None):
    db_service = DatabaseService()
    db_service.backup_sql(backup_url=backup_url)
    return ["SQL database backup completed successfully."]

@router.post("/export_nosql")
def export_nosql(output_dir: Optional[str] = "app/backups"):
    """Export NoSQL (MongoDB) database to JSON files"""
    db_service = DatabaseService()
    result = db_service.export_nosql(output_dir=output_dir)
    logging.info("NoSQL export endpoint called.")
    return result
@router.post("/import_sql")
def import_sql(backup_url: Optional[str] = settings.SQLITE_URL):
    db_service = DatabaseService()
    db_service.import_sql(import_url=backup_url)
    logging.info("SQL import endpoint called.")
    return ["SQL database restoration completed successfully."]

@router.post("/import_nosql")
def import_nosql(input_dir: Optional[str] = "app/backups"):
    """Import NoSQL (MongoDB) database from JSON files"""
    db_service = DatabaseService()
    result = db_service.import_nosql(input_dir=input_dir)
    logging.info("NoSQL import endpoint called.")
    return result

@router.post("/populate_sentiment")
def populate_sentiment():
    """
    Populate sentiment_records table by aggregating sentiment from news articles.
    For each (date, ticker) pair, calculate the average confidence score.
    """
    db_service = DatabaseService()
    db_service.populate_sentiment()
    logging.info("Sentiment population endpoint called.")
    return ["Sentiment records populated successfully."]

@router.post("/populate_correlation")
def populate_correlation():
    """
    Populate correlation_records table by calculating correlation between
    sentiment changes and price changes for each ticker.
    """
    db_service = DatabaseService()
    db_service.populate_correlation()
    logging.info("Correlation population endpoint called.")
    return ["Correlation records populated successfully."]