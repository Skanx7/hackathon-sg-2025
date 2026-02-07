from app.models import *
from .metadata_scraper import MetadataScraper
from .price_scraper import PriceScraper
from .news_scraper import NewsScraper
from app.config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from datetime import datetime, timezone, timedelta, date
from typing import List, Dict, Optional, Union
import logging
import json
import os

from app.models.sql_models import Base, StockPrice, CompanyMetadata, SentimentRecord, CorrelationRecord

class DatabaseService:

    def __init__(self):
        self.session = SessionLocal()

    def populate_sql_metadata(self):
        scraped_metadata = MetadataScraper().get_multiple_tickers_metadata(list(settings.CAC40_TICKERS.keys()))
        for data in scraped_metadata.values():
            if "error" in data:
                continue  # Skip entries with errors
            company_metadata = {
                "symbol": data.get("symbol"),
                "name": data.get("name"),
                "sector": data.get("sector"),
                "industry": data.get("industry"),
                "country": data.get("country"),
                "city": data.get("city"),
                "address": data.get("address"),
                "employees": data.get("employees"),
                "website": data.get("website"),
                "summary": data.get("summary"),
                "logo_url": data.get("logo_url"),
                "currency": data.get("currency")
            }
            company = CompanyMetadata(**company_metadata)
            self.session.merge(company)  # Use merge to avoid duplicates
        self.session.commit()
        logging.info("SQL Metadata population complete.")
    
    def populate_sql_prices(self):
        prices_data = PriceScraper().get_price_data(list(settings.CAC40_TICKERS.keys()))
        for ticker, df in prices_data.items():
            for index, row in df.iterrows():
                stock_price = {
                    "ticker": ticker,
                    "date": index,
                    "open_price": row["Open"],
                    "high_price": row["High"],
                    "low_price": row["Low"],
                    "close_price": row["Close"],
                    "volume": row["Volume"]
                }
                price = StockPrice(**stock_price)
                self.session.merge(price)
        self.session.commit()
        logging.info("SQL Prices population complete.")

    def populate_nosql_newsapi(self, last_n_days: int = 30):
        tickers_data = [{"ticker": t.get("ticker"), "name": t.get("name"), "alternate_ticker": t.get("alternate_ticker")} for t in settings.CAC40_TICKERS.values()]
        news_data = NewsScraper().scrape_newsapi(tickers_data, last_n_days=last_n_days)
        for articles in news_data.get("articles_by_ticker", {}).values():
            if isinstance(articles, dict) and "error" in articles:
                continue  # Skip entries with errors
            for article in articles:
                news_document = NewsDocument.create(
                    ticker=article.get("ticker"),
                    title=article.get("title"),
                    content=article.get("content"),
                    medium="newsapi",
                    source=article.get("source"),
                    description=article.get("description"),
                    url=article.get("url"),
                    published_at=article.get("published_at"),
                )
                logging.info(f"Inserting article for ticker {article.get('ticker')}: {article.get('title')}")
                news_collection.insert_one(news_document)
        logging.info("NoSQL NewsAPI population complete.")

    def populate_nosql_polygon(self, start_date: date, limit: int = 1000, end_date: Optional[date] = None):
        logging.info(type(start_date))
        logging.info(f"Polygon start_date resolved to: {start_date}")
        if end_date is None:
            end_date = date.today()

        tickers = list(settings.CAC40_TICKERS.keys())
        news_data = NewsScraper().scrape_polygon(tickers, start_date, end_date=end_date, limit=limit)
        for articles in news_data.get("articles_by_ticker", {}).values():
            if isinstance(articles, dict) and "error" in articles:
                continue  # Skip entries with errors
            for article in articles:
                news_document= NewsDocument.create(
                    ticker=article.get("ticker"),
                    title=article.get("title"),
                    content=article.get("content"),
                    medium="polygon",
                    source=article.get("source"),
                    description=article.get("description"),
                    url=article.get("url"),
                    published_at=article.get("published_at"),
                )
                news_collection.insert_one(news_document)
        logging.info("NoSQL Polygon population complete.")
            
    def populate_nosql_reddit(self, last_n_days: int = 30, subreddits: Optional[List[str]] = None):
        tickers_data = [{"ticker": t.get("ticker"), "name": t.get("name"), "alternate_ticker": t.get("alternate_ticker")} for t in settings.CAC40_TICKERS.values()]
        news_data = NewsScraper().scrape_reddit(tickers_data, last_n_days=last_n_days, subreddits=subreddits)
        for articles in news_data.get("articles_by_ticker", {}).values():
            if isinstance(articles, dict) and "error" in articles:
                continue  # Skip entries with errors
            for article in articles:
                news_data = NewsDocument.create(
                    ticker=article.get("ticker"),
                    title=article.get("title"),
                    content=article.get("content"),
                    medium="reddit",
                    source=article.get("source"),
                    description=article.get("description"),
                    url=article.get("url"),
                    published_at=article.get("published_at"),
                )
                news_collection.insert_one(news_data)
        logging.info("NoSQL Reddit population complete.")

    def populate_sentiment(self):
        """
        Populate the sentiment_records table by aggregating sentiment from news articles.
        For each (date, ticker) pair, calculate the average confidence score from all articles
        published on that date for that ticker.
        """
        if news_collection is None:
            logging.error("MongoDB news collection is not available.")
            return
        
        # Query all news articles that have sentiment data
        query = {"sentiment.confidence": {"$exists": True, "$ne": None}}
        articles = list(news_collection.find(query))
        
        if not articles:
            logging.warning("No articles with sentiment data found.")
            return
        
        # Group articles by (date, ticker)
        sentiment_by_date_ticker = {}
        for article in articles:
            ticker = article.get("ticker")
            published_at = article.get("published_at")
            confidence = article.get("sentiment", {}).get("confidence")
            news_id = str(article.get("_id"))
            
            if not ticker or not published_at or confidence is None:
                continue
            
            # Extract just the date part
            if isinstance(published_at, str):
                article_date = datetime.fromisoformat(published_at).date()
            else:
                article_date = published_at.date()
            
            key = (article_date, ticker)
            if key not in sentiment_by_date_ticker:
                sentiment_by_date_ticker[key] = {
                    "confidences": [],
                    "news_ids": []
                }
            
            sentiment_by_date_ticker[key]["confidences"].append(confidence)
            sentiment_by_date_ticker[key]["news_ids"].append(news_id)
        
        # Calculate average confidence for each (date, ticker) and insert into SQL
        for (article_date, ticker), data in sentiment_by_date_ticker.items():
            avg_confidence = sum(data["confidences"]) / len(data["confidences"])
            
            # Use the first news_id as a representative (or could concatenate all)
            news_id = data["news_ids"][0] if data["news_ids"] else "unknown"
            
            sentiment_record = SentimentRecord(
                ticker=ticker,
                date=article_date,
                sentiment_score=avg_confidence,
                news_id=news_id
            )
            
            # Use merge to avoid duplicates based on ticker and date
            existing = self.session.query(SentimentRecord).filter_by(
                ticker=ticker,
                date=article_date
            ).first()
            
            if existing:
                existing.sentiment_score = avg_confidence
                existing.news_id = news_id
            else:
                self.session.add(sentiment_record)
        
        self.session.commit()
        logging.info(f"Sentiment population complete. Processed {len(sentiment_by_date_ticker)} unique (date, ticker) pairs.")

    def populate_correlation(self):
        """
        Populate the correlation_records table by calculating correlation between
        sentiment changes and price changes for each ticker.
        """
        # Get all unique tickers from sentiment records
        tickers = self.session.query(SentimentRecord.ticker).distinct().all()
        tickers = [t[0] for t in tickers]
        
        for ticker in tickers:
            # Get sentiment data ordered by date
            sentiment_data = self.session.query(SentimentRecord).filter_by(
                ticker=ticker
            ).order_by(SentimentRecord.date).all()
            
            # Get price data ordered by date
            price_data = self.session.query(StockPrice).filter_by(
                ticker=ticker
            ).order_by(StockPrice.date).all()
            
            if len(sentiment_data) < 2 or len(price_data) < 2:
                logging.warning(f"Not enough data for ticker {ticker} to calculate correlation.")
                continue
            
            # Create dictionaries for easy lookup
            sentiment_dict = {record.date: record.sentiment_score for record in sentiment_data}
            price_dict = {record.date: record.close_price for record in price_data}
            
            # Find common dates and calculate changes
            common_dates = sorted(set(sentiment_dict.keys()) & set(price_dict.keys()))
            
            if len(common_dates) < 2:
                logging.warning(f"Not enough common dates for ticker {ticker} to calculate correlation.")
                continue
            
            # Calculate changes for dates where we have both sentiment and price
            sentiment_changes = []
            price_changes = []
            correlation_dates = []
            
            for i in range(1, len(common_dates)):
                prev_date = common_dates[i - 1]
                curr_date = common_dates[i]
                
                sentiment_change = sentiment_dict[curr_date] - sentiment_dict[prev_date]
                
                # Avoid division by zero
                if price_dict[prev_date] == 0:
                    continue
                    
                price_change = (price_dict[curr_date] - price_dict[prev_date]) / price_dict[prev_date]
                
                sentiment_changes.append(sentiment_change)
                price_changes.append(price_change)
                correlation_dates.append(curr_date)
            
            # Calculate correlation coefficient
            if len(sentiment_changes) < 2 or not correlation_dates:
                logging.warning(f"Not enough valid data points for ticker {ticker} to calculate correlation.")
                continue
            
            # Simple Pearson correlation
            n = len(sentiment_changes)
            sum_x = sum(sentiment_changes)
            sum_y = sum(price_changes)
            sum_xy = sum(x * y for x, y in zip(sentiment_changes, price_changes))
            sum_x2 = sum(x * x for x in sentiment_changes)
            sum_y2 = sum(y * y for y in price_changes)
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator_x = (n * sum_x2 - sum_x * sum_x) ** 0.5
            denominator_y = (n * sum_y2 - sum_y * sum_y) ** 0.5
            
            if denominator_x == 0 or denominator_y == 0:
                correlation = 0.0
            else:
                correlation = numerator / (denominator_x * denominator_y)
            
            # Store correlation with the most recent date in the analysis
            # This represents the correlation calculated using all available data up to this date
            # Note: common_dates is guaranteed to have at least 2 elements due to earlier check
            latest_date = correlation_dates[-1] if correlation_dates else common_dates[-1]
            
            correlation_record = CorrelationRecord(
                ticker=ticker,
                date=latest_date,
                correlation_coefficient=correlation
            )
            
            # Use merge to avoid duplicates
            existing = self.session.query(CorrelationRecord).filter_by(
                ticker=ticker,
                date=latest_date
            ).first()
            
            if existing:
                existing.correlation_coefficient = correlation
            else:
                self.session.add(correlation_record)
        
        self.session.commit()
        logging.info(f"Correlation population complete for {len(tickers)} tickers.")
    def populate_sql(self):
        try:
            self.populate_sql_metadata()
            self.populate_sql_prices()
            logging.info("SQL database population complete.")
        except Exception as e:
            logging.error(f"Error populating SQL database: {e}")
            self.session.rollback()
    def populate_nosql(self, last_n_days: int = 600, subreddits: Optional[List[str]] = None):
        try:
            self.populate_nosql_newsapi(last_n_days=last_n_days)
            start_date = datetime.now(timezone.utc) - timedelta(days=last_n_days)
            self.populate_nosql_polygon(start_date=start_date, limit=1000)
            self.populate_nosql_reddit(last_n_days=last_n_days, subreddits=subreddits)
            logging.info("NoSQL database population complete.")

        except Exception as e:
            logging.error(f"Error populating NoSQL database: {e}")

    def backup_sql(self, backup_url:  Optional[str] = None):
        backup_uri = backup_url or settings.SQLITE_URL
        sqlite_engine = create_engine(backup_uri)
        Base.metadata.create_all(sqlite_engine)

        with Session(self.session.bind) as source_session:
            with Session(sqlite_engine) as target_session:
                companies = source_session.query(CompanyMetadata).all()
                for c in companies:
                    target_session.merge(CompanyMetadata(**{col.name: getattr(c, col.name) for col in CompanyMetadata.__table__.columns}))

                # Copy StockPrice
                prices = source_session.query(StockPrice).all()
                for p in prices:
                    target_session.merge(StockPrice(**{col.name: getattr(p, col.name) for col in StockPrice.__table__.columns}))

                target_session.commit()

    def export_nosql(self, output_dir: Optional[str] = None):
        """Export MongoDB database to JSON files"""
        if output_dir is None:
            output_dir = "/tmp/mongodb_dump"
        
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            db_name = settings.MONGODB_DB
            logging.info(f"Starting MongoDB export to {output_dir} for database {db_name}")
            
            # Export each collection to a separate JSON file
            collections_exported = []
            
            # Export news collection
            if news_collection is not None:
                news_docs = list(news_collection.find())
                # Convert ObjectId and datetime objects to strings for JSON serialization
                for doc in news_docs:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    # Convert datetime objects to ISO format strings
                    for key, value in doc.items():
                        if isinstance(value, datetime):
                            doc[key] = value.isoformat()
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if isinstance(subvalue, datetime):
                                    doc[key][subkey] = subvalue.isoformat()
                
                news_file = os.path.join(output_dir, "news.json")
                with open(news_file, 'w', encoding='utf-8') as f:
                    json.dump(news_docs, f, ensure_ascii=False, indent=2)
                collections_exported.append(f"news ({len(news_docs)} documents)")
                logging.info(f"Exported {len(news_docs)} documents from news collection")
            
            # Export company collection
            if company_collection is not None:
                company_docs = list(company_collection.find())
                # Convert ObjectId and datetime objects to strings for JSON serialization
                for doc in company_docs:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    for key, value in doc.items():
                        if isinstance(value, datetime):
                            doc[key] = value.isoformat()
                
                company_file = os.path.join(output_dir, "companies.json")
                with open(company_file, 'w', encoding='utf-8') as f:
                    json.dump(company_docs, f, ensure_ascii=False, indent=2)
                collections_exported.append(f"companies ({len(company_docs)} documents)")
                logging.info(f"Exported {len(company_docs)} documents from companies collection")
            
            message = f"NoSQL database exported successfully: {', '.join(collections_exported)}"
            logging.info(f"MongoDB export completed successfully to {output_dir}")
            
            return {
                "status": "success",
                "output_dir": output_dir,
                "collections": collections_exported,
                "message": message
            }
        
        except Exception as e:
            error_msg = f"Error during MongoDB export: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def import_nosql(self, input_dir: Optional[str] = None):
        """Import MongoDB database from JSON files"""
        if input_dir is None:
            input_dir = "/tmp/mongodb_dump"
        
        try:
            # Check if input directory exists
            if not os.path.exists(input_dir):
                raise FileNotFoundError(f"Import directory not found: {input_dir}")
            
            db_name = settings.MONGODB_DB
            logging.info(f"Starting MongoDB import from {input_dir} for database {db_name}")
            
            collections_imported = []
            
            # Import news collection
            news_file = os.path.join(input_dir, "news.json")
            if os.path.exists(news_file) and news_collection is not None:
                with open(news_file, 'r', encoding='utf-8') as f:
                    news_docs = json.load(f)
                
                # Convert ISO format strings back to datetime objects
                for doc in news_docs:
                    # Remove _id to let MongoDB generate new ones or use existing
                    if '_id' in doc:
                        del doc['_id']
                    
                    # Convert string dates back to datetime objects
                    if 'published_at' in doc and isinstance(doc['published_at'], str):
                        doc['published_at'] = datetime.fromisoformat(doc['published_at'])
                    if 'created_at' in doc and isinstance(doc['created_at'], str):
                        doc['created_at'] = datetime.fromisoformat(doc['created_at'])
                    
                    # Handle nested sentiment dates
                    if 'sentiment' in doc and isinstance(doc['sentiment'], dict):
                        if 'updated_at' in doc['sentiment'] and isinstance(doc['sentiment']['updated_at'], str):
                            doc['sentiment']['updated_at'] = datetime.fromisoformat(doc['sentiment']['updated_at'])
                
                # Drop existing collection and insert new data
                news_collection.drop()
                if news_docs:
                    news_collection.insert_many(news_docs)
                collections_imported.append(f"news ({len(news_docs)} documents)")
                logging.info(f"Imported {len(news_docs)} documents to news collection")
            
            # Import company collection
            company_file = os.path.join(input_dir, "companies.json")
            if os.path.exists(company_file) and company_collection is not None:
                with open(company_file, 'r', encoding='utf-8') as f:
                    company_docs = json.load(f)
                
                # Convert ISO format strings back to datetime objects
                for doc in company_docs:
                    # Remove _id to let MongoDB generate new ones
                    if '_id' in doc:
                        del doc['_id']
                    
                    if 'created_at' in doc and isinstance(doc['created_at'], str):
                        doc['created_at'] = datetime.fromisoformat(doc['created_at'])
                    if 'updated_at' in doc and isinstance(doc['updated_at'], str):
                        doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
                
                # Drop existing collection and insert new data
                company_collection.drop()
                if company_docs:
                    company_collection.insert_many(company_docs)
                collections_imported.append(f"companies ({len(company_docs)} documents)")
                logging.info(f"Imported {len(company_docs)} documents to companies collection")
            
            message = f"NoSQL database imported successfully: {', '.join(collections_imported)}"
            logging.info(f"MongoDB import completed successfully from {input_dir}")
            
            return {
                "status": "success",
                "input_dir": input_dir,
                "collections": collections_imported,
                "message": message
            }
        
        except FileNotFoundError as e:
            logging.error(str(e))
            raise
        except Exception as e:
            error_msg = f"Error during MongoDB import: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

    def close(self):
        self.session.close()

        