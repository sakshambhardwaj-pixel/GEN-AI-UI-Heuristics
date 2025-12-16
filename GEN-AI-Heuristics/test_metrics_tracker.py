"""
Property-based tests for MetricsTracker module.

This module contains property-based tests using Hypothesis to verify
the correctness properties defined in the design document.
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
import re

from metrics_tracker import (
    CrawlMetrics,
    TokenMetrics,
    TimeMetrics,
    MetricsTracker,
)


# **Feature: crawl-metrics-improvements, Property 3: Time Tracking Consistency**
# **Validates: Requirements 3.1, 3.2, 3.3**
class TestTimeTrackingConsistency:
    """
    Property 3: Time Tracking Consistency
    
    *For any* evaluation session with start time S and end time E (where E > S),
    the elapsed_seconds property SHALL equal (E - S).total_seconds() and
    format_elapsed() SHALL return a string in HH:MM:SS format.
    """

    @settings(max_examples=100)
    @given(
        start_offset_seconds=st.integers(min_value=0, max_value=86400 * 365),  # Up to 1 year
        duration_seconds=st.integers(min_value=0, max_value=86400 * 7)  # Up to 1 week duration
    )
    def test_elapsed_seconds_equals_time_difference(self, start_offset_seconds, duration_seconds):
        """
        Property: elapsed_seconds SHALL equal (end_time - start_time).total_seconds()
        
        **Feature: crawl-metrics-improvements, Property 3: Time Tracking Consistency**
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        base_time = datetime(2024, 1, 1, 0, 0, 0)
        start_time = base_time + timedelta(seconds=start_offset_seconds)
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        time_metrics = TimeMetrics(start_time=start_time, end_time=end_time)
        
        expected_elapsed = (end_time - start_time).total_seconds()
        actual_elapsed = time_metrics.elapsed_seconds
        
        assert actual_elapsed == expected_elapsed, (
            f"elapsed_seconds mismatch: expected {expected_elapsed}, got {actual_elapsed}"
        )

    @settings(max_examples=100)
    @given(
        duration_seconds=st.integers(min_value=0, max_value=86400 * 7)  # Up to 1 week
    )
    def test_format_elapsed_returns_valid_hhmmss_format(self, duration_seconds):
        """
        Property: format_elapsed() SHALL return a string in HH:MM:SS format
        
        **Feature: crawl-metrics-improvements, Property 3: Time Tracking Consistency**
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        time_metrics = TimeMetrics(start_time=start_time, end_time=end_time)
        formatted = time_metrics.format_elapsed()
        
        # Verify HH:MM:SS format using regex
        pattern = r'^\d{2,}:\d{2}:\d{2}$'
        assert re.match(pattern, formatted), (
            f"format_elapsed() returned '{formatted}' which doesn't match HH:MM:SS format"
        )

    @settings(max_examples=100)
    @given(
        hours=st.integers(min_value=0, max_value=999),
        minutes=st.integers(min_value=0, max_value=59),
        seconds=st.integers(min_value=0, max_value=59)
    )
    def test_format_elapsed_correctly_represents_duration(self, hours, minutes, seconds):
        """
        Property: format_elapsed() SHALL correctly represent the duration components
        
        **Feature: crawl-metrics-improvements, Property 3: Time Tracking Consistency**
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        total_seconds = hours * 3600 + minutes * 60 + seconds
        
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = start_time + timedelta(seconds=total_seconds)
        
        time_metrics = TimeMetrics(start_time=start_time, end_time=end_time)
        formatted = time_metrics.format_elapsed()
        
        # Parse the formatted string
        parts = formatted.split(':')
        parsed_hours = int(parts[0])
        parsed_minutes = int(parts[1])
        parsed_seconds = int(parts[2])
        
        assert parsed_hours == hours, f"Hours mismatch: expected {hours}, got {parsed_hours}"
        assert parsed_minutes == minutes, f"Minutes mismatch: expected {minutes}, got {parsed_minutes}"
        assert parsed_seconds == seconds, f"Seconds mismatch: expected {seconds}, got {parsed_seconds}"

    def test_elapsed_seconds_returns_zero_when_incomplete(self):
        """
        Property: elapsed_seconds SHALL return 0.0 if session not complete
        
        **Feature: crawl-metrics-improvements, Property 3: Time Tracking Consistency**
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        # No start or end time
        time_metrics = TimeMetrics()
        assert time_metrics.elapsed_seconds == 0.0
        
        # Only start time
        time_metrics = TimeMetrics(start_time=datetime.now())
        assert time_metrics.elapsed_seconds == 0.0
        
        # Only end time
        time_metrics = TimeMetrics(end_time=datetime.now())
        assert time_metrics.elapsed_seconds == 0.0

    @settings(max_examples=100)
    @given(
        duration_seconds=st.integers(min_value=0, max_value=86400 * 7)
    )
    def test_metrics_tracker_session_time_consistency(self, duration_seconds):
        """
        Property: MetricsTracker session methods SHALL maintain time consistency
        
        **Feature: crawl-metrics-improvements, Property 3: Time Tracking Consistency**
        **Validates: Requirements 3.1, 3.2, 3.3**
        """
        tracker = MetricsTracker()
        
        # Manually set times to test consistency
        start_time = datetime(2024, 1, 1, 0, 0, 0)
        end_time = start_time + timedelta(seconds=duration_seconds)
        
        tracker.time.start_time = start_time
        tracker.time.end_time = end_time
        
        summary = tracker.get_summary()
        
        expected_elapsed = float(duration_seconds)
        assert summary["elapsed_seconds"] == expected_elapsed, (
            f"Summary elapsed_seconds mismatch: expected {expected_elapsed}, got {summary['elapsed_seconds']}"
        )
        
        # Verify format is included in summary
        assert "elapsed_time" in summary
        assert re.match(r'^\d{2,}:\d{2}:\d{2}$', summary["elapsed_time"])
