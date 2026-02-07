import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
class PriceScraper:
    VALID_INTERVALS = ["1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"]
    def get_price_data(self, ticker_list: List[str], interval: str = "1d", start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch historical price data for a given ticker symbol.

        Args:
            ticker (str): The stock ticker symbol.
            start_date (str): The start date for the data (YYYY-MM-DD).
            end_date (str): The end date for the data (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing the historical price data.
        """
        if interval not in self.VALID_INTERVALS:
            interval = "1d"  # Default to daily if invalid interval provided
        if start_date is None:
            start_date = "2000-01-01"
        df = yf.download(ticker_list, start=start_date, end=end_date, auto_adjust=True, interval=interval)
        price_data = {ticker: df.xs(ticker, level=1, axis=1) for ticker in ticker_list}
        return price_data
    


