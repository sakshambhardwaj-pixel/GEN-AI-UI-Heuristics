# Requirements Document

## Introduction

This document specifies requirements for improving the GEN-AI-Heuristics evaluation tool based on user feedback and stakeholder meetings. The improvements focus on five main areas: (1) fixing the page crawling behavior where the max page limit setting doesn't work as expected, (2) adding execution metrics including elapsed time and cost tracking, (3) implementing transparent token consumption logging to help users understand resource usage and financial feasibility, (4) creating separate internal analysis reports for detailed metrics and URL tracking, and (5) supporting model selection for cost/latency optimization.

## Glossary

- **Crawler**: The component that navigates web pages using Playwright to collect HTML content for evaluation
- **Max Page Limit**: User-configurable setting that specifies the maximum number of pages the Crawler should evaluate
- **Prescriptive URLs**: Specific URLs provided by the user that the Crawler must evaluate
- **Token**: A unit of text processed by the OpenAI API, used for billing purposes
- **Evaluation**: The process of analyzing a page's content against heuristic criteria using the LLM
- **Session**: A complete run of the tool from start to finish, including crawling and evaluation phases
- **Max Depth**: The number of URLs discovered between main crawled pages, including hidden and nested URLs
- **Internal Analysis Report**: A detailed report containing all scanned URLs, metrics, and technical details for internal use
- **Client-Facing Report**: A streamlined HTML report suitable for sharing with clients without technical details
- **Model Selection**: The ability to choose between different LLM models (GPT-4o, GPT-4o-mini) for evaluation

## Requirements

### Requirement 1

**User Story:** As a user, I want the max page limit setting to accurately control how many pages are evaluated, so that I can predict and control the scope of my analysis.

#### Acceptance Criteria

1. WHEN a user sets the max page limit to N pages, THE Crawler SHALL evaluate no more than N pages during the crawling phase
2. WHEN the Crawler reaches the max page limit, THE Crawler SHALL stop discovering new pages and proceed with evaluation
3. WHEN prescriptive URLs are provided, THE Crawler SHALL prioritize those URLs within the max page limit
4. WHEN the Crawler completes, THE System SHALL display the actual number of pages crawled versus the max page limit requested

### Requirement 2

**User Story:** As a user, I want the crawler to navigate past login pages when no prescriptive URLs are provided, so that I can evaluate authenticated content without manually specifying every URL.

#### Acceptance Criteria

1. WHEN a user provides login credentials and no prescriptive URLs, THE Crawler SHALL navigate past the login page and discover internal pages
2. WHEN the Crawler encounters a login page during crawling, THE Crawler SHALL detect the login state and attempt to proceed to authenticated content
3. WHEN the Crawler fails to navigate past a login page, THE System SHALL log a warning message indicating the login navigation issue
4. WHEN crawling authenticated sites, THE Crawler SHALL maintain the authenticated session across all page requests

### Requirement 3

**User Story:** As a user, I want to see elapsed time for the analysis, so that I can understand how long evaluations take and plan accordingly.

#### Acceptance Criteria

1. WHEN an evaluation session starts, THE System SHALL record the start timestamp
2. WHEN an evaluation session completes, THE System SHALL calculate and display the total elapsed time
3. WHEN displaying elapsed time, THE System SHALL format the duration in human-readable format showing hours, minutes, and seconds
4. WHEN the evaluation is in progress, THE System SHALL display a running elapsed time indicator

### Requirement 4

**User Story:** As a user, I want to see the token consumption and associated costs for each evaluation, so that I can assess the financial feasibility of running analyses at scale.

#### Acceptance Criteria

1. WHEN an LLM API call is made, THE System SHALL capture the number of input tokens consumed
2. WHEN an LLM API call is made, THE System SHALL capture the number of output tokens consumed
3. WHEN an evaluation session completes, THE System SHALL display the total tokens consumed broken down by input and output tokens
4. WHEN displaying token usage, THE System SHALL calculate and display the estimated cost in USD based on current OpenAI pricing
5. WHEN displaying cost metrics, THE System SHALL show cost per page evaluated for easy scaling estimates

### Requirement 5

**User Story:** As a user, I want transparent logging of why pages were not evaluated, so that I can understand and troubleshoot when the tool evaluates fewer pages than requested.

#### Acceptance Criteria

1. WHEN the Crawler skips a page, THE System SHALL log the reason for skipping with the URL
2. WHEN the evaluation completes with fewer pages than the max limit, THE System SHALL display a summary explaining why fewer pages were evaluated
3. WHEN pages are skipped due to navigation errors, THE System SHALL categorize and count errors by type
4. WHEN pages are skipped due to duplicate URLs, THE System SHALL log the duplicate detection
5. WHEN pages are skipped due to being outside the base domain, THE System SHALL log the domain mismatch

### Requirement 6

**User Story:** As a user, I want a metrics summary section in the output report, so that I can review all execution statistics in one place.

#### Acceptance Criteria

1. WHEN an evaluation session completes, THE System SHALL generate a metrics summary section
2. WHEN generating the metrics summary, THE System SHALL include total elapsed time, pages requested, pages evaluated, total tokens consumed, and estimated cost
3. WHEN generating the HTML report, THE System SHALL include the metrics summary as a dedicated section
4. WHEN generating the CSV report, THE System SHALL include metrics as additional columns or a separate summary row

### Requirement 7

**User Story:** As an internal analyst, I want a separate detailed analysis report containing all scanned URLs and technical metrics, so that I can review comprehensive crawl data without exposing technical details to clients.

#### Acceptance Criteria

1. WHEN an evaluation session completes, THE System SHALL generate a separate internal analysis report in Excel format
2. WHEN generating the internal report, THE System SHALL include all analyzed URLs including hidden and nested URLs discovered during crawling
3. WHEN generating the internal report, THE System SHALL include detailed time metrics showing elapsed time per page and total session duration
4. WHEN generating the internal report, THE System SHALL include cost breakdown showing tokens per page, cost per page, and total cost
5. WHEN generating the internal report, THE System SHALL include max depth information showing the number of URLs discovered between main pages
6. WHEN generating the client-facing HTML report, THE System SHALL exclude the detailed URL list to avoid misleading information about pages scanned

### Requirement 8

**User Story:** As a user, I want to select which LLM model to use for evaluation, so that I can optimize for cost or quality based on my needs.

#### Acceptance Criteria

1. WHEN configuring an evaluation, THE System SHALL display a model selection dropdown with available models (GPT-4o, GPT-4o-mini)
2. WHEN a user selects a model, THE System SHALL use that model for all LLM API calls during the evaluation
3. WHEN displaying cost estimates, THE System SHALL calculate costs based on the selected model's pricing
4. WHEN generating reports, THE System SHALL include the model name used for the evaluation

### Requirement 9

**User Story:** As a user, I want the crawler to reliably navigate authenticated sites when no prescriptive URLs are provided, so that I can evaluate protected content without manually specifying every URL.

#### Acceptance Criteria

1. WHEN a user provides login credentials without prescriptive URLs, THE Crawler SHALL navigate past the login page and discover internal pages automatically
2. WHEN the Crawler successfully authenticates, THE Crawler SHALL explore the authenticated site starting from the post-login landing page
3. WHEN the Crawler fails to discover pages after login, THE System SHALL log detailed diagnostic information about the navigation state
4. WHEN the Crawler encounters navigation uncertainty, THE System SHALL provide clear feedback to the user about what pages were accessible
5. WHEN crawling authenticated sites, THE Crawler SHALL maintain consistent session state across all page requests
