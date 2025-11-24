import asyncio
import sys
import json
import sys
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import pandas as pd
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import streamlit as st
from openai import OpenAI
from io import BytesIO
import re
import os
import time
from datetime import datetime
from html_generator import generate_html_from_analysis_json, create_fallback_html_report

# Fix for Windows asyncio subprocess issue with Playwright
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()


def convert_analysis_to_csv(analysis_json):
    """Converts the analysis JSON to a CSV string."""
    if not analysis_json:
        return ""

    records = []
    for heuristic_name, data in analysis_json.items():
        record = {
            "Heuristic": heuristic_name,
            "Score": data.get("total_score", ""),
            "Grade": data.get("grade", ""),
            "Performance Level": data.get("performance_level", ""),
            "Pages Evaluated": data.get("pages_evaluated", ""),
            "Definition": data.get("definition", ""),
            "Detailed Assessment": data.get("detailed_assessment", ""),
            "Business Impact": data.get("business_impact", ""),
            "User Experience Impact": data.get("user_experience_impact", ""),
            "Key Strengths": "; ".join(data.get("key_strengths", [])),
            "Key Weaknesses": "; ".join(data.get("key_weaknesses", [])),
            "Quick Wins": "; ".join(data.get("quick_wins", [])),
            "Methodology Notes": data.get("methodology_notes", ""),
            "Confidence Score": data.get("confidence_score", ""),
        }

        for i, subtopic in enumerate(data.get("subtopics", [])):
            record[f"Subtopic {i+1} Name"] = subtopic.get("name", "")
            record[f"Subtopic {i+1} Score"] = subtopic.get("score", "")
            record[f"Subtopic {i+1} Description"] = subtopic.get("description", "")
            record[f"Subtopic {i+1} Impact Level"] = subtopic.get("impact_level", "")

        for i, recommendation in enumerate(data.get("recommendations", [])):
            if isinstance(recommendation, dict):
                record[f"Recommendation {i+1} Priority"] = recommendation.get("priority", "")
                record[f"Recommendation {i+1} Effort"] = recommendation.get("effort", "")
                record[f"Recommendation {i+1} Timeframe"] = recommendation.get("timeframe", "")
                record[f"Recommendation {i+1} Recommendation"] = recommendation.get("recommendation", "")
                record[f"Recommendation {i+1} Expected Outcome"] = recommendation.get("expected_outcome", "")
                record[f"Recommendation {i+1} Implementation Notes"] = recommendation.get("implementation_notes", "")

        records.append(record)

    df = pd.DataFrame(records)
    return df.to_csv(index=False).encode('utf-8')

def fetch_and_map_prompts(uploaded_file):
    if uploaded_file is None:
        st.warning("Please upload an Excel file to proceed.")
        return {}
    try:
        xls = pd.ExcelFile(uploaded_file)
        df = pd.read_excel(xls, sheet_name="AI Prompts")
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        return {}
    mapping = {}
    for idx, row in df.iterrows():
        heuristic = str(row[0]).strip() if pd.notna(row[0]) else None
        prompt = str(row[1]).strip() if pd.notna(row[1]) else None
        if heuristic and prompt:
            mapping[heuristic] = prompt
    return mapping

@st.cache_data
def fetch_wcag_guidelines():
    """
    Fetches WCAG guidelines from the W3C website.
    Note: This scraper is tightly coupled to the HTML structure of the page and may break if the structure changes.
    """
    url = "https://www.w3.org/WAI/WCAG22/quickref/"
    guidelines = {}
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        for h4 in soup.find_all("h4", id=lambda x: x and x.startswith('qr-')):
            title = h4.get_text(strip=True).replace("\n", " ").replace("  ", " ")
            sc_body = h4.find_parent("article").find("div", class_="sc-text")
            if sc_body:
                description = sc_body.get_text(strip=True, separator='\n')
                prompt = f"Evaluate the website against the following WCAG 2.2 Success Criterion:\n\n**{title}**\n\n{description}\n\nPlease provide a detailed analysis of the website's compliance with this criterion. Provide a score from 0-4 (0=fail, 4=exceeds) and justify with examples from the page."
                guidelines[title] = prompt

        return guidelines
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching WCAG guidelines: {e}")
        return {}

