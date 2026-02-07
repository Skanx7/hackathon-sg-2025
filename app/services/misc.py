import re
import time
from collections import deque
from datetime import timedelta
from typing import Optional

class RateLimiter:
    """Simple rate limiter to manage API request timing"""
    
    def __init__(self, calls_limit: int, period_seconds: float):
        self.calls_limit = calls_limit
        self.period_seconds = period_seconds
        self.timestamps = deque(maxlen=calls_limit)
    
    def wait_if_needed(self):
        """Wait if we've hit the rate limit"""
        now = time.time()
        
        # If we haven't made enough requests yet, no need to wait
        if len(self.timestamps) < self.calls_limit:
            self.timestamps.append(now)
            return
            
        # Check if oldest request is outside our time window
        elapsed = now - self.timestamps[0]
        if elapsed < self.period_seconds:
            # Need to wait until oldest request is outside window
            wait_time = self.period_seconds - elapsed
            time.sleep(wait_time)
        
        # Add current timestamp and remove oldest if at limit
        self.timestamps.append(time.time())


def clean_text(s: Optional[str]) -> str:
    """Clean text by removing extra whitespace"""
    if not s:
        return ""
    return re.sub(r"\s+", " ", s.strip())


def clean_company_name(name: Optional[str]) -> str:
    """Clean company name by removing specific corporate suffixes for better search results"""
    if not name:
        return ""
    
    # Remove specific words that interfere with search
    words_to_remove = [
        r'\bSE\b',       # Societas Europaea
        r'\bNV\b',       # Naamloze vennootschap
        r'\bGROUPE\b',   # French for Group
        r'\bSA\b',       # Société Anonyme
        r'\bSCIENT\.',   # Scientific abbreviation (period is not a word char, so no \b needed after)
        r'\bINTL\b',     # International
        r'\bACT\.A\b'    # Action A shares
    ]
    
    cleaned_name = name
    for word in words_to_remove:
        cleaned_name = re.sub(word, '', cleaned_name, flags=re.IGNORECASE)
    
    # Clean up extra whitespace that may result from removal
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name.strip())
    
    return cleaned_name


# Define common rate limits as constants
REDDIT_RATE_LIMIT = {
    "calls": 100,
    "period": timedelta(minutes=1).total_seconds()
}

NEWSAPI_RATE_LIMIT = {
    "calls": 100,
    "period": timedelta(days=1).total_seconds()
}

POLYGON_RATE_LIMIT = {
    "calls": 5,
    "period": timedelta(minutes=1).total_seconds()
}