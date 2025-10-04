# GEN-AI-UI-Heuristics
Here's a comprehensive README file for your application:
text
# AI-Powered Heuristic Evaluation Tool

An automated web application that performs comprehensive UX heuristic evaluations on websites by intelligently crawling pages and analyzing them against established usability principles using GPT-4o.

## 🎯 Overview

This tool automates the traditionally manual process of heuristic evaluation by:
- Automatically crawling websites (with or without authentication)
- Evaluating each discovered page against customizable UX heuristics
- Generating detailed, consolidated reports with actionable recommendations
- Providing real-time progress tracking as evaluations complete

## 🚀 Key Features

### Intelligent Web Crawling
- **Automated Discovery**: Starts from a single URL and intelligently discovers linked pages within the same domain
- **Configurable Depth**: Control how many pages to evaluate (1-100)
- **Link Following**: Automatically follows internal links up to 2 levels deep
- **Login Support**: Can authenticate and crawl pages behind login walls
- **Resource Optimization**: Blocks images, fonts, and stylesheets to speed up crawling

### Page-by-Page Heuristic Analysis
The tool evaluates **each crawled page individually** against your heuristics:
- If you set "Max pages to evaluate" to 10, it will crawl up to 10 pages
- For each page discovered, it runs **all heuristics** from your Excel file
- Example: 10 pages × 3 heuristics = 30 individual evaluations
- Each evaluation is performed by GPT-4o with detailed scoring and justification

### Real-Time Progress Tracking
- Live updates showing current page and heuristic being evaluated
- Progress bar indicating completion percentage
- Expandable results for each heuristic evaluation as they complete
- Total evaluation count (e.g., "Processing: Error Prevention (6/30)")

### Consolidated Reporting
After individual evaluations complete:
- **Aggregates findings** across all pages for each heuristic
- **Calculates average scores** from multiple page evaluations
- **Identifies patterns** in usability issues across the site
- **Generates comprehensive HTML report** with:
  - Overall scores and grades per heuristic
  - Key strengths and weaknesses
  - Prioritized recommendations
  - Business impact analysis
  - Quick wins and implementation guidance

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Playwright browser automation
- Streamlit

## 🔧 Installation

1. Clone the repository:

git clone <repository-url>
cd heuristic-evaluation-tool
text

2. Install dependencies:

pip install -r requirements.txt
text

3. Install Playwright browsers:

playwright install chromium
text

4. Create a `.env` file:

OPENAI_API_KEY=your_openai_api_key_here
text

## 📁 Required Files

### Excel File Structure
Create an Excel file with a sheet named **"AI Prompts"** containing:
- Column 1: Heuristic Name (e.g., "Error Prevention")
- Column 2: Detailed evaluation prompt for GPT-4o

Example:
| Heuristic Name | Evaluation Prompt |
|----------------|------------------|
| Error Prevention | Evaluate this page for error prevention mechanisms. Look for input validation, confirmation dialogs, undo options... |
| User Control | Assess how much control users have over their actions... |

## 🎮 Usage

### 1. Launch the Application

streamlit run main.py
text

### 2. Configure Target Website

**For Public Websites:**
- Uncheck "Site requires login"
- Enter the Website URL (e.g., `https://www.example.com`)
- Set "Max pages to evaluate" (e.g., 10)

**For Login-Protected Websites:**
- Check "Site requires login"
- Enter Login URL
- Provide credentials (username/password)
- Specify CSS selectors for login form elements

### 3. Upload Heuristics Excel File
Upload your prepared Excel file containing heuristic names and evaluation prompts.

### 4. Run Crawl and Evaluate
Click "Run Crawl and Evaluate" to start:

**Crawling Phase:**
- Starts at the specified URL
- Discovers links on the page
- Follows internal links (up to 2 levels deep)
- Extracts and cleans HTML content
- Stops when reaching max pages limit

**Evaluation Phase (Page-by-Page):**
For each crawled page:
1. Loads the page content
2. Iterates through each heuristic from your Excel file
3. Sends page content + heuristic prompt to GPT-4o
4. Receives detailed evaluation with scores and justifications
5. Displays result in expandable section
6. Moves to next heuristic for same page
7. Proceeds to next page and repeats

**Example Flow with 3 Pages and 2 Heuristics:**

