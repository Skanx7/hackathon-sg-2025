from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from app.config import settings
import logging
server_engine = create_engine(
    f"{settings.SQL_URL}"
)
with server_engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.SQL_DB};"))
    logging.info(f"Ensured database '{settings.SQL_DB}' exists.")

engine = create_engine(
    f"{settings.SQL_URL}/{settings.SQL_DB}"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class StockPrice(Base):
    __tablename__ = "stock_prices"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float, nullable=False)
    volume = Column(Float)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class CompanyMetadata(Base):
    __tablename__ = "company_metadata"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(255))
    sector = Column(String(255))
    industry = Column(String(255))
    country = Column(String(128))
    city = Column(String(128))
    address = Column(String(255))
    employees = Column(Integer)
    website = Column(String(255))
    summary = Column(String(1000))
    logo_url = Column(String(255))
    currency = Column(String(16))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))


class SentimentRecord(Base):
    __tablename__ = "sentiment_records"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    sentiment_score = Column(Float, nullable=False)
    news_id = Column(String(64), nullable=False)

class CorrelationRecord(Base):
    __tablename__ = "correlation_records"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(32), index=True, nullable=False)
    date = Column(Date, index=True, nullable=False)
    correlation_coefficient = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

