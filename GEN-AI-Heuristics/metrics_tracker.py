"""
MetricsTracker module for tracking crawl execution metrics.

This module provides dataclasses and a tracker class for monitoring:
- Crawl metrics (pages requested, crawled, skipped)
- Token metrics (input/output tokens, API calls, costs)
- Time metrics (session duration)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


# Model pricing configuration (per 1K tokens)
MODEL_PRICING = {
    "gpt-4o": {
        "input": 0.005,      # $5.00 per 1M tokens
        "output": 0.015,     # $15.00 per 1M tokens
        "description": "Most capable model, higher cost"
    },
    "gpt-4o-mini": {
        "input": 0.00015,    # $0.15 per 1M tokens
        "output": 0.0006,    # $0.60 per 1M tokens
        "description": "Cost-effective model, good for most evaluations"
    }
}


@dataclass
class CrawlMetrics:
    """Metrics related to page crawling.
    
    Attributes:
        pages_requested: Maximum number of pages requested to crawl
        pages_crawled: Number of pages successfully crawled
        pages_skipped: Number of pages skipped
        skip_reasons: Dictionary mapping skip reason categories to lists of URLs
            Categories: 'navigation_error', 'duplicate', 'domain_mismatch', 
                       'max_limit_reached', 'max_depth_exceeded'
        crawled_urls: List of all successfully crawled URLs
    """
    pages_requested: int = 0
    pages_crawled: int = 0
    pages_skipped: int = 0
    skip_reasons: Dict[str, List[str]] = field(default_factory=dict)
    crawled_urls: List[str] = field(default_factory=list)


@dataclass
class TokenMetrics:
    """Metrics related to LLM token consumption.
    
    Attributes:
        total_input_tokens: Total number of input/prompt tokens consumed
        total_output_tokens: Total number of output/completion tokens consumed
        api_calls: Number of API calls made
    """
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    api_calls: int = 0
    
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens (input + output)."""
        return self.total_input_tokens + self.total_output_tokens
    
    def calculate_cost(self, model: str = "gpt-4o-mini") -> float:
        """Calculate cost based on selected model pricing.
        
        Model pricing (per 1K tokens):
        - GPT-4o: Input $0.005, Output $0.015
        - GPT-4o-mini: Input $0.00015, Output $0.0006
        
        Args:
            model: Model name (default: "gpt-4o-mini")
            
        Returns:
            Estimated cost in USD
        """
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4o-mini"])
        input_cost = (self.total_input_tokens / 1000) * pricing["input"]
        output_cost = (self.total_output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost


@dataclass
class TimeMetrics:
    """Metrics related to execution time.
    
    Attributes:
        start_time: Session start timestamp
        end_time: Session end timestamp
    """
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def elapsed_seconds(self) -> float:
        """Calculate elapsed time in seconds.
        
        Returns:
            Elapsed time in seconds, or 0.0 if session not complete
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    def format_elapsed(self) -> str:
        """Format elapsed time as HH:MM:SS.
        
        Returns:
            Formatted time string in HH:MM:SS format
        """
        seconds = int(self.elapsed_seconds)
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


class MetricsTracker:
    """Central metrics tracking for evaluation sessions.
    
    This class aggregates all metrics (crawl, token, time) and provides
    methods for recording events and generating summaries.
    
    Example:
        tracker = MetricsTracker()
        tracker.start_session()
        tracker.crawl.pages_requested = 10
        tracker.record_page_crawled("https://example.com")
        tracker.record_api_call(input_tokens=100, output_tokens=50)
        tracker.end_session()
        summary = tracker.get_summary()
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize a new MetricsTracker with empty metrics.
        
        Args:
            model: Model name for cost calculation (default: "gpt-4o-mini")
        """
        self.crawl = CrawlMetrics()
        self.tokens = TokenMetrics()
        self.time = TimeMetrics()
        self.model = model
    
    def start_session(self) -> None:
        """Mark session start time."""
        self.time.start_time = datetime.now()
    
    def end_session(self) -> None:
        """Mark session end time."""
        self.time.end_time = datetime.now()
    
    def record_page_crawled(self, url: str) -> None:
        """Record a successfully crawled page.
        
        Args:
            url: The URL of the crawled page
        """
        self.crawl.pages_crawled += 1
        self.crawl.crawled_urls.append(url)
    
    def record_page_skipped(self, url: str, reason: str) -> None:
        """Record a skipped page with reason.
        
        Args:
            url: The URL of the skipped page
            reason: The reason for skipping (e.g., 'duplicate', 'domain_mismatch',
                   'max_limit_reached', 'navigation_error', 'max_depth_exceeded')
        """
        self.crawl.pages_skipped += 1
        if reason not in self.crawl.skip_reasons:
            self.crawl.skip_reasons[reason] = []
        self.crawl.skip_reasons[reason].append(url)
    
    def record_api_call(self, input_tokens: int, output_tokens: int) -> None:
        """Record token usage from an API call.
        
        Args:
            input_tokens: Number of input/prompt tokens used
            output_tokens: Number of output/completion tokens used
        """
        self.tokens.total_input_tokens += input_tokens
        self.tokens.total_output_tokens += output_tokens
        self.tokens.api_calls += 1
    
    def get_summary(self) -> dict:
        """Get complete metrics summary.
        
        Returns:
            Dictionary containing all metrics:
            - elapsed_time: Formatted time string (HH:MM:SS)
            - elapsed_seconds: Raw elapsed seconds
            - pages_requested: Max pages setting
            - pages_crawled: Actually crawled count
            - pages_skipped: Total skipped count
            - skip_reasons: Breakdown by reason category
            - total_input_tokens: Input tokens consumed
            - total_output_tokens: Output tokens consumed
            - total_tokens: Total tokens (input + output)
            - api_calls: Number of API calls
            - estimated_cost_usd: Estimated cost in USD
            - cost_per_page: Cost per page evaluated
            - model_used: Model name used for evaluation
        """
        cost = self.tokens.calculate_cost(model=self.model)
        pages = self.crawl.pages_crawled if self.crawl.pages_crawled > 0 else 1
        return {
            "elapsed_time": self.time.format_elapsed(),
            "elapsed_seconds": self.time.elapsed_seconds,
            "pages_requested": self.crawl.pages_requested,
            "pages_crawled": self.crawl.pages_crawled,
            "pages_skipped": self.crawl.pages_skipped,
            "skip_reasons": self.crawl.skip_reasons,
            "total_input_tokens": self.tokens.total_input_tokens,
            "total_output_tokens": self.tokens.total_output_tokens,
            "total_tokens": self.tokens.total_tokens,
            "api_calls": self.tokens.api_calls,
            "estimated_cost_usd": round(cost, 4),
            "cost_per_page": round(cost / pages, 4),
            "model_used": self.model
        }
