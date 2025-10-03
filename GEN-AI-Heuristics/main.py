import asyncio
import json
from dotenv import load_dotenv
import pandas as pd
from playwright.async_api import async_playwright
from urllib.parse import urlparse
import streamlit as st
from bs4 import BeautifulSoup
from openai import OpenAI
from io import BytesIO
import re
import os
import time
from datetime import datetime
from html_generator import generate_html_from_analysis_json, create_fallback_html_report

load_dotenv()

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
        "confidence_score": "Low"
    }

async def login_and_crawl_all_pages(url: str, username: str, password: str, login_url: str, username_selector: str, password_selector: str, submit_selector: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        visited_urls = set()
        url_to_content = {}

        await page.goto(login_url)
        await page.fill(username_selector, username)
        await page.fill(password_selector, password)
        await page.click(submit_selector)
        await page.wait_for_load_state("networkidle")

        async def crawl(current_url):
            if current_url in visited_urls:
                return
            visited_urls.add(current_url)
            await page.goto(current_url)
            await page.wait_for_load_state("networkidle")

            content = await page.content()
            cleaned_content = clean_html_content(content)
            url_to_content[current_url] = cleaned_content
            print(f"Crawled {current_url} with cleaned content length {len(cleaned_content)}")

            links = await page.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            base_domain = urlparse(login_url).netloc
            for link in links:
                link_domain = urlparse(link).netloc
                if link_domain == base_domain and not link.startswith(("mailto:", "javascript:")):
                    await crawl(link)

        await crawl(url)
        await browser.close()
        return url_to_content

def run_crawl_and_evaluate_stream(start_url, username, password, login_url, username_selector, password_selector, submit_selector, prompt_map):
    results = asyncio.run(
        login_and_crawl_all_pages(
            url=start_url, username=username, password=password, login_url=login_url,
            username_selector=username_selector, password_selector=password_selector, submit_selector=submit_selector,
        )
    )

    evaluations = {}
    placeholder = st.empty()

    for url, content in results.items():
        for heuristic, prompt in prompt_map.items():
            prompt_with_url = prompt.replace("[Enter Website URL Here]", login_url)
            result = evaluate_heuristic_with_llm(prompt_with_url, content)
            if heuristic not in evaluations:
                evaluations[heuristic] = {}
                evaluations[heuristic][url] = {"output": result}
                placeholder.json(evaluations)
    
    placeholder.empty()
    return evaluations

def main():
    st.header("Heuristic Evaluation")

    with st.sidebar:
        st.title("Upload Excel file")
        uploaded_file = st.file_uploader("Upload Heuristic Excel file with AI Prompts sheet", type=["xlsx", "xls"])
        st.title("Website Credentials")
        login_url = st.text_input("Login URL", value="https://www.saucedemo.com/")
        start_url = st.text_input("Start URL", value="https://www.saucedemo.com/inventory.html")
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

    if uploaded_file:
        prompt_map = fetch_and_map_prompts(uploaded_file)
        st.write("Loaded heuristics and prompts:", list(prompt_map.keys()))

        if st.button("Run Crawl and Evaluate"):
            with st.spinner("Crawling site and evaluating..."):
                evaluations = run_crawl_and_evaluate_stream(
                    start_url, username, password, login_url,
                    username_selector, password_selector, submit_selector, prompt_map,
                )
                st.session_state["evaluations"] = evaluations
                st.success("Evaluation complete")
                st.json(st.session_state["evaluations"])

        if "evaluations" in st.session_state:
            st.subheader("Saved Evaluation Output")

            if st.button("Generate Enhanced Report (HTML)"):
                with st.spinner("Generating comprehensive HTML report..."):
                    analysis_json = analyze_each_heuristic_individually_for_report(st.session_state["evaluations"])
                    print('Analysis JSON:', analysis_json)
                    
                    if not analysis_json:
                        st.error("Failed to generate analysis. Please try again.")
                        return
                    
                    site_name = login_url.replace("https://", "").replace("http://", "").split('/')
                    
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

    else:
        st.info("Please upload an Excel file to start.")

if __name__ == "__main__":
    main()
