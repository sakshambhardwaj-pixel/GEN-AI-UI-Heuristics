# Implementation Plan

- [x] 1. Create MetricsTracker module with core data classes










  - [x] 1.1 Create `metrics_tracker.py` with CrawlMetrics, TokenMetrics, and TimeMetrics dataclasses


    - Define CrawlMetrics with pages_requested, pages_crawled, pages_skipped, skip_reasons fields
    - Define TokenMetrics with total_input_tokens, total_output_tokens, api_calls fields and calculate_cost method
    - Define TimeMetrics with start_time, end_time fields and elapsed_seconds property and format_elapsed method
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 5.1_
  - [x] 1.2 Write property test for time tracking consistency








    - **Property 3: Time Tracking Consistency**
    - **Validates: Requirements 3.1, 3.2, 3.3**

  - [x] 1.3 Implement MetricsTracker class with session management methods



    - Implement start_session(), end_session(), record_page_crawled(), record_page_skipped(), record_api_call()
    - Implement get_summary() method returning complete metrics dictionary
    - _Requirements: 6.1, 6.2_
  - [ ]* 1.4 Write property test for token accumulation correctness
    - **Property 4: Token Accumulation Correctness**
    - **Validates: Requirements 4.1, 4.2**
  - [ ]* 1.5 Write property test for cost calculation accuracy
    - **Property 5: Cost Calculation Accuracy**
    - **Validates: Requirements 4.3, 4.4, 4.5**
  - [ ]* 1.6 Write property test for skip reason categorization
    - **Property 6: Skip Reason Categorization**
    - **Validates: Requirements 5.1, 5.3, 5.4, 5.5**
  - [ ]* 1.7 Write property test for metrics summary completeness
    - **Property 7: Metrics Summary Completeness**
    - **Validates: Requirements 6.1, 6.2**



- [x] 2. Checkpoint - Ensure all tests pass




  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Fix crawling functions to respect max page limit

  - [x] 3.1 Modify `login_and_crawl_all_pages` to accept and enforce max_pages parameter





    - Add max_pages parameter to function signature
    - Check page count before adding new URLs to crawl queue

    - Pass MetricsTracker instance to track crawl metrics
    - _Requirements: 1.1, 1.2_
  - [x] 3.2 Modify `crawl_all_pages_no_login` to properly enforce max_pages parameter

    - Ensure max_pages is checked at the start of each crawl iteration
    - Stop link discovery when limit is reached
    - _Requirements: 1.1, 1.2_

  - [x] 3.3 Update crawl functions to prioritize prescriptive URLs


    - Process prescriptive URLs first before discovering new links
    - Ensure prescriptive URLs are included within the max page limit



    - _Requirements: 1.3_
  - [ ]* 3.4 Write property test for max page limit enforcement
    - **Property 1: Max Page Limit Enforcement**
    - **Validates: Requirements 1.1**
  - [ ]* 3.5 Write property test for prescriptive URL prioritization
    - **Property 2: Prescriptive URL Prioritization**

    - **Validates: Requirements 1.3**

- [x] 4. Add skip reason logging to crawl functions


  - [x] 4.1 Update crawl functions to log skip reasons with MetricsTracker

    - Log "max_limit_reached" when page limit is hit

    - Log "duplicate" when URL already visited

    - Log "domain_mismatch" when URL is outside base domain
    - Log "navigation_error" with error details when page fails to load
    - Log "max_depth_exceeded" when depth limit is reached


    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - [x] 4.2 Add summary display for skip reasons in UI

    - Display categorized skip reasons after crawl completes



    - Show count per category and sample URLs
    - _Requirements: 5.2_

- [x] 5. Checkpoint - Ensure all tests pass

  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Integrate token tracking into LLM evaluation functions

  - [x] 6.1 Modify `evaluate_heuristic_with_llm` to accept MetricsTracker and record token usage

    - Extract prompt_tokens and completion_tokens from OpenAI response.usage
    - Call metrics.record_api_call() with token counts
    - _Requirements: 4.1, 4.2_




  - [x] 6.2 Modify `analyze_each_heuristic_individually_for_report` to track tokens

    - Pass MetricsTracker to analysis function
    - Record token usage for each heuristic analysis API call
    - _Requirements: 4.1, 4.2_


- [x] 7. Update main.py to use MetricsTracker throughout evaluation flow

  - [x] 7.1 Initialize MetricsTracker at start of evaluation



    - Create MetricsTracker instance when "Run Crawl and Evaluate" is clicked
    - Call start_session() before crawling begins
    - Set pages_requested from max_pages_to_evaluate setting




    - _Requirements: 3.1, 6.1_
  - [x] 7.2 Pass MetricsTracker to crawl and evaluation functions


    - Thread MetricsTracker through run_crawl_and_evaluate_stream and run_crawl_and_evaluate_public



    - Pass to all crawl functions and LLM evaluation functions
    - _Requirements: 3.1, 4.1, 5.1_

  - [x] 7.3 Call end_session() and display metrics summary after evaluation completes


    - Call end_session() when all evaluations finish
    - Display metrics summary in Streamlit UI
    - Show elapsed time, pages crawled vs requested, token usage, and estimated cost
    - _Requirements: 3.2, 4.3, 4.4, 4.5, 6.1_

