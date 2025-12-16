"""
Internal Analysis Report Generator for detailed Excel reports.

This module generates comprehensive internal reports containing:
- Summary metrics
- All URLs (crawled and skipped)
- Cost breakdown
- Heuristic scores
"""

import pandas as pd
from io import BytesIO
from typing import Dict, Any
from metrics_tracker import MetricsTracker


class InternalReportGenerator:
    """Generates detailed internal analysis reports in Excel format."""
    
    def __init__(self, metrics: MetricsTracker, analysis_json: dict):
        """Initialize the report generator.
        
        Args:
            metrics: MetricsTracker instance with session data
            analysis_json: Dictionary containing heuristic analysis results
        """
        self.metrics = metrics
        self.analysis_json = analysis_json
        self.model = metrics.model
    
    def generate_excel_report(self, site_name: str = "Website") -> BytesIO:
        """Generate comprehensive Excel report for internal use.
        
        Args:
            site_name: Name of the evaluated site
            
        Returns:
            BytesIO object containing the Excel file
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Executive Summary
            summary_df = self._create_summary_sheet(site_name)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 2: All URLs (crawled + skipped)
            urls_df = self._create_urls_sheet()
            urls_df.to_excel(writer, sheet_name='All URLs', index=False)
            
            # Sheet 3: Cost Breakdown
            cost_df = self._create_cost_breakdown_sheet()
            cost_df.to_excel(writer, sheet_name='Cost Breakdown', index=False)
            
            # Sheet 4: Heuristic Scores
            scores_df = self._create_scores_sheet()
            scores_df.to_excel(writer, sheet_name='Heuristic Scores', index=False)
        
        output.seek(0)
        return output
    
    def _create_summary_sheet(self, site_name: str) -> pd.DataFrame:
        """Create summary metrics sheet.
        
        Args:
            site_name: Name of the evaluated site
            
        Returns:
            DataFrame with summary metrics
        """
        summary = self.metrics.get_summary()
        max_depth = len(summary.get("skip_reasons", {}).get("max_depth_exceeded", []))
        
        summary_data = {
            "Site Name": [site_name],
            "Model Used": [self.model],
            "Elapsed Time": [summary["elapsed_time"]],
            "Pages Requested": [summary["pages_requested"]],
            "Pages Crawled": [summary["pages_crawled"]],
            "Pages Skipped": [summary["pages_skipped"]],
            "Max Depth": [max_depth],
            "Total Tokens": [summary["total_tokens"]],
            "Input Tokens": [summary["total_input_tokens"]],
            "Output Tokens": [summary["total_output_tokens"]],
            "Estimated Cost (USD)": [summary["estimated_cost_usd"]],
            "Cost Per Page": [summary["cost_per_page"]],
            "API Calls": [summary["api_calls"]]
        }
        
        return pd.DataFrame(summary_data)
    
    def _create_urls_sheet(self) -> pd.DataFrame:
        """Create sheet with all URLs including hidden/nested.
        
        Returns:
            DataFrame with all URLs and their status
        """
        urls_data = []
        
        # Add crawled URLs
        for url in self.metrics.crawl.crawled_urls:
            urls_data.append({
                "URL": url,
                "Status": "Crawled",
                "Reason": ""
            })
        
        # Add skipped URLs with reasons
        for reason, urls in self.metrics.crawl.skip_reasons.items():
            for url in urls:
                urls_data.append({
                    "URL": url,
                    "Status": "Skipped",
                    "Reason": reason
                })
        
        # If no data, add a placeholder
        if not urls_data:
            urls_data.append({
                "URL": "No URLs tracked",
                "Status": "N/A",
                "Reason": "No crawling performed"
            })
        
        return pd.DataFrame(urls_data)
    
    def _create_cost_breakdown_sheet(self) -> pd.DataFrame:
        """Create sheet with cost breakdown.
        
        Returns:
            DataFrame with cost breakdown details
        """
        summary = self.metrics.get_summary()
        
        cost_data = {
            "Metric": [
                "Input Tokens",
                "Output Tokens",
                "Total Tokens",
                "Total Cost (USD)",
                "Cost Per Page",
                "Tokens Per Page",
                "API Calls"
            ],
            "Value": [
                summary["total_input_tokens"],
                summary["total_output_tokens"],
                summary["total_tokens"],
                summary["estimated_cost_usd"],
                summary["cost_per_page"],
                round(summary["total_tokens"] / max(summary["pages_crawled"], 1), 2),
                summary["api_calls"]
            ]
        }
        
        return pd.DataFrame(cost_data)
    
    def _create_scores_sheet(self) -> pd.DataFrame:
        """Create sheet with heuristic scores.
        
        Returns:
            DataFrame with heuristic scores and grades
        """
        scores_data = []
        
        for heuristic_name, data in self.analysis_json.items():
            scores_data.append({
                "Heuristic": heuristic_name,
                "Score": data.get("total_score", 0),
                "Max Score": data.get("max_score", 4),
                "Grade": data.get("grade", "N/A"),
                "Performance Level": data.get("performance_level", "N/A"),
                "Pages Evaluated": data.get("pages_evaluated", 0),
                "Confidence": data.get("confidence_score", "N/A")
            })
        
        return pd.DataFrame(scores_data)