Page 1: Homepage
└─ Evaluate: Error Prevention → Score: 3.5/4
└─ Evaluate: User Control → Score: 3.0/4
Page 2: Product Page
└─ Evaluate: Error Prevention → Score: 2.5/4
└─ Evaluate: User Control → Score: 3.5/4
Page 3: Checkout
└─ Evaluate: Error Prevention → Score: 4.0/4
└─ Evaluate: User Control → Score: 3.2/4
Total: 6 evaluations completed
text

### 5. Generate HTML Report
Click "Generate Enhanced Report" to:
- Analyze all page evaluations for each heuristic
- Calculate average scores across pages
- Identify common patterns and issues
- Generate downloadable HTML report with consolidated findings

## 📊 How Crawling Works

### Discovery Process
1. **Start URL**: Begin at the specified URL
2. **Extract Links**: Find all `<a href>` tags on the page
3. **Filter Links**: Keep only same-domain internal links
4. **Follow Links**: Navigate to discovered pages (up to depth 2)
5. **Limit Pages**: Stop when reaching the "Max pages to evaluate" limit

### Example Crawl Pattern

Start: https://example.com/
├─ Discovers: /about (depth 1)
├─ Discovers: /products (depth 1)
│ └─ Discovers: /products/item-1 (depth 2)
│ └─ Discovers: /products/item-2 (depth 2)
└─ Discovers: /contact (depth 1)
With "Max pages: 5" → Evaluates 5 pages total
text

## 🎯 Evaluation Methodology

### Individual Page Analysis
Each page receives a detailed evaluation for each heuristic:
- **Structured Scoring**: 0-4 scale per heuristic component
- **Evidence-Based**: Specific examples from page content
- **Justification**: Detailed reasoning for scores
- **Confidence Level**: Assessment reliability indicator

### Consolidated Report
The final report aggregates individual evaluations:
- **Average Scores**: Calculated across all evaluated pages
- **Letter Grades**: A (3.5-4.0), B (2.5-3.4), C (1.5-2.4), D (0.5-1.4), F (0-0.4)
- **Pattern Recognition**: Common issues across multiple pages
- **Priority Matrix**: Recommendations sorted by priority, effort, and timeframe

## 🔄 Refresh Functionality
Click "🔄 Refresh" in the sidebar to:
- Clear all stored evaluations
- Reset session state
- Start fresh with new configuration

## 📈 Output Examples

### Real-Time Display

📊 Live Evaluation Progress
⏳ Processing: Error Prevention (6/30)
🌐 Evaluating URL: https://example.com/products
✅ Error Prevention - Completed
✅ User Control - Completed
text

### JSON Output
Raw evaluation data available in expandable section showing:

{
"Error Prevention": {
"https://example.com/": {
"output": "Overall Numeric Score: 3.5/4\nPart 1: Input Validation: 4/4\n..."
}
}
}
text

### HTML Report
Professional report including:
- Executive summary with overall grades
- Detailed heuristic-by-heuristic breakdown
- Prioritized recommendation list
- Business impact analysis
- Quick wins section

## ⚠️ Important Notes

### Cost Considerations
- Uses GPT-4o API (costs apply per evaluation)
- Each page × each heuristic = one API call
- Example: 10 pages × 5 heuristics = 50 API calls
- Set "Max pages" appropriately to control costs

### Performance
- Evaluation time depends on:
  - Number of pages crawled
  - Number of heuristics
  - GPT-4o response time (typically 5-15 seconds per evaluation)
- Example timing: 10 pages × 3 heuristics ≈ 5-15 minutes total

### Best Practices
1. **Start Small**: Test with 2-3 pages first
2. **Focused Prompts**: Write specific, actionable heuristic prompts
3. **Key Pages**: Prioritize important user flows (homepage, checkout, etc.)
4. **Regular Evaluations**: Run after major design changes

## 🛠️ Troubleshooting

### Login Issues
- Verify CSS selectors using browser DevTools (Inspect Element)
- Ensure selectors use # for IDs, . for classes
- Check if site uses CAPTCHA or 2FA (not supported)

### Crawling Issues
- Some sites may block automated browsers
- Reduce "Max pages" if timeouts occur
- Check that start URL is accessible

### API Errors
- Verify OpenAI API key is valid
- Check API usage limits and quotas
- Ensure sufficient credits available