- [x] 8. Add metrics section to HTML report


  - [x] 8.1 Create `generate_metrics_section_html` function in html_generator.py





    - Generate HTML for execution metrics section
    - Include elapsed time, pages crawled/requested, token breakdown, and cost
    - Style consistently with existing report sections
    - _Requirements: 6.3_
  - [x] 8.2 Integrate metrics section into `generate_html_from_analysis_json`


    - Add metrics_summary parameter to function
    - Insert metrics section after Executive Summary
    - _Requirements: 6.3_

- [x] 9. Add metrics to CSV report

  - [x] 9.1 Update `convert_analysis_to_csv` to include metrics data


    - Add metrics as additional columns or summary row
    - Include elapsed_time, pages_crawled, total_tokens, estimated_cost
    - _Requirements: 6.4_

- [x] 10. Add live elapsed time display during evaluation

  - [x] 10.1 Implement running elapsed time indicator in Streamlit UI


    - Display elapsed time that updates during evaluation
    - Show alongside progress bar
    - _Requirements: 3.4_

- [x] 11. Add model selection support

  - [x] 11.1 Add MODEL_PRICING configuration to metrics_tracker.py


    - Define pricing for GPT-4o and GPT-4o-mini models
    - Update calculate_cost() to accept model parameter
    - _Requirements: 8.3_
  - [x] 11.2 Add model selection dropdown to Streamlit UI


    - Add selectbox with available models (GPT-4o, GPT-4o-mini)
    - Display model description and pricing info
    - _Requirements: 8.1_
  - [x] 11.3 Update LLM evaluation functions to use selected model


    - Pass model parameter to evaluate_heuristic_with_llm
    - Pass model parameter to analyze_each_heuristic_individually_for_report
    - _Requirements: 8.2_
  - [x] 11.4 Include model name in reports


    - Add model_used field to metrics summary
    - Display model name in HTML and Excel reports
    - _Requirements: 8.4_
  - [ ]* 11.5 Write property test for model-based cost calculation
    - **Property 5: Cost Calculation Accuracy with Model Selection**
    - **Validates: Requirements 8.3**

- [x] 12. Create internal analysis report generator

  - [x] 12.1 Create InternalReportGenerator class in new file `internal_report.py`


    - Implement generate_excel_report() method
    - Create summary sheet with all metrics
    - _Requirements: 7.1, 7.3, 7.4_
  - [x] 12.2 Implement URL tracking in CrawlMetrics


    - Add crawled_urls list to track all successfully crawled URLs
    - Update record_page_crawled() to store URLs
    - _Requirements: 7.2_
  - [x] 12.3 Create All URLs sheet in Excel report


    - Include all crawled URLs with status "Crawled"
    - Include all skipped URLs with status and reason
    - _Requirements: 7.2_
  - [x] 12.4 Create Cost Breakdown sheet in Excel report

    - Include tokens per page, cost per page calculations
    - Include max depth information
    - _Requirements: 7.4, 7.5_
  - [x] 12.5 Integrate internal report generation into main.py


    - Generate Excel report after evaluation completes
    - Add download button for internal report
    - _Requirements: 7.1_
  - [ ]* 12.6 Write property test for internal report URL completeness
    - **Property 8: Internal Report URL Completeness**
    - **Validates: Requirements 7.2**

- [x] 13. Update client-facing HTML report to exclude URL details

  - [x] 13.1 Remove detailed URL list from HTML report


    - Ensure analyzed_urls are not displayed in client report
    - Keep only summary metrics visible
    - _Requirements: 7.6_
  - [ ]* 13.2 Write property test for client report URL exclusion
    - **Property 9: Client Report URL Exclusion**
    - **Validates: Requirements 7.6**

- [x] 14. Enhance authenticated site navigation

  - [x] 14.1 Implement navigate_authenticated_site function


    - Add post-login landing page detection
    - Implement error message detection for failed logins
    - _Requirements: 9.1, 9.2_
  - [x] 14.2 Update login_and_crawl_all_pages to use enhanced navigation


    - Use navigate_authenticated_site for initial login
    - Start crawling from post-login landing page when no prescriptive URLs
    - _Requirements: 9.1, 9.2_
  - [x] 14.3 Add diagnostic logging for navigation issues

    - Log detailed state information when navigation fails
    - Provide clear feedback about accessible pages
    - _Requirements: 9.3, 9.4_
  - [x] 14.4 Ensure session state consistency

    - Verify authenticated session is maintained across requests
    - Add session validation checks
    - _Requirements: 9.5_

- [x] 15. Checkpoint - Ensure all tests pass


  - Ensure all tests pass, ask the user if questions arise.

- [x] 16. Final integration and testing

  - [x] 16.1 End-to-end test with model selection


    - Test evaluation with GPT-4o and GPT-4o-mini
    - Verify cost calculations are correct for each model
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 16.2 Test dual report generation

    - Verify HTML report excludes URL details
    - Verify Excel report includes all URLs and metrics
    - _Requirements: 7.1, 7.6_
  - [x] 16.3 Test authenticated site crawling

    - Test with sites requiring login
    - Verify post-login page discovery works
    - _Requirements: 9.1, 9.2_

- [x] 17. Final Checkpoint - Ensure all tests pass



  - Ensure all tests pass, ask the user if questions arise.
