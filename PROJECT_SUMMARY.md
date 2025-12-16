# AI-Powered Heuristic Evaluation Tool

## About

An automated web application that performs comprehensive UX heuristic evaluations on websites using GPT-4o. It intelligently crawls pages and analyzes them against established usability principles and WCAG accessibility standards, generating detailed reports with actionable recommendations.

## Key Capabilities

- **Intelligent Web Crawling** - Automatically discovers and crawls pages within a domain, supports authenticated sites with login handling
- **AI-Powered Analysis** - Uses GPT-4o to evaluate each page against customizable UX heuristics with structured scoring (0-4 scale)
- **WCAG Compliance** - Built-in integration with WCAG 2.2 guidelines for accessibility audits
- **Custom Heuristics** - Upload Excel files with your own evaluation criteria and prompts
- **Real-Time Progress** - Live tracking of evaluation progress with expandable results
- **Comprehensive Reporting** - Generates professional HTML reports with grades, charts, strengths/weaknesses, and prioritized recommendations
- **Targeted Evaluation** - Map specific URLs to specific heuristics for focused analysis
- **Export Options** - Download reports as HTML or CSV for stakeholder sharing and data analysis

## Business Value

| Value Area | Impact |
|------------|--------|
| **Time Savings** | Automates manual heuristic evaluation work that typically takes days |
| **Cost Reduction** | Reduces need for extensive UX consultant hours |
| **Consistency** | Standardized evaluation criteria across all assessments |
| **Actionable Insights** | Prioritized recommendations with effort/impact analysis |
| **Compliance** | Automated WCAG accessibility compliance checking |
| **Competitive Edge** | Enables rapid competitive UX benchmarking |
| **Quality Assurance** | Pre-launch audits catch issues before users do |
| **Continuous Improvement** | Track UX scores over time to measure progress |

## Tech Stack

Python, Streamlit, Playwright, OpenAI GPT-4o, BeautifulSoup, Pandas
