# AI-Powered Heuristic Evaluation Tool - End-to-End Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          1. USER CONFIGURATION                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │ Target URL   │  │ Login Config │  │ Excel File   │
          │ Max Pages    │  │ (Optional)   │  │ (Heuristics) │
          └──────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          2. WEB CRAWLING PHASE                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │ Launch Playwright │
                          │ (Chromium Browser)│
                          └───────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          │   Login Required?     │
                          └───────────┬───────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │ YES             │                 │ NO
                    ▼                 │                 ▼
          ┌──────────────────┐        │       ┌──────────────────┐
          │ Navigate to      │        │       │ Navigate to      │
          │ Login URL        │        │       │ Start URL        │
          │ Enter Credentials│        │       └──────────────────┘
          │ Submit Form      │        │                 │
          └──────────────────┘        │                 │
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                          ┌───────────────────┐
                          │ Extract Page HTML │
                          │ Clean Content     │
                          └───────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │ Find All Links    │
                          │ Filter Same-Domain│
                          └───────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Follow Links (Depth ≤ 2)   │
                    │ Store: URL + HTML Content   │
                    └─────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │ Reached Max Pages?│
                          └───────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │ NO              │                 │ YES
                    │                 │                 │
                    └────────┐        │        ┌────────┘
                             │        │        │
                             └────────┼────────┘
                                      ▼
                          ┌───────────────────┐
                          │ Crawling Complete │
                          │ Pages Collected:  │
                          │ [URL1, URL2, ...] │
                          └───────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      3. EVALUATION PHASE (Page-by-Page)                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Load Heuristics from Excel  │
                    │ [H1, H2, H3, ..., Hn]       │
                    └─────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ FOR EACH PAGE (P1...Pn):    │
                    └─────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │   FOR EACH HEURISTIC (H):   │
                    └─────────────────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────┐
          │         Prepare GPT-4o API Request            │
          │  ┌─────────────────────────────────────┐      │
          │  │ Input:                              │      │
          │  │ - Page HTML Content                 │      │
          │  │ - Heuristic Evaluation Prompt       │      │
          │  └─────────────────────────────────────┘      │
          └───────────────────────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │ Call OpenAI API   │
                          │ (GPT-4o Model)    │
                          └───────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────┐
          │         Receive Evaluation Response           │
          │  ┌─────────────────────────────────────┐      │
          │  │ Output:                             │      │
          │  │ - Numeric Scores (0-4 scale)        │      │
          │  │ - Detailed Justifications           │      │
          │  │ - Specific Examples                 │      │
          │  │ - Confidence Level                  │      │
          │  └─────────────────────────────────────┘      │
          └───────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Store Result:               │
                    │ results[Heuristic][URL] =   │
                    │ {output, score, details}    │
                    └─────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Display in Streamlit UI     │
                    │ ✅ Heuristic - Completed    │
                    │ (Expandable Section)        │
                    └─────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Update Progress Counter     │
                    │ (Current/Total Evaluations) │
                    └─────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │ More Heuristics?  │
                          └───────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │ YES             │                 │ NO
                    │                 │                 │
                    └────────┐        │        ┌────────┘
                             │        │        │
                             └────────┼────────┘
                                      ▼
                          ┌───────────────────┐
                          │   More Pages?     │
                          └───────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │ YES             │                 │ NO
                    │                 │                 │
                    └────────┐        │        ┌────────┘
                             │        │        │
                             └────────┼────────┘
                                      ▼
                    ┌─────────────────────────────┐
                    │ All Evaluations Complete    │
                    │ Total: Pages × Heuristics   │
                    └─────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    4. REPORT GENERATION PHASE                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Aggregate Results by        │
                    │ Heuristic Across All Pages  │
                    └─────────────────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────┐
          │         FOR EACH HEURISTIC:                   │
          │  ┌─────────────────────────────────────┐      │
          │  │ - Calculate Average Score           │      │
          │  │ - Identify Common Patterns          │      │
          │  │ - Extract Key Issues                │      │
          │  │ - Assign Letter Grade (A-F)         │      │
          │  └─────────────────────────────────────┘      │
          └───────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Prepare Consolidated Report │
                    │ Prompt for GPT-4o           │
                    └─────────────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────┐
                          │ Call OpenAI API   │
                          │ (Report Generation)│
                          └───────────────────┘
                                      │
                                      ▼
          ┌───────────────────────────────────────────────┐
          │         Generate HTML Report                  │
          │  ┌─────────────────────────────────────┐      │
          │  │ Sections:                           │      │
          │  │ - Executive Summary                 │      │
          │  │ - Overall Grades                    │      │
          │  │ - Heuristic Breakdown               │      │
          │  │ - Key Strengths                     │      │
          │  │ - Key Weaknesses                    │      │
          │  │ - Prioritized Recommendations       │      │
          │  │ - Business Impact Analysis          │      │
          │  │ - Quick Wins                        │      │
          │  │ - Implementation Guidance           │      │
          │  └─────────────────────────────────────┘      │
          └───────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │ Display Download Button     │
                    │ in Streamlit UI             │
                    └─────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          5. USER ACTIONS                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │ Download     │  │ Review       │  │ Refresh &    │
          │ HTML Report  │  │ JSON Results │  │ Start New    │
          └──────────────┘  └──────────────┘  └──────────────┘


═══════════════════════════════════════════════════════════════════════════════
                              DATA FLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════════════

Configuration:
  • Target: https://example.com
  • Max Pages: 3
  • Heuristics: 2 (Error Prevention, User Control)

Crawling Output:
  ├─ Page 1: https://example.com/
  ├─ Page 2: https://example.com/products
  └─ Page 3: https://example.com/checkout

Evaluation Matrix (3 pages × 2 heuristics = 6 evaluations):
  
  Page 1 + Error Prevention    → Score: 3.5/4 ✅
  Page 1 + User Control        → Score: 3.0/4 ✅
  Page 2 + Error Prevention    → Score: 2.5/4 ✅
  Page 2 + User Control        → Score: 3.5/4 ✅
  Page 3 + Error Prevention    → Score: 4.0/4 ✅
  Page 3 + User Control        → Score: 3.2/4 ✅

Consolidated Report:
  
  Error Prevention:
    • Average Score: 3.33/4 (Grade: B+)
    • Pattern: Strong on checkout, weak on product pages
  
  User Control:
    • Average Score: 3.23/4 (Grade: B+)
    • Pattern: Consistent across all pages

═══════════════════════════════════════════════════════════════════════════════
                            TECHNOLOGY STACK
═══════════════════════════════════════════════════════════════════════════════

Frontend:        Streamlit (Python web framework)
Web Automation:  Playwright (Chromium browser control)
AI Processing:   OpenAI GPT-4o API
Data Storage:    Session state (in-memory)
Input Format:    Excel (.xlsx) with "AI Prompts" sheet
Output Format:   HTML report + JSON data

═══════════════════════════════════════════════════════════════════════════════
```
