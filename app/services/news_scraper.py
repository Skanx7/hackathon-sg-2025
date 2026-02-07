from app.config import settings
from app.services.misc import RateLimiter, clean_text, clean_company_name, REDDIT_RATE_LIMIT, NEWSAPI_RATE_LIMIT, POLYGON_RATE_LIMIT

import requests
import logging
import praw
from datetime import datetime, timezone, timedelta, date
from typing import List, Dict, Optional, Union

class NewsScraper:
    """News scraper for Reddit, NewsAPI and Polygon"""
    
    # Default subreddits to scrape
    SUBREDDITS_TO_SCRAPE = [
        # French subreddits
        "Bourse", "Investir", "FinanceFR", "Economie", "FranceFinance", 
        # English/Global subreddits
        "stocks", "investing", "StockMarket", "Economy", "FinancialNews", 
        "ValueInvesting", "WallStreetBets", "Dividends", "GlobalMarkets", 
        "Finance", "Business", "GlobalMarketNews", "StockMarketDiscussion",
        "StockMarketNews", "algotrading", "Robinhood", "Daytrading", 
        "pennystocks", "interactivebrokers", "trading212", "DEGIRO", "XTB", "Etoro"
    ]
    
    def __init__(self):
        # Initialize rate limiters
        self.reddit_limiter = RateLimiter(
            calls_limit=REDDIT_RATE_LIMIT["calls"],
            period_seconds=REDDIT_RATE_LIMIT["period"]
        )
        self.newsapi_limiter = RateLimiter(
            calls_limit=NEWSAPI_RATE_LIMIT["calls"],
            period_seconds=NEWSAPI_RATE_LIMIT["period"]
        )
        self.polygon_limiter = RateLimiter(
            calls_limit=POLYGON_RATE_LIMIT["calls"],
            period_seconds=POLYGON_RATE_LIMIT["period"]
        )

        # Configure Reddit client
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT,
            ratelimit_seconds=5,
            check_for_async=False
        )
        
        # API URLs and keys
        self.news_api_url = settings.NEWS_API_URL
        self.news_api_key = settings.NEWS_API_KEY
        self.polygon_api_url = settings.POLYGON_API_URL
        self.polygon_api_key = settings.POLYGON_API_KEY

    def _make_api_request(self, url: str, params: Dict, headers: Dict = None, 
                         rate_limiter: RateLimiter = None) -> Dict:
        """Make an API request with rate limiting and error handling"""
        if rate_limiter:
            rate_limiter.wait_if_needed()
            
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"API request failed: {url} - {str(e)}")
            return {"error": str(e)}

    def scrape_reddit_single(self, 
                            ticker_data: dict, 
                            last_n_days: int = 30, 
                            subreddits: Optional[List[str]] = None) -> List[Dict]:
        """Scrape Reddit for a single ticker"""
        subs = subreddits or self.SUBREDDITS_TO_SCRAPE
        min_ts = datetime.now(timezone.utc) - timedelta(days=max(1, last_n_days))
        
        # Use only the company name, cleaned of corporate suffixes
        company_name = ticker_data.get("name", "")
        if not company_name:
            logging.warning(f"No company name found for ticker {ticker_data.get('ticker')}")
            return []
        
        # Clean the company name for better search results
        search_term = clean_company_name(company_name)
        if not search_term:
            logging.warning(f"Company name became empty after cleaning for ticker {ticker_data.get('ticker')}")
            search_term = company_name  # Fall back to original name
        
        logging.info(f"Searching Reddit for: '{search_term}' (original: '{company_name}')")

        rows, seen_ids, seen_urls = [], set(), set()

        for sub in subs:
            try:
                # Apply rate limiter before each subreddit search
                self.reddit_limiter.wait_if_needed()
                
                logging.debug(f"Searching r/{sub} for '{search_term}'")
                
                for post in self.reddit.subreddit(sub).search(search_term, sort="new"):
                    created = datetime.fromtimestamp(post.created_utc, tz=timezone.utc)
                    if created < min_ts:
                        continue

                    pid, url = f"t3_{post.id}", getattr(post, "url", None)
                    if pid in seen_ids or (url and url in seen_urls):
                        continue

                    rows.append({
                        "company": company_name,
                        "subreddit": sub,
                        "created_utc": created,
                        "id": pid,
                        "title": clean_text(post.title),  # Using imported clean_text function
                        "text": clean_text(post.selftext),
                        "url": url
                    })
                    seen_ids.add(pid)
                    if url:
                        seen_urls.add(url)
                        
                logging.debug(f"Found {len([r for r in rows if r['subreddit'] == sub])} posts in r/{sub}")
            except Exception as e:
                logging.warning(f"Error scraping Reddit for '{search_term}' in subreddit '{sub}': {e}")
                continue

        if not rows:
            logging.info(f"No Reddit posts found for '{search_term}'")
            return []

        # Sort and deduplicate results
        rows.sort(key=lambda x: x["created_utc"], reverse=True)
        out, seen = [], set()
        for r in rows:
            key = (r.get("url"), r["id"], r.get("text"))
            if key not in seen:
                seen.add(key)
                out.append(r)
        
        logging.info(f"Scraped {len(out)} unique Reddit posts for '{search_term}'")
        return out

    def scrape_reddit(self, 
                     tickers_data: List[Dict], 
                     last_n_days: int = 30, 
                     subreddits: Optional[List[str]] = None) -> Dict:
        """Scrape Reddit for multiple tickers"""
        results = {
            "total_articles": 0,
            "tickers_processed": [],
            "articles_by_ticker": {}
        }
        
        subs = subreddits or self.SUBREDDITS_TO_SCRAPE
        for ticker_info in tickers_data:
            ticker = ticker_info["ticker"]
            articles = self.scrape_reddit_single(ticker_info, last_n_days=last_n_days, subreddits=subs)
            
            results["total_articles"] += len(articles)
            results["tickers_processed"].append(ticker)
            results["articles_by_ticker"][ticker] = articles
            
        return results

    def scrape_newsapi(self, tickers_data: List[Dict], last_n_days: int = 30) -> Dict:
        """Scrape NewsAPI for ticker information"""
        if not self.news_api_url or not self.news_api_key:
            return {"error": "NEWS_API_URL or NEWS_API_KEY not configured"}

        # NewsAPI free tier allows max 30 days lookback
        last_n_days = max(1, min(last_n_days, 30))
        
        results = {
            "total_articles": 0,
            "tickers_processed": [],
            "articles_by_ticker": {}
        }

        headers = {
            "Authorization": f"Bearer {self.news_api_key}"
        }

        for ticker_info in tickers_data:
            ticker = ticker_info.get("ticker", "")
            company_name = ticker_info.get("name", "")
            alternate_ticker = ticker_info.get("alternate_ticker", "")
            
            query = f"{ticker} OR {company_name}" 
            if alternate_ticker:
                query = f"{ticker} OR {company_name} OR {alternate_ticker}"
                
            params = {
                "q": query,
                "from": (datetime.now(timezone.utc) - timedelta(days=last_n_days)).date().isoformat(),
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": 100,
            }
            
            # Apply rate limiting
            data = self._make_api_request(
                url=self.news_api_url, 
                params=params,
                headers=headers,
                rate_limiter=self.newsapi_limiter
            )
            
            if "error" in data:
                results["articles_by_ticker"][ticker] = {"error": data["error"]}
                continue
                
            articles = data.get("articles", [])
            processed_articles = []
            
            for article in articles:
                processed_article = {
                    "ticker": ticker,
                    "title": clean_text(article.get("title", "")),
                    "source": article.get("source", {}).get("name", "unknown"),
                    "content": clean_text(article.get("content", "")),
                    "description": clean_text(article.get("description", "")),
                    "url": article.get("url", None),
                    "published_at": datetime.fromisoformat(article["publishedAt"].replace("Z", "+00:00"))
                    if "publishedAt" in article else None
                }
                processed_articles.append(processed_article)
            
            # Add the processed articles to results
            results["articles_by_ticker"][ticker] = processed_articles
            results["tickers_processed"].append(ticker)
            results["total_articles"] += len(processed_articles)
            
        return results

    def scrape_polygon(self, 
                      tickers: List[str], 
                      start_date: date, 
                      end_date: Optional[date] = None, 
                      limit: int = 1000) -> Dict:
        """Scrape Polygon.io API for news"""
        results = {
            "total_articles": 0,
            "tickers_processed": [],
            "articles_by_ticker": {}
        }
        if not self.polygon_api_url or not self.polygon_api_key:
            return {"error": "POLYGON_API_URL or POLYGON_API_KEY not configured"}
            
        headers = {
            "Authorization": f"Bearer {self.polygon_api_key}"
        }

        end_date = end_date or date.today()

        for ticker in tickers:
            params = {
                "ticker": ticker,
                "published_utc.gte": start_date.isoformat(),
                "published_utc.lte": end_date.isoformat(),
                "sort": "published_utc",
                "order": "desc",
                "limit": min(1000, limit),
            }
            
            # Apply rate limiting
            data = self._make_api_request(
                url=self.polygon_api_url,
                params=params,
                headers=headers,
                rate_limiter=self.polygon_limiter
            )
            
            if "error" in data:
                results["articles_by_ticker"][ticker] = {"error": data["error"]}
                continue
            
            articles = data.get("results", [])
            processed_articles = []
            
            for article in articles:
                insights = article.get("insights", [])
                matching_insight = next(
                    (insight for insight in insights if insight.get("ticker") == ticker), 
                    None
                ) 

                processed_article = {
                    "ticker": ticker,
                    "title": clean_text(article.get("title", "")),
                    "source": article.get("publisher", {}).get("homepage_url", "unknown"),
                    "content": clean_text(article.get("description", "")),
                    "description": clean_text(matching_insight.get("sentiment_reasoning", "")) if matching_insight else "",
                    "url": article.get("url", None),
                    "keywords": matching_insight.get("keywords", []) if matching_insight else [],
                    "published_at": datetime.fromisoformat(article["published_utc"].replace("Z", "+00:00"))
                    if "published_utc" in article else None
                }
                processed_articles.append(processed_article)

            results["articles_by_ticker"][ticker] = processed_articles
            results["tickers_processed"].append(ticker)
            results["total_articles"] += len(processed_articles)

        return results