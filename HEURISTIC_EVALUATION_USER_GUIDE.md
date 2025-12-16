# Heuristic Evaluation Tool - User Guide & Knowledge Transfer

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Getting Started](#getting-started)
4. [Feature Walkthrough](#feature-walkthrough)
5. [Use Cases & Scenarios](#use-cases--scenarios)
6. [Technical Architecture](#technical-architecture)
7. [Troubleshooting](#troubleshooting)

---

## Project Overview

### What is This Tool?
The **Heuristic Evaluation Tool** is an AI-powered web application that automatically evaluates websites against usability heuristics and WCAG (Web Content Accessibility Guidelines) standards. It crawls websites, analyzes their content using OpenAI's GPT-4, and generates comprehensive evaluation reports.

### Key Benefits
- **Automated UX Analysis**: Eliminates manual heuristic evaluation work
- **WCAG Compliance Checking**: Validates accessibility standards automatically
- **Comprehensive Reports**: Generates detailed HTML and CSV reports with actionable insights
- **Multi-Page Analysis**: Crawls and evaluates multiple pages across a website
- **Login Support**: Can evaluate authenticated/protected pages

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Web Crawling**: Playwright (browser automation)
- **AI Analysis**: OpenAI GPT-4o
- **Report Generation**: Custom HTML/CSS templates
- **Data Processing**: Pandas, BeautifulSoup4

---

## Key Features

### 1. **Custom Heuristic Evaluation**
Upload an Excel file with custom heuristics and evaluation prompts to assess specific UX principles.

### 2. **WCAG Guidelines Integration**
Automatically fetches and evaluates against WCAG 2.2 success criteria from W3C.

### 3. **Authenticated Site Crawling**
Supports login-protected websites with customizable CSS selectors for authentication.

### 4. **Public Site Crawling**
Evaluates public websites without authentication requirements.

### 5. **Targeted URL Evaluation**
Assign specific URLs to specific heuristics for focused analysis.

### 6. **Live Progress Tracking**
Real-time progress bars and status updates during evaluation.

### 7. **Enhanced HTML Reports**
Professional, comprehensive reports with:
- Executive summaries with letter grades
- Visual bar charts for scores
- Strengths and weaknesses analysis
- Prioritized recommendations
- Business impact assessments
- Quick wins identification

### 8. **CSV Export**
Structured data export for further analysis in Excel or other tools.

---

## Getting Started

### Prerequisites
1. **Python 3.8+** installed
2. **OpenAI API Key** (required for AI analysis)
3. **Internet connection** for web crawling

### Installation

#### Option 1: Local Setup
```bash
# Navigate to project directory
cd GEN-AI-Heuristics

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run the application
streamlit run main.py
```

#### Option 2: Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8501
```

#### Option 3: Podman Setup (Windows)
```powershell
# Build the container
.\build-podman.ps1

# Start the application
.\start_app.ps1

# Stop the application
.\stop-podman.ps1
```

### Initial Configuration
1. Open browser to `http://localhost:8501`
2. The Streamlit interface will load
3. Configure your evaluation in the sidebar

---

## Feature Walkthrough

### Feature 1: Evaluating a Public Website with WCAG Guidelines

**Use Case**: You want to check if your public marketing website meets accessibility standards.

**Steps**:

1. **Configure Sidebar Settings**
   - ✅ Uncheck "Use UI Heuristic Prompt Sheet"
   - ✅ Expand "WCAG Guidelines" section
   - ✅ Click "Select All" or choose specific guidelines (e.g., "1.1.1 Non-text Content")
   - ✅ Uncheck "Site requires login"
   - ✅ Enter your website URL in "Site URL" field: `https://example.com`
   - ✅ Set "Max pages to evaluate": `5`

2. **Run Evaluation**
   - Click **"Run Crawl and Evaluate"** button
   - Watch live progress as pages are crawled and evaluated
   - Each evaluation result appears in expandable sections

3. **Generate Report**
   - After evaluation completes, click **"Generate Enhanced Report (HTML)"**
   - Wait for AI analysis (progress bar shows status)
   - Download buttons appear for HTML and CSV reports

4. **Review Results**
   - Open HTML report in browser
   - Review overall grade and performance level
   - Check detailed heuristic scores
   - Read prioritized recommendations

**Expected Output**:
- Overall grade (A-F) based on average scores
- Detailed analysis for each WCAG criterion
- Visual bar charts showing performance
- Actionable recommendations with priority levels

---

### Feature 2: Evaluating a Login-Protected Website with Custom Heuristics

**Use Case**: You need to evaluate an internal application that requires authentication using your company's custom UX heuristics.

**Steps**:

1. **Prepare Heuristic Excel File**
   - Create Excel file with sheet named "AI Prompts"
   - Column A: Heuristic names (e.g., "Visibility of System Status")
   - Column B: Evaluation prompts for AI
   - Example prompt format:
     ```
     Evaluate the website's visibility of system status.
     Score from 0-4 where:
     - 4 = Excellent: Clear feedback for all actions
     - 3 = Good: Most actions have feedback
     - 2 = Fair: Some feedback present
     - 1 = Poor: Minimal feedback
     - 0 = Critical: No feedback provided
     
     Analyze: [Enter Website URL Here]
     Provide specific examples and scores.
     ```

2. **Configure Sidebar for Login**
   - ✅ Check "Use UI Heuristic Prompt Sheet"
   - ✅ Upload your Excel file
   - ✅ Check "Site requires login"
   - ✅ Enter "Login URL": `https://app.example.com/login`
   - ✅ Enter credentials (Username/Password)
   - ✅ Configure CSS selectors:
     - **Username Selector**: `#username` (or `.username-field`, `input[name='user']`)
     - **Password Selector**: `#password`
     - **Submit Button Selector**: `#login-button`

3. **Find CSS Selectors** (Important!)
   - Open login page in Chrome/Firefox
   - Right-click on username field → "Inspect Element"
   - Look for `id` attribute: `<input id="username">` → use `#username`
   - Or `class` attribute: `<input class="user-input">` → use `.user-input`
   - Or `name` attribute: `<input name="user">` → use `input[name='user']`
   - Repeat for password field and submit button

4. **Optional: Specify URLs**
   - Enter specific URLs to evaluate (one per line):
     ```
     https://app.example.com/dashboard
     https://app.example.com/settings
     https://app.example.com/profile
     ```

5. **Run Evaluation**
   - Click **"Run Crawl and Evaluate"**
   - Tool logs in automatically
   - Crawls up to 50 pages (max depth: 2 levels)
   - Evaluates each page against all heuristics

6. **Generate and Download Report**
   - Click **"Generate Enhanced Report (HTML)"**
   - Download HTML report for stakeholders
   - Download CSV for data analysis

**Expected Output**:
- Comprehensive evaluation across all custom heuristics
- Page-by-page analysis
- Aggregated scores and grades
- Business impact assessments
- Quick wins for immediate improvements

---

### Feature 3: Targeted Heuristic-URL Mapping

**Use Case**: You want to evaluate specific heuristics on specific pages (e.g., checkout flow for "Error Prevention", homepage for "Aesthetic Design").

**Steps**:

1. **Enable Per-Heuristic Assignment**
   - Configure heuristics (Excel upload or WCAG selection)
   - ✅ Check "Assign URLs to specific heuristics"

2. **Assign URLs to Heuristics**
   - Text areas appear for each heuristic
   - Enter URLs for each heuristic (one per line):
     ```
     For "Error Prevention":
     https://shop.example.com/checkout
     https://shop.example.com/payment
     
     For "Aesthetic and Minimalist Design":
     https://shop.example.com/
     https://shop.example.com/products
     ```

3. **Run Targeted Evaluation**
   - Click **"Run Crawl and Evaluate"**
   - Each heuristic only evaluates its assigned URLs
   - More focused and faster analysis

**Expected Output**:
- Focused evaluation results
- Reduced evaluation time
- More relevant insights per heuristic

---

### Feature 4: Combining WCAG and Custom Heuristics

**Use Case**: You want comprehensive evaluation covering both accessibility standards and custom UX principles.

**Steps**:

1. **Enable Both Sources**
   - ✅ Check "Use UI Heuristic Prompt Sheet"
   - Upload custom heuristics Excel file
   - Expand "WCAG Guidelines"
   - Select relevant WCAG criteria

2. **Configure Target Site**
   - Set up login (if needed) or public URL
   - Specify URLs or let it crawl

3. **Run Combined Evaluation**
   - Click **"Run Crawl and Evaluate"**
   - Tool evaluates against ALL selected heuristics (custom + WCAG)

4. **Review Comprehensive Report**
   - HTML report includes both custom and WCAG evaluations
   - Unified scoring and recommendations

**Expected Output**:
- Holistic UX and accessibility assessment
- Combined recommendations prioritized by impact
- Complete compliance picture

---

### Feature 5: Iterative Evaluation and Comparison

**Use Case**: You've made improvements and want to re-evaluate to measure progress.

**Steps**:

1. **Initial Evaluation**
   - Run evaluation as described above
   - Download and save HTML report with date: `report_2024-01-15.html`
   - Note overall grade and key issues

2. **Make Improvements**
   - Implement recommended changes
   - Deploy updates to website

3. **Re-Evaluation**
   - Click **"🔄 Refresh"** button in sidebar (clears session)
   - Configure same settings as initial evaluation
   - Run evaluation again
   - Download new report: `report_2024-02-15.html`

4. **Compare Results**
   - Open both HTML reports side-by-side
   - Compare overall grades
   - Check if specific heuristic scores improved
   - Verify issues were resolved

**Expected Output**:
- Measurable improvement metrics
- Validation of fixes
- Identification of remaining issues

---

## Use Cases & Scenarios

### Scenario 1: Pre-Launch Website Audit
**Goal**: Ensure new website meets UX standards before launch

**Approach**:
1. Use WCAG guidelines for accessibility baseline
2. Add custom heuristics for brand-specific UX principles
3. Evaluate staging environment (with login if needed)
4. Generate report for stakeholder review
5. Prioritize fixes based on "High Priority" recommendations
6. Implement "Quick Wins" first
7. Re-evaluate before launch

**Timeline**: 2-3 days for evaluation and fixes

---

### Scenario 2: Competitive Analysis
**Goal**: Compare your website against competitors

**Approach**:
1. Evaluate your website (save report as `our_site.html`)
2. Evaluate competitor sites (public URLs, no login)
3. Use same heuristics for fair comparison
4. Compare overall grades and specific heuristic scores
5. Identify areas where competitors excel
6. Prioritize improvements based on competitive gaps

**Timeline**: 1 day for evaluations, ongoing for improvements

---

### Scenario 3: Accessibility Compliance Audit
**Goal**: Verify WCAG 2.2 Level AA compliance

**Approach**:
1. Select all relevant WCAG Level A and AA criteria
2. Evaluate all public pages
3. Generate comprehensive report
4. Document all failures with evidence
5. Create remediation plan based on priority
6. Track progress with re-evaluations

**Timeline**: Ongoing compliance monitoring

---

### Scenario 4: Post-Redesign Validation
**Goal**: Ensure redesign improved UX without introducing new issues

**Approach**:
1. Evaluate old design (before redesign)
2. Save baseline report
3. After redesign, evaluate new design with same heuristics
4. Compare scores across all heuristics
5. Verify improvements in targeted areas
6. Identify any regressions
7. Address new issues before full rollout

**Timeline**: 1 week for validation cycle

---

## Technical Architecture

### System Flow
```
User Input (Streamlit UI)
    ↓
Configuration (Login/URLs/Heuristics)
    ↓
Web Crawling (Playwright)
    ↓
Content Extraction (BeautifulSoup)
    ↓
AI Evaluation (OpenAI GPT-4o)
    ↓
Analysis Aggregation
    ↓
Report Generation (HTML/CSV)
    ↓
Download/Review
```

### Key Components

#### 1. **main.py** - Core Application
- Streamlit UI setup
- Orchestrates crawling and evaluation
- Manages session state
- Handles user interactions

#### 2. **html_generator.py** - Report Generation
- `generate_html_from_analysis_json()`: Creates comprehensive HTML reports
- `generate_overall_assessment_text()`: Generates executive summary
- `generate_conclusion_content()`: Creates actionable conclusions
- Professional styling with CSS

#### 3. **Crawling Functions**
- `login_and_crawl_all_pages()`: Authenticated crawling
- `crawl_all_pages_no_login()`: Public site crawling
- `crawl_specific_urls()`: Targeted URL crawling
- Playwright-based browser automation
- Resource blocking for faster crawling

#### 4. **Evaluation Functions**
- `evaluate_heuristic_with_llm()`: Single page evaluation
- `analyze_each_heuristic_individually_for_report()`: Aggregates results
- OpenAI API integration
- Structured prompt engineering

### Data Flow

#### Input Data Structures
```python
# Heuristic Prompt Map
{
    "Heuristic Name": "Evaluation prompt text...",
    "Another Heuristic": "Another prompt..."
}

# Heuristic-URL Map (optional)
{
    "Heuristic Name": ["url1", "url2"],
    "Another Heuristic": ["url3", "url4"]
}
```

#### Output Data Structures
```python
# Evaluation Results
{
    "Heuristic Name": {
        "url1": {"output": "AI evaluation text..."},
        "url2": {"output": "AI evaluation text..."}
    }
}

# Analysis JSON (for reports)
{
    "Heuristic Name": {
        "heuristic_name": "...",
        "total_score": 3.2,
        "grade": "B",
        "performance_level": "Good",
        "subtopics": [...],
        "recommendations": [...],
        "key_strengths": [...],
        "key_weaknesses": [...]
    }
}
```

### Configuration Files

#### **.env**
```
OPENAI_API_KEY=your_api_key_here
```

#### **docker-compose.yml**
- Defines containerized deployment
- Port mapping (8501)
- Environment variables
- Volume mounts for uploads

#### **requirements.txt**
- All Python dependencies
- Pinned versions for reproducibility

---

## Troubleshooting

### Issue 1: "Login Failed" Error
**Symptoms**: Evaluation fails immediately after clicking "Run Crawl and Evaluate"

**Solutions**:
1. **Verify CSS Selectors**:
   - Open login page in browser
   - Right-click → Inspect Element on each field
   - Confirm selectors match actual HTML
   - Try alternative selectors (id, class, name)

2. **Check Credentials**:
   - Verify username/password are correct
   - Check for typos or extra spaces

3. **Increase Timeout**:
   - Some sites load slowly
   - Code has 120s timeout (should be sufficient)

4. **Check for CAPTCHA**:
   - Tool cannot bypass CAPTCHAs
   - Use test accounts without CAPTCHA requirements

---

### Issue 2: "No Pages Crawled" or "Empty Content"
**Symptoms**: Evaluation runs but finds no content

**Solutions**:
1. **Check URL Format**:
   - Must include `https://` or `http://`
   - Verify URL is accessible

2. **Verify Login Success**:
   - Check if login actually worked
   - Look at console output for errors

3. **Check Max Depth/Pages**:
   - Default: 50 pages max, 2 levels deep
   - Increase if needed (edit code)

4. **JavaScript-Heavy Sites**:
   - Tool waits for "domcontentloaded"
   - Some SPAs may need longer waits
   - Consider adding delays in code

---

### Issue 3: "OpenAI API Error"
**Symptoms**: Evaluation fails during AI analysis

**Solutions**:
1. **Check API Key**:
   - Verify `.env` file exists
   - Confirm API key is valid
   - Check OpenAI account has credits

2. **Rate Limiting**:
   - OpenAI has rate limits
   - Tool includes 1s delays between requests
   - Reduce number of pages/heuristics if hitting limits

3. **Token Limits**:
   - Very large pages may exceed token limits
   - Tool truncates content to 3000 chars for analysis
   - Should handle most cases

---

### Issue 4: "Report Generation Failed"
**Symptoms**: Evaluation completes but report generation fails

**Solutions**:
1. **Check Evaluation Data**:
   - Verify evaluations actually ran
   - Look for error messages in console

2. **JSON Parsing Issues**:
   - AI sometimes returns malformed JSON
   - Tool has fallback analysis
   - Check if fallback was used

3. **Memory Issues**:
   - Large evaluations may use lots of memory
   - Reduce number of pages
   - Restart application

---

### Issue 5: Slow Performance
**Symptoms**: Evaluation takes very long time

**Solutions**:
1. **Reduce Scope**:
   - Evaluate fewer pages
   - Use specific URLs instead of full crawl
   - Select fewer heuristics

2. **Optimize Crawling**:
   - Tool already blocks images/media/fonts
   - Consider reducing max_depth in code

3. **Parallel Processing**:
   - Current implementation is sequential
   - Could be parallelized (code modification needed)

---

### Issue 6: CSS Selector Not Working
**Symptoms**: Login fails with correct credentials

**Common Selector Patterns**:
```css
/* By ID */
#username
#user-name
#login-username

/* By Class */
.username-input
.form-control.username

/* By Name Attribute */
input[name='username']
input[name='user']

/* By Type */
input[type='email']
input[type='password']

/* Complex Selectors */
form#login input[name='username']
div.login-form input.username
```

**How to Find Correct Selector**:
1. Open browser DevTools (F12)
2. Click "Select Element" tool (Ctrl+Shift+C)
3. Click on the field
4. In Elements panel, right-click element
5. Copy → Copy selector
6. Simplify if needed (remove unnecessary parts)

---

## Best Practices

### 1. Heuristic Prompt Design
**Good Prompt Example**:
```
Evaluate the website's error prevention mechanisms.

Score from 0-4:
- 4 = Excellent: Comprehensive validation, confirmations, undo options
- 3 = Good: Most errors prevented, some confirmations
- 2 = Fair: Basic validation present
- 1 = Poor: Minimal error prevention
- 0 = Critical: No error prevention

Analyze: [Enter Website URL Here]

Provide:
1. Overall score with justification
2. Specific examples of good/bad error prevention
3. Recommendations for improvement
4. Impact on user experience
```

**Why This Works**:
- Clear scoring criteria
- Specific evaluation dimensions
- Requests structured output
- Asks for examples and recommendations

---

### 2. Evaluation Scope Planning
**Small Scope (Quick Check)**:
- 3-5 key pages
- 5-8 critical heuristics
- 30-60 minutes total time

**Medium Scope (Comprehensive)**:
- 10-20 pages
- 10-15 heuristics
- 2-4 hours total time

**Large Scope (Full Audit)**:
- 30-50 pages
- All WCAG + custom heuristics
- 4-8 hours total time

---

### 3. Report Review Workflow
1. **Executive Summary First**:
   - Check overall grade
   - Read key findings
   - Understand strategic implications

2. **Prioritize by Impact**:
   - Focus on "High Priority" recommendations
   - Review "Critical Issues" section
   - Identify "Quick Wins"

3. **Detailed Analysis**:
   - Review each heuristic's detailed assessment
   - Check specific examples and evidence
   - Understand business impact

4. **Action Planning**:
   - Create tickets for high-priority issues
   - Assign quick wins to team members
   - Schedule follow-up evaluation

---

### 4. Continuous Monitoring
**Monthly Audits**:
- Run same evaluation monthly
- Track score trends over time
- Measure improvement velocity

**Post-Release Checks**:
- Evaluate after each major release
- Catch regressions early
- Validate improvements

**Competitive Benchmarking**:
- Quarterly competitor evaluations
- Track relative performance
- Identify industry trends

---

## Advanced Usage

### Custom Scoring Scales
Modify prompts to use different scales:
- 0-10 scale for finer granularity
- Pass/Fail for compliance checks
- Percentage-based scoring

### Multi-Language Support
- Evaluate sites in different languages
- Adjust prompts for language-specific heuristics
- Consider cultural UX differences

### Integration with CI/CD
```bash
# Example: Run evaluation in CI pipeline
python -c "
from main import run_crawl_and_evaluate_public
results = run_crawl_and_evaluate_public(
    'https://staging.example.com',
    prompt_map,
    max_pages_to_evaluate=10
)
# Check if scores meet threshold
# Fail build if scores too low
"
```

---

## Appendix

### Sample Heuristics Excel Format
| Heuristic Name | Evaluation Prompt |
|----------------|-------------------|
| Visibility of System Status | Evaluate how well the website keeps users informed... |
| Match Between System and Real World | Assess if the website uses familiar language... |
| User Control and Freedom | Check if users can easily undo actions... |

### WCAG 2.2 Coverage
The tool can evaluate against all WCAG 2.2 success criteria including:
- **Perceivable**: Text alternatives, captions, adaptable content
- **Operable**: Keyboard accessible, enough time, seizure prevention
- **Understandable**: Readable, predictable, input assistance
- **Robust**: Compatible with assistive technologies

### Useful Resources
- [Nielsen Norman Group - 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Playwright Documentation](https://playwright.dev/python/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

---

## Support & Maintenance

### Getting Help
1. Check this guide first
2. Review error messages in console
3. Check Streamlit logs
4. Verify all prerequisites are met

### Updating Dependencies
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update Playwright browsers
playwright install chromium
```

### Contributing Improvements
- Add new heuristics to Excel template
- Enhance prompts for better AI analysis
- Improve report styling in `html_generator.py`
- Add new features to `main.py`

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: Development Team
