import logging
from typing import List, Dict, Optional
import yfinance as yf
class MetadataScraper:
    @staticmethod
    def get_ticker_metadata(ticker: str) -> Dict:
        """Fetch static company metadata for CAC40 tickers"""
        try:
            t = yf.Ticker(ticker)
            info = t.info

            company = {
                "name": info.get("shortName") or info.get("longName") or ticker,
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "city": info.get("city"),
                "symbol": ticker,
                "address": info.get("address1"),
                "employees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
                "summary": info.get("longBusinessSummary"),
                "logo_url": info.get("logo_url"),
                "currency": info.get("currency")
                }
            return company
        except Exception as e:
            logging.warning(f"Error fetching metadata for {ticker}: {e}")
            return {"symbol": ticker, "error": str(e)}
    @staticmethod
    def get_multiple_tickers_metadata(tickers : List[str]) -> List[Dict]:
        """Fetch metadata for multiple tickers"""
        results = {}
        for ticker in tickers:
            metadata = MetadataScraper.get_ticker_metadata(ticker)
            results[ticker] = metadata
        return results