def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text(separator=' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_llm_response(response: str) -> str:
    """Format LLM response from OpenAI ChatCompletion object or string for better viewing"""
    if hasattr(response, 'choices') and response.choices:
        text = response.choices[0].message.content
    elif hasattr(response, 'content'):
        text = response.content
    else:
        text = str(response)
    
    text = text.replace("\\n", "\n")
    text = re.sub(r'(\*\*Overall Numeric Score.*?\*\*)', r'\n\1\n', text)
    text = re.sub(r'(\*\*Sub-level Scores:\*\*)', r'\n\1\n', text)
    text = re.sub(r'(\*\*Justification.*?\*\*)', r'\n\1\n', text)
    text = re.sub(r'(\*\*Detailed Answers:\*\*)', r'\n\1\n', text)
    text = re.sub(r'(\*\*Evaluation Scope:\*\*)', r'\n\1\n', text)
    text = re.sub(r'(\*\*Part \d+:)', r'\n\n\1', text)
    text = re.sub(r'(\n|^)(-\s+\*\*)', r'\1\n\2', text)
    text = re.sub(r'(\n|^)(-\s+)', r'\1\n\2', text)
    text = re.sub(r'(\*Confidence:\s*\d+\*)', r'\n  \1\n', text)
    text = re.sub(r'(\*\*\?\*\*\s*)', r'\1\n  ', text)
    text = re.sub(r'(\n)(\d+\.)', r'\1\n\2', text)
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    text = text.strip() + '\n' + '='*60 + '\n'
    return text

def evaluate_heuristic_with_llm(prompt: str, page_content: str) -> str:
    """Evaluate heuristics using OpenAI's API"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    full_prompt = f"{prompt}\n\nPage Content:\n{page_content}"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": """You are an expert UX evaluator conducting heuristic evaluations. 
                    Provide detailed, structured responses with specific scores and evidence-based justifications. 
                    Follow the evaluation criteria exactly as specified in the prompt."""
                },
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ],
            temperature=0,  
            max_tokens=4000
        )
        
        output = response
        summary = format_llm_response(output)
        return summary
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"Error: {str(e)}"

def analyze_each_heuristic_individually_for_report(evaluations: dict) -> dict:
    """Analyze each heuristic individually to prevent crashes with large data"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    final_analysis = {}
    heuristic_names = list(evaluations.keys())
    total_heuristics = len(heuristic_names)
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_container = st.container()
    
    for idx, heuristic_name in enumerate(heuristic_names):
        # Update progress
        progress = (idx) / total_heuristics
        progress_bar.progress(progress)
        
        with status_container:
            st.info(f"🔍 Analyzing {heuristic_name} ({idx + 1}/{total_heuristics})")
        
        pages_data = evaluations[heuristic_name]
        
        # Truncate data if too large to prevent crashes
        truncated_pages_data = {}
        for url, data in pages_data.items():
            output_text = data.get('output', '')
            if len(output_text) > 3000:
                truncated_output = output_text[:3000] + "... [truncated for analysis]"
                truncated_pages_data[url] = {"output": truncated_output}
            else:
                truncated_pages_data[url] = data
        
        evaluated_urls = list(pages_data.keys())
        # Enhanced analysis prompt for more detailed information
        individual_analysis_prompt = f"""
        You are a UX expert analyzing heuristic evaluation data for "{heuristic_name}".

        Heuristic: {heuristic_name}
        Evaluation Data:
        {json.dumps({heuristic_name: truncated_pages_data}, indent=2)}

        Please provide a comprehensive JSON response with the following structure:
        {{
            "heuristic_name": "{heuristic_name}",
            "definition": "<clear definition of what this heuristic measures and why it's important for UX>",
            "total_score": <calculated average score from the data>,
            "max_score": 4,
            "grade": "<letter grade A-F based on score>",
            "performance_level": "<Excellent/Good/Fair/Poor based on score>",
            "detailed_assessment": "<comprehensive 3-4 paragraph assessment explaining the current state, implications, and strategic considerations for this heuristic>",
            "subtopics": [
                {{
                    "name": "<subtopic name extracted from the evaluation data>",
                    "score": <score extracted from evaluation>,
                    "description": "<detailed description of performance, strengths, weaknesses, and recommendations>",
                    "impact_level": "<High/Medium/Low impact on user experience>"
                }}
            ],
            "overall_description": "<comprehensive summary of overall performance, key findings, and strategic recommendations>",
            "key_strengths": ["<strength 1 with specific examples>", "<strength 2 with examples>", "<strength 3>"],
            "key_weaknesses": ["<weakness 1 with specific examples>", "<weakness 2 with examples>", "<weakness 3>"],
            "business_impact": "<how this heuristic performance affects business goals and user satisfaction>",
            "user_experience_impact": "<specific ways this impacts the user's journey and satisfaction>",
            "recommendations": [
                {{
                    "priority": "High/Medium/Low",
                    "effort": "Low/Medium/High",
                    "timeframe": "Immediate/Short-term/Long-term",
                    "recommendation": "<specific actionable recommendation>",
                    "expected_outcome": "<what improvement this would bring>",
                    "implementation_notes": "<how to implement this recommendation>"
                }}
            ],
            "quick_wins": ["<low effort, high impact improvements>", "<another quick win>"],
            "methodology_notes": "<any notes about the evaluation process, limitations, or data quality>",
            "pages_evaluated": {len(pages_data)},
            "analyzed_urls": evaluated_urls,
            "confidence_score": "<High/Medium/Low confidence in this analysis based on data quality>"
        }}

        Analysis Guidelines:
        1. Extract actual scores from patterns like "Overall Numeric Score for [Heuristic]: X", "Part X: [Subtopic Name]: Y"
        2. Calculate grade: A (3.5-4.0), B (2.5-3.4), C (1.5-2.4), D (0.5-1.4), F (0-0.4)
        3. Provide specific, actionable insights based on the evaluation data
        4. Write a detailed_assessment that explains the strategic implications and current state comprehensively
        5. Focus on business impact and user experience outcomes
        6. Be comprehensive but practical in recommendations
        7. Include implementation guidance where possible
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior UX consultant specializing in comprehensive heuristic evaluations and report generation. You excel at:
                        1. Extracting and analyzing quantitative scores from evaluation data
                        2. Providing actionable insights with business impact consideration
                        3. Creating structured, professional analysis reports suitable for stakeholders
                        4. Identifying patterns, priorities, and strategic recommendations
                        5. Understanding the limitations of heuristic evaluations
                        6. Writing detailed strategic assessments that explain implications and context
                        
                        Always return valid JSON with specific, actionable recommendations. Consider both technical implementation and business impact in your analysis."""
                    },
                    {
                        "role": "user",
                        "content": individual_analysis_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=3500
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # More robust JSON cleaning
            if analysis_text.startswith("```"):
                lines = analysis_text.split('\n')
                start_idx = 0
                end_idx = len(lines)
                for i, line in enumerate(lines):
                    if line.strip().startswith('{'):
                        start_idx = i
                        break
                for i in range(len(lines)-1, -1, -1):
                    if lines[i].strip().endswith('}'):
                        end_idx = i + 1
                        break
                analysis_text = '\n'.join(lines[start_idx:end_idx])
            
            try:
                heuristic_analysis = json.loads(analysis_text)
                heuristic_analysis["analyzed_urls"] = evaluated_urls
                final_analysis[heuristic_name] = heuristic_analysis
                with status_container:
                    st.success(f"✅ {heuristic_name} analyzed successfully")
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error for {heuristic_name}: {e}")
                with status_container:
                    st.warning(f"JSON parsing failed for {heuristic_name}, using fallback")
                final_analysis[heuristic_name] = create_individual_fallback_analysis(heuristic_name, pages_data)
                
        except Exception as e:
            print(f"Error analyzing {heuristic_name}: {e}")
            with status_container:
                st.error(f"Error analyzing {heuristic_name}: {str(e)}")
            final_analysis[heuristic_name] = create_individual_fallback_analysis(heuristic_name, pages_data)
        
        time.sleep(1)
    
    progress_bar.progress(1.0)
    status_container.success("All heuristics analyzed successfully!")
    
    return final_analysis

def create_individual_fallback_analysis(heuristic_name: str, pages_data: dict) -> dict:
    """Create fallback analysis for a specific heuristic"""
    return {
        "heuristic_name": heuristic_name,
        "definition": f"{heuristic_name} measures the usability and user experience quality of the interface design.",
        "total_score": 2.0,
        "max_score": 4,
        "grade": "C",
        "performance_level": "Fair",
        "detailed_assessment": f"The {heuristic_name} heuristic evaluation encountered technical limitations during processing. Based on available data, the implementation appears to meet basic functional requirements but shows room for enhancement. This assessment suggests that while core functionality is present, there are likely opportunities to improve user experience through more detailed analysis and targeted improvements. The current state indicates a moderate level of usability that could benefit from focused attention and strategic enhancements.",
        "subtopics": [
            {
                "name": "Overall Assessment", 
                "score": 2, 
                "description": f"Basic {heuristic_name} functionality present but needs improvement.",
                "impact_level": "Medium"
            }
        ],
        "overall_description": f"The {heuristic_name} heuristic shows basic implementation with room for improvement.",
        "key_strengths": ["Basic functionality present", "Core features working"],
        "key_weaknesses": ["Limited advanced features", "Inconsistent implementation"],
        "business_impact": "Moderate impact on user satisfaction and business goals.",
        "user_experience_impact": "Users can complete basic tasks but may encounter friction.",
        "recommendations": [
            {
                "priority": "Medium",
                "effort": "Medium",
                "timeframe": "Short-term",
                "recommendation": "Conduct detailed manual review of this heuristic",
                "expected_outcome": "Better understanding of specific issues and improvements needed",
                "implementation_notes": "Assign UX team to evaluate specific user flows"
            }
        ],
        "quick_wins": ["Manual review of key pages", "User feedback collection"],
        "methodology_notes": "Fallback analysis due to processing limitations. Manual review recommended for accurate assessment.",
        "pages_evaluated": len(pages_data),
        "analyzed_urls": list(pages_data.keys()),
        "confidence_score": "Low"
    }

async def login_and_crawl_all_pages(url: str, username: str, password: str, login_url: str, username_selector: str, password_selector: str, submit_selector: str, additional_urls: list[str] = None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Block heavy resources to speed up crawling
        async def route_handler(route):
            if route.request.resource_type in {"image", "media", "font", "stylesheet"}:
                return await route.abort()
            return await route.continue_()

        await context.route("**/*", route_handler)

        page = await context.new_page()
        page.set_default_navigation_timeout(120000)
        page.set_default_timeout(120000)

        visited_urls = set()
        url_to_content = {}
        max_pages = 50
        max_depth = 2

        # Login flow with more lenient waits
        try:
            await page.goto(login_url, wait_until="domcontentloaded", timeout=120000)
            await page.fill(username_selector, username)
            await page.fill(password_selector, password)
            await page.click(submit_selector)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(500)
        except Exception as e:
            print(f"Login navigation error: {e}")

        base_domain = urlparse(login_url).netloc

        async def crawl(current_url, depth):
            if current_url in visited_urls or len(visited_urls) >= max_pages or depth > max_depth:
                return
            visited_urls.add(current_url)
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_timeout(300)
            except Exception as e:
                print(f"Timeout or navigation error for {current_url}: {e}")
                return

            try:
                content = await page.content()
                cleaned_content = clean_html_content(content)
                url_to_content[current_url] = cleaned_content
                print(f"Crawled {current_url} with cleaned content length {len(cleaned_content)}")
            except Exception as e:
                print(f"Content extraction error at {current_url}: {e}")
                return

            try:
                links = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            except Exception as e:
                print(f"Link extraction error at {current_url}: {e}")
                return

            for link in links:
                link_domain = urlparse(link).netloc
                if link_domain == base_domain and not link.startswith(("mailto:", "javascript:")):
                    await crawl(link, depth + 1)

        await crawl(url, 0)

        if additional_urls:
            for additional_url in additional_urls:
                if additional_url not in visited_urls:
                    await crawl(additional_url, 0)

        await browser.close()
        return url_to_content

async def crawl_all_pages_no_login(start_url: str, additional_urls: list[str] = None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Block heavy resources to reduce timeouts
        async def route_handler(route):
            if route.request.resource_type in {"image", "media", "font", "stylesheet"}:
                return await route.abort()
            return await route.continue_()

        await context.route("**/*", route_handler)

        page = await context.new_page()
        page.set_default_navigation_timeout(120000)
        page.set_default_timeout(120000)

        visited_urls = set()
        url_to_content = {}
        base_domain = urlparse(start_url).netloc
        max_pages = 50
        max_depth = 2

        async def crawl(current_url, depth):
            if current_url in visited_urls or len(visited_urls) >= max_pages or depth > max_depth:
                return
            visited_urls.add(current_url)
            try:
                await page.goto(current_url, wait_until="domcontentloaded", timeout=120000)
                await page.wait_for_timeout(300)
            except Exception as e:
                print(f"Timeout or navigation error for {current_url}: {e}")
                return

            try:
                content = await page.content()
                cleaned_content = clean_html_content(content)
                url_to_content[current_url] = cleaned_content
                print(f"Crawled {current_url} with cleaned content length {len(cleaned_content)}")
            except Exception as e:
                print(f"Content extraction error at {current_url}: {e}")
                return

            try:
                links = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            except Exception as e:
                print(f"Link extraction error at {current_url}: {e}")
                return

            for link in links:
                link_domain = urlparse(link).netloc
                if link_domain == base_domain and not link.startswith(("mailto:", "javascript:")):
                    await crawl(link, depth + 1)

        await crawl(start_url, 0)

        if additional_urls:
            for additional_url in additional_urls:
                if additional_url not in visited_urls:
                    await crawl(additional_url, 0)

        await browser.close()
        return url_to_content


async def crawl_specific_urls(urls: list[str], login_url: str = None, username: str = None, password: str = None, username_selector: str = None, password_selector: str = None, submit_selector: str = None, no_login: bool = False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        page.set_default_navigation_timeout(120000)

        if not no_login and login_url:
            try:
                await page.goto(login_url, wait_until="domcontentloaded")
                if username and password and username_selector and password_selector and submit_selector:
                    await page.fill(username_selector, username)
                    await page.fill(password_selector, password)
                    await page.click(submit_selector)
                    await page.wait_for_load_state("domcontentloaded")
            except Exception as e:
                print(f"Login failed: {e}")
                await browser.close()
                return {}

        url_to_content = {}
        for url in urls:
            try:
                await page.goto(url, wait_until="domcontentloaded")
                content = await page.content()
                cleaned_content = clean_html_content(content)
                url_to_content[url] = cleaned_content
            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

        await browser.close()
        return url_to_content


def run_crawl_and_evaluate_stream(start_url, username, password, login_url, username_selector, password_selector, submit_selector, prompt_map, specific_urls=None, heuristic_url_map=None):
    evaluations = {}

    # Create containers for live updates
    st.subheader("📊 Live Evaluation Progress")
    progress_container = st.container()
    results_container = st.container()

    # Combine all URLs to be crawled
    all_urls_to_crawl = set(specific_urls or [])
    if heuristic_url_map:
        for urls in heuristic_url_map.values():
            all_urls_to_crawl.update(urls)

    # Crawl the main site and any additional URLs
    crawled_content = asyncio.run(
        login_and_crawl_all_pages(
            url=login_url,
            username=username,
            password=password,
            login_url=login_url,
            username_selector=username_selector,
            password_selector=password_selector,
            submit_selector=submit_selector,
            additional_urls=list(all_urls_to_crawl)
        )
    )

    total_evaluations = 0
    for heuristic in prompt_map:
        if heuristic_url_map and heuristic in heuristic_url_map:
            total_evaluations += len(heuristic_url_map[heuristic])
        else:
            total_evaluations += len(crawled_content)
    
    current_eval = 0

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    for heuristic, prompt in prompt_map.items():
        urls_to_evaluate = (heuristic_url_map or {}).get(heuristic, crawled_content.keys())
        
        for url in urls_to_evaluate:
            if url not in crawled_content:
                st.warning(f"URL {url} specified for {heuristic} was not crawled. Skipping.")
                continue

            content = crawled_content[url]
            current_eval += 1
            
            with progress_container:
                progress_bar.progress(current_eval / total_evaluations if total_evaluations > 0 else 0)
                status_text.info(f"⏳ Processing: **{heuristic}** on {url} ({current_eval}/{total_evaluations})")

            prompt_with_url = prompt.replace("[Enter Website URL Here]", url)
            result = evaluate_heuristic_with_llm(prompt_with_url, content)
            
            if heuristic not in evaluations:
                evaluations[heuristic] = {}
            evaluations[heuristic][url] = {"output": result}

            with results_container:
                with st.expander(f"✅ **{heuristic}** on `{url}` - Completed", expanded=False):
                    st.text_area(
                        "Evaluation Result",
                        value=result,
                        height=300,
                        key=f"{heuristic}_{url}_{current_eval}"
                    )
                    st.markdown("---")

    with progress_container:
        progress_bar.progress(1.0)
        status_text.success(f"✅ All evaluations complete! ({total_evaluations} total)")

    return evaluations

def run_crawl_and_evaluate_public(start_url, prompt_map, max_pages_to_evaluate: int = 1, specific_urls=None, heuristic_url_map=None):
    evaluations = {}

    st.subheader("📊 Live Evaluation Progress")
    progress_container = st.container()
    results_container = st.container()

    all_urls_to_crawl = set(specific_urls or [])
    if heuristic_url_map:
        for urls in heuristic_url_map.values():
            all_urls_to_crawl.update(urls)

    crawled_content = asyncio.run(crawl_all_pages_no_login(start_url, additional_urls=list(all_urls_to_crawl)))

    total_evaluations = 0
    for heuristic in prompt_map:
        if heuristic_url_map and heuristic in heuristic_url_map:
            total_evaluations += len(heuristic_url_map[heuristic])
        else:
            total_evaluations += len(crawled_content)

    current_eval = 0

    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()

    for heuristic, prompt in prompt_map.items():
        urls_to_evaluate = (heuristic_url_map or {}).get(heuristic, crawled_content.keys())

        for url in urls_to_evaluate:
            if url not in crawled_content:
                st.warning(f"URL {url} specified for {heuristic} was not crawled. Skipping.")
                continue
            
            content = crawled_content[url]
            current_eval += 1

            with progress_container:
                progress_bar.progress(current_eval / total_evaluations if total_evaluations > 0 else 0)
                status_text.info(f"⏳ Processing: **{heuristic}** on {url} ({current_eval}/{total_evaluations})")

            prompt_with_url = prompt.replace("[Enter Website URL Here]", url)
            result = evaluate_heuristic_with_llm(prompt_with_url, content)

            if heuristic not in evaluations:
                evaluations[heuristic] = {}
            evaluations[heuristic][url] = {"output": result}

            with results_container:
                with st.expander(f"✅ **{heuristic}** on `{url}` - Completed", expanded=False):
                    st.text_area(
                        "Evaluation Result",
                        value=result,
                        height=300,
                        key=f"{heuristic}_{url}_{current_eval}"
                    )
                    st.markdown("---")

    with progress_container:
        progress_bar.progress(1.0)
        status_text.success(f"✅ All evaluations complete! ({total_evaluations} total)")

    return evaluations

def main():
    st.header("Heuristic Evaluation")


    with st.sidebar:
        st.title("Upload Excel file")
        uploaded_file = st.file_uploader("Upload Heuristic Excel file with AI Prompts sheet", type=["xlsx", "xls"])

        # Add WCAG Guidelines section
        st.title("WCAG Guidelines")
        wcag_guidelines = fetch_wcag_guidelines()
        if wcag_guidelines:
            with st.expander("Select WCAG Guidelines to Evaluate"):
                selected_wcag_guidelines = []
                for guideline in wcag_guidelines.keys():
                    if st.checkbox(guideline, key=f"wcag_{guideline}"):
                        selected_wcag_guidelines.append(guideline)
        else:
            st.warning("Could not load WCAG guidelines.")

        st.title("Target Website")
        requires_login = st.checkbox("Site requires login", value=True)
        start_url = None
        max_pages_to_evaluate = st.number_input("Max pages to evaluate", min_value=1, max_value=100, value=1)
        specific_urls_input = st.text_area("Enter specific URLs to evaluate (one per line)")
        
        # Per-heuristic URL assignment
        assign_per_heuristic = st.checkbox("Assign URLs to specific heuristics")
        heuristic_url_map = {}

        # FIX: Initialize login_url with a default value
        login_url = None
        username = None
        password = None
        username_selector = None
        password_selector = None
        submit_selector = None
        
        if requires_login:
            login_url = st.text_input("Login URL", value="https://www.saucedemo.com/")
            username = st.text_input("Username", value="standard_user")
            password = st.text_input("Password", value="secret_sauce", type="password")
        
            username_selector = st.text_input(
                "Username Selector", 
                value="#user-name",
                help="CSS selector for the username input field. Right-click on the username field in the login page, select 'Inspect Element', then copy the id (#id) or class (.class) or tag selector. Example: #username, .username-field, input[name='username']"
            )
            
            password_selector = st.text_input(
                "Password Selector", 
                value="#password",
                help="CSS selector for the password input field. Right-click on the password field in the login page, select 'Inspect Element', then copy the id (#id) or class (.class) or tag selector. Example: #password, .password-field, input[type='password']"
            )
            
            submit_selector = st.text_input(
                "Submit Button Selector", 
                value="#login-button",
                help="CSS selector for the login/submit button. Right-click on the login button, select 'Inspect Element', then copy the id (#id) or class (.class) or tag selector. Example: #login-btn, .submit-button, button[type='submit']"
            )
        else:
            # For public sites: show site URL input when login not required
            start_url = st.text_input("Site URL", value="https://www.saucedemo.com/", help="Enter the public site URL to crawl")

        
        # Refresh button
        st.markdown("---")
        if st.button("🔄 Refresh", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


    if uploaded_file:
        prompt_map = fetch_and_map_prompts(uploaded_file)

        # Combine heuristics from Excel with selected WCAG guidelines
        if 'selected_wcag_guidelines' in locals() and selected_wcag_guidelines:
            for guideline in selected_wcag_guidelines:
                if guideline in wcag_guidelines:
                    prompt_map[guideline] = wcag_guidelines[guideline]

        st.session_state.prompt_map = prompt_map
        st.write("Loaded heuristics and prompts:", list(prompt_map.keys()))

        if assign_per_heuristic:
            if "prompt_map" in st.session_state and st.session_state.prompt_map:
                st.subheader("Assign URLs to Heuristics")
                for heuristic in st.session_state.prompt_map.keys():
                    urls = st.text_area(f"URLs for {heuristic}", key=f"urls_{heuristic}")
                    if urls:
                        heuristic_url_map[heuristic] = [url.strip() for url in urls.split("\n") if url.strip()]

        if st.button("Run Crawl and Evaluate"):
            if not st.session_state.prompt_map:
                st.error("Please upload an Excel file with prompts before running the evaluation.")
            else:
                specific_urls = [url.strip() for url in specific_urls_input.split("\n") if url.strip()]
                with st.spinner("Crawling site and evaluating..."):
                    if requires_login:
                        evaluations = run_crawl_and_evaluate_stream(
                            start_url, username, password, login_url,
                            username_selector, password_selector, submit_selector, st.session_state.prompt_map,
                            specific_urls=specific_urls,
                            heuristic_url_map=heuristic_url_map
                        )
                    else:
                        evaluations = run_crawl_and_evaluate_public(
                            start_url,
                            st.session_state.prompt_map,
                            max_pages_to_evaluate=int(max_pages_to_evaluate),
                            specific_urls=specific_urls,
                            heuristic_url_map=heuristic_url_map
                        )
                    st.session_state["evaluations"] = evaluations
                    st.success("Evaluation complete")
                    st.json(st.session_state["evaluations"])

        if "evaluations" in st.session_state:
            st.subheader("Saved Evaluation Output")

            if st.button("Generate Enhanced Report (HTML)"):
                with st.spinner("Generating comprehensive HTML report..."):
                    analysis_json = analyze_each_heuristic_individually_for_report(st.session_state["evaluations"])
                    st.session_state["analysis_json"] = analysis_json
                    
                    if not analysis_json:
                        st.error("Failed to generate analysis. Please try again.")
                        return
                    
                    # FIX: Use login_url if available, otherwise use start_url
                    url_to_parse = login_url if (requires_login and login_url) else start_url
                    site_name = url_to_parse.replace("https://", "").replace("http://", "").split('/')[0]
                    
                    html_report = generate_html_from_analysis_json(
                        analysis_json, 
                        site_name=site_name,
                        site_description="Comprehensive UX Heuristic Analysis"
                    )
                    
                    st.session_state["html_report"] = html_report

        if "html_report" in st.session_state and st.session_state["html_report"]:
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📄 Download Enhanced HTML Report",
                    data=st.session_state["html_report"],
                    file_name="enhanced_heuristic_evaluation_report.html",
                    mime="text/html",
                )
            with col2:
                if "analysis_json" in st.session_state:
                    csv_data = convert_analysis_to_csv(st.session_state["analysis_json"])
                    st.download_button(
                        label="📄 Download CSV Report",
                        data=csv_data,
                        file_name="heuristic_evaluation_report.csv",
                        mime="text/csv",
                    )
    else:
        st.info("Please upload an Excel file to start.")



if __name__ == "__main__":
    main()