"""
HTML and CSS generation for heuristic evaluation reports.
Contains all HTML templates, CSS styles, and content generation functions.
"""

from datetime import datetime
import streamlit as st

def generate_overall_assessment_text(analysis_json: dict, average_score: float, performance_level: str, overall_grade: str) -> str:
    """Generate comprehensive overall assessment text focused on strengths, improvements, and issues"""
    
    # Analyze performance distribution
    excellent_heuristics = []
    good_heuristics = []
    fair_heuristics = []
    poor_heuristics = []
    
    for heuristic_name, data in analysis_json.items():
        score = data.get('total_score', 0)
        if score >= 3.5:
            excellent_heuristics.append(heuristic_name)
        elif score >= 2.5:
            good_heuristics.append(heuristic_name)
        elif score >= 1.5:
            fair_heuristics.append(heuristic_name)
        else:
            poor_heuristics.append(heuristic_name)
    
    # Collect all strengths, weaknesses, and issues
    all_strengths = []
    all_improvements = []
    critical_issues = []
    high_priority_recs = []
    
    for data in analysis_json.values():
        # Collect strengths
        strengths = data.get('key_strengths', [])
        for strength in strengths[:2]:  # Top 2 per heuristic
            if strength not in all_strengths:
                all_strengths.append(strength)
        
        # Collect weaknesses as improvement areas
        weaknesses = data.get('key_weaknesses', [])
        for weakness in weaknesses[:2]:  # Top 2 per heuristic
            if weakness not in all_improvements:
                all_improvements.append(weakness)
        
        # Collect high priority recommendations as critical issues
        recommendations = data.get('recommendations', [])
        for rec in recommendations:
            if isinstance(rec, dict) and rec.get('priority') == 'High':
                rec_text = rec.get('recommendation', '')
                if rec_text and rec_text not in high_priority_recs:
                    high_priority_recs.append(rec_text)
        
        # Identify critical issues from poor performing heuristics
        if data.get('total_score', 0) < 1.5:
            heuristic_name = data.get('heuristic_name', '')
            if heuristic_name:
                critical_issues.append(f"Critical usability issues in {heuristic_name}")

    assessment_text = f"""
    <div style="background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 12px; margin: 1.5rem 0;">
        <p style="font-size: 1.15rem; line-height: 1.8; margin-bottom: 1.5rem;">
            <strong>This comprehensive heuristic evaluation reveals that the website demonstrates {performance_level} usability performance 
            with an overall grade of {overall_grade} ({average_score}/4.0).</strong> The evaluation assessed {len(analysis_json)} critical 
            usability heuristics across multiple pages, providing a detailed analysis of current strengths, improvement opportunities, 
            and critical issues that impact user experience.
        </p>
        
        <div style="background: #ecfdf5; border-left: 4px solid #10b981; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
            <h4 style="color: #065f46; margin-top: 0; margin-bottom: 1rem;">✅ What the Website Does Well:</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">"""

    # Add top strengths
    if excellent_heuristics:
        assessment_text += f"<li><strong>Excellent Performance Areas:</strong> {', '.join(excellent_heuristics)} demonstrate outstanding usability implementation</li>"
    
    if good_heuristics:
        assessment_text += f"<li><strong>Good Implementation:</strong> {', '.join(good_heuristics)} show solid user experience design</li>"
    
    # Add specific strengths
    for strength in all_strengths[:4]:  # Top 4 overall strengths
        assessment_text += f"<li>{strength}</li>"
    
    if not all_strengths and not excellent_heuristics and not good_heuristics:
        assessment_text += "<li>Basic functionality is present and operational</li>"
        assessment_text += "<li>Core user tasks can be completed</li>"

    assessment_text += """
            </ul>
        </div>
        
        <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
            <h4 style="color: #92400e; margin-top: 0; margin-bottom: 1rem;">🔧 Areas for Improvement:</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">"""

    # Add improvement areas
    if fair_heuristics:
        assessment_text += f"<li><strong>Moderate Enhancement Needed:</strong> {', '.join(fair_heuristics)} require focused attention to improve user experience</li>"
    
    # Add specific improvements
    for improvement in all_improvements[:5]:  # Top 5 improvement areas
        assessment_text += f"<li>{improvement}</li>"
    
    if not all_improvements and not fair_heuristics:
        assessment_text += "<li>Enhanced user interface consistency</li>"
        assessment_text += "<li>Improved user guidance and feedback</li>"

    assessment_text += """
            </ul>
        </div>"""

    # Add critical issues section if there are any
    if poor_heuristics or critical_issues or high_priority_recs:
        assessment_text += """
        <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
            <h4 style="color: #991b1b; margin-top: 0; margin-bottom: 1rem;">⚠️ Critical Issues Requiring Immediate Attention:</h4>
            <ul style="margin: 0; padding-left: 1.5rem;">"""
        
        if poor_heuristics:
            assessment_text += f"<li><strong>Poor Performance Areas:</strong> {', '.join(poor_heuristics)} show significant usability problems that impact user satisfaction</li>"
        
        # Add critical issues
        for issue in critical_issues[:3]:
            assessment_text += f"<li>{issue}</li>"
        
        # Add high priority recommendations as issues
        for rec in high_priority_recs[:3]:
            assessment_text += f"<li>{rec}</li>"
        
        if not poor_heuristics and not critical_issues and not high_priority_recs:
            assessment_text += "<li>No critical usability issues identified that require immediate attention</li>"
        
        assessment_text += """
            </ul>
        </div>"""

    # Summary and strategic implications
    if average_score >= 3.0:
        strategic_text = "The website demonstrates strong usability fundamentals with opportunities for refinement and optimization to achieve excellence."
    elif average_score >= 2.0:
        strategic_text = "The website provides adequate user experience with clear opportunities for targeted improvements that will enhance user satisfaction and engagement."
    else:
        strategic_text = "The website requires systematic attention to usability issues to meet user expectations and achieve business objectives effectively."

    assessment_text += f"""
        <p style="font-size: 1.1rem; line-height: 1.7; margin-top: 1.5rem; margin-bottom: 1rem; padding: 1.5rem; background: #f0f9ff; border-radius: 8px;">
            <strong>Strategic Summary:</strong> {strategic_text} With {len(excellent_heuristics + good_heuristics)} heuristics performing well 
            and {len(fair_heuristics + poor_heuristics)} requiring attention, the focus should be on {"maintaining strengths while addressing specific improvement areas" if average_score >= 2.5 else "systematic enhancement across multiple usability dimensions"}.
        </p>
        
        <p style="font-size: 1.05rem; line-height: 1.7; margin: 0;">
            <strong>Next Steps:</strong> Prioritize addressing critical issues first, then focus on the improvement areas identified above. 
            Regular user testing and iterative improvements will help maintain and enhance the positive aspects while resolving usability challenges.
        </p>
    </div>
    """
    
    return assessment_text

def generate_conclusion_content(analysis_json: dict, average_score: float, max_score: int) -> str:
    """Generate dynamic conclusion content based on analysis data"""
    all_recommendations = []
    priority_areas = []
    quick_wins = []
    
    for heuristic_name, data in analysis_json.items():
        try:
            score = float(data.get('total_score', 0))
        except (ValueError, TypeError):
            score = 0.0
            
        if score < average_score:
            priority_areas.append(heuristic_name.lower())
        
        # Collect recommendations and quick wins
        recommendations = data.get('recommendations', [])
        for rec in recommendations:
            if isinstance(rec, dict):
                rec_text = rec.get('recommendation', '')
                if rec_text:
                    all_recommendations.append(str(rec_text))
            else:
                all_recommendations.append(str(rec))
        
        quick_wins.extend(data.get('quick_wins', []))
    
    # Generate priority areas text
    if priority_areas:
        if len(priority_areas) == 1:
            priority_text = f"Priority should be given to improving {priority_areas}"
        elif len(priority_areas) == 2:
            priority_text = f"Priority areas for enhancement include {priority_areas} and {priority_areas}"[1]
        else:
            priority_text = f"Priority areas for enhancement include {', '.join(priority_areas[:-1])}, and {priority_areas[-1]}"
    else:
        priority_text = "All heuristic areas show consistent performance levels"
    
    conclusion_content = f"<p>{priority_text}."
    
    # Add recommendation summary
    if all_recommendations:
        top_recommendations = all_recommendations[:3]
        if len(top_recommendations) == 1:
            conclusion_content += f" Key recommendation: {str(top_recommendations).lower()}."
        elif len(top_recommendations) > 1:
            safe_recs = [str(rec).lower() for rec in top_recommendations[:-1]]
            last_rec = str(top_recommendations[-1]).lower()
            conclusion_content += f" Key recommendations include {', '.join(safe_recs)}, and {last_rec}."
    
    conclusion_content += "</p>"
    
    # Add quick wins section
    if quick_wins:
        conclusion_content += "<h4>🚀 Immediate Quick Wins:</h4><ul>"
        for win in quick_wins[:5]:  # Show top 5 quick wins
            conclusion_content += f"<li>{win}</li>"
        conclusion_content += "</ul>"
    
    return conclusion_content

def generate_html_from_analysis_json(analysis_json: dict, site_name: str = "Website", site_description: str = "UX Heuristic Analysis") -> str:
    """Generate enhanced HTML report with comprehensive overall assessment"""
    
    if analysis_json is None:
        st.error("Analysis data is not available. Please try running the evaluation again.")
        return create_fallback_html_report(site_name, site_description)
    
    if not isinstance(analysis_json, dict) or len(analysis_json) == 0:
        st.error("Invalid or empty analysis data received.")
        return create_fallback_html_report(site_name, site_description)

    # Calculate overall statistics
    total_score = 0
    max_score = 4
    heuristic_count = len(analysis_json)
    
    for heuristic_name, data in analysis_json.items():
        try:
            score = float(data.get('total_score', 0))
            total_score += score
        except (ValueError, TypeError):
            pass
    
    average_score = round(total_score / heuristic_count, 1) if heuristic_count > 0 else 0
    
    # Determine overall grade and performance level
    if average_score >= 3.5:
        overall_grade = "A"
        performance_level = "excellent"
        overall_assessment = "provides strong user experience with well-implemented heuristic principles"
        status_color = "#10b981"
    elif average_score >= 2.5:
        overall_grade = "B"
        performance_level = "good"
        overall_assessment = "provides adequate user experience with room for targeted improvements"
        status_color = "#3b82f6"
    elif average_score >= 1.5:
        overall_grade = "C"
        performance_level = "fair"
        overall_assessment = "shows basic functionality but requires focused attention in several areas"
        status_color = "#f59e0b"
    elif average_score >= 0.5:
        overall_grade = "D"
        performance_level = "poor"
        overall_assessment = "has significant usability issues that need immediate attention"
        status_color = "#ef4444"
    else:
        overall_grade = "F"
        performance_level = "failing"
        overall_assessment = "requires comprehensive redesign and usability improvements"
        status_color = "#dc2626"

    # Generate comprehensive assessment text
    overall_assessment_content = generate_overall_assessment_text(analysis_json, average_score, performance_level, overall_grade)

    # Generate the complete HTML template
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Heuristic Evaluation Report – {site_name}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        html {{ box-sizing: border-box; font-size: 16px; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{
            font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
            background: #f8f9fb; color: #222; margin: 0; padding: 0 0 3rem 0; line-height: 1.6;
        }}
        header {{
            background: #2d3e50; color: #fff; padding: 2rem 0 1rem 0;
            text-align: center; margin-bottom: 2rem;
        }}
        h1 {{ margin: 0 0 0.5rem 0; font-size: 2.2rem; letter-spacing: 0.02em; }}
        h2, h3 {{ color: #2d3e50; margin-top: 2.5rem; margin-bottom: 1rem; }}
        h3 {{ margin-top: 2rem; font-size: 1.25rem; }}
        h4 {{ color: #374151; margin-top: 1.5rem; margin-bottom: 0.5rem; }}
        section {{
            max-width: 1000px; margin: 0 auto 2.5rem auto; background: #fff;
            border-radius: 8px; box-shadow: 0 2px 8px rgba(44,62,80,0.07); padding: 2rem 2.5rem;
        }}
        .executive-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: black; border-radius: 12px; padding: 2rem; margin-bottom: 2rem;
        }}
        .overall-grade {{
            display: inline-block; background: {status_color}; color: white;
            padding: 0.5rem 1rem; border-radius: 8px; font-size: 1.5rem; font-weight: bold;
            margin-right: 1rem;
        }}
        .stats-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem; margin: 1.5rem 0;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;
            text-align: center; backdrop-filter: blur(10px);
        }}
        .stat-number {{ font-size: 2rem; font-weight: bold; display: block; }}
        .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}
        .instructions {{
            background: #f0f9ff; border-left: 5px solid #0ea5e9; padding: 1.5rem;
            border-radius: 7px; margin: 1.5rem 0;
        }}
        .alert {{ 
            background: #fef3c7; border-left: 5px solid #f59e0b; padding: 1rem; 
            border-radius: 7px; margin: 1rem 0; 
        }}
        table {{ 
            width: 100%; border-collapse: collapse; margin: 1.5rem 0 2rem 0; 
            background: #fafbfc; border-radius: 6px; overflow: hidden; 
        }}
        th, td {{ padding: 0.75rem 1rem; text-align: left; }}
        th {{ 
            background: #e9ecef; font-weight: 600; color: #2d3e50; 
            border-bottom: 2px solid #d1d5db; 
        }}
        td {{ border-bottom: 1px solid #e5e7eb; }}
        .grade-cell {{ text-align: center; font-weight: bold; font-size: 1.1rem; }}
        .grade-A {{ color: #10b981; }}
        .grade-B {{ color: #3b82f6; }}
        .grade-C {{ color: #f59e0b; }}
        .grade-D {{ color: #ef4444; }}
        .grade-F {{ color: #dc2626; }}
        .bar-chart-container {{
            margin: 1.5rem 0 2rem 0; padding: 1.5rem 1rem 1.5rem 2.5rem;
            background: #f4f6fa; border-radius: 8px; overflow-x: auto;
        }}
        .bar-chart {{ width: 100%; max-width: 700px; margin: 0 auto; position: relative; }}
        .bar-row {{ display: flex; align-items: center; margin-bottom: 1.1rem; min-height: 2.2rem; }}
        .bar-label {{
            flex: 0 0 260px; font-size: 1rem; color: #2d3e50; margin-right: 1.2rem;
            text-align: right; padding-right: 0.5rem; white-space: pre-line;
        }}
        .bar-bg {{
            flex: 1 1 auto; background: #e5e7eb; border-radius: 5px; height: 1.2rem;
            position: relative; margin-right: 0.7rem; min-width: 60px; max-width: 350px; overflow: hidden;
        }}
        .bar-fill {{
            height: 100%; border-radius: 5px 0 0 5px; 
            background: linear-gradient(90deg, #3b82f6 60%, #2563eb 100%);
            transition: width 0.5s; position: absolute; left: 0; top: 0;
        }}
        .bar-fill.zero {{
            background: repeating-linear-gradient(135deg, #e5e7eb, #e5e7eb 8px, #f87171 8px, #f87171 16px);
            border-radius: 5px;
        }}
        .bar-score {{ 
            min-width: 2.5rem; font-weight: 600; color: #2563eb; 
            font-size: 1.05rem; text-align: left; 
        }}
        .bar-score.zero {{ color: #f87171; }}
        .bar-axis {{
            display: flex; align-items: center; margin-left: 357px; margin-top: 0.2rem; margin-bottom: 1.2rem;
            font-size: 0.97rem; color: #6b7280; position: relative; 
            width: calc(100% - 260px - 2.5rem); max-width: 350px;
        }}
        .bar-axis-tick {{ flex: 1 1 0; text-align: center; position: relative; }}
        .bar-axis-tick:first-child {{ text-align: left; }}
        .bar-axis-tick:last-child {{ text-align: right; }}
        .summary-table th, .summary-table td {{ text-align: center; }}
        .summary-table th:first-child, .summary-table td:first-child {{ text-align: left; }}
        .impact-section {{
            background: #fef7ed; border-left: 5px solid #f97316; padding: 1.5rem;
            border-radius: 7px; margin: 1.5rem 0;
        }}
        .recommendations {{
            background: #f0fdf4; border-left: 5px solid #16a34a; padding: 1.5rem 2rem;
            border-radius: 7px; margin-top: 1.5rem;
        }}
        .recommendation-item {{
            background: white; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;
            border-left: 3px solid #16a34a;
        }}
        .recommendation-header {{ font-weight: bold; color: #166534; margin-bottom: 0.5rem; }}
        .strengths-weaknesses {{ 
            display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 1.5rem 0; 
        }}
        .strengths {{
            background: #ecfdf5; padding: 1rem 1.5rem; border-radius: 7px; 
            border-left: 4px solid #10b981;
        }}
        .weaknesses {{
            background: #fef2f2; padding: 1rem 1.5rem; border-radius: 7px; 
            border-left: 4px solid #ef4444;
        }}
        .quick-wins {{
            background: #fffbeb; border-left: 5px solid #f59e0b; padding: 1.5rem;
            border-radius: 7px; margin: 1.5rem 0;
        }}
        .methodology {{
            background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.5rem;
            border-radius: 7px; margin: 2rem 0; font-size: 0.9rem;
        }}
        .confidence-indicator {{
            display: inline-block; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.8rem; font-weight: bold; margin-left: 0.5rem;
        }}
        .confidence-high {{ background: #d1fae5; color: #065f46; }}
        .confidence-medium {{ background: #fef3c7; color: #92400e; }}
        .confidence-low {{ background: #fee2e2; color: #991b1b; }}
        .detailed-assessment {{
            background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.5rem;
            border-radius: 8px; margin: 1.5rem 0; font-size: 1rem; line-height: 1.7;
        }}
        @media (max-width: 768px) {{
            .strengths-weaknesses {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: 1fr; }}
            .bar-label {{ flex: 0 0 120px; font-size: 0.9rem; }}
            .bar-axis {{ margin-left: 120px; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Heuristic Evaluation Report</h1>
        <div style="font-size:1.15rem; color:#cbd5e1;">{site_name}</div>
        <div style="font-size:1rem; color:#cbd5e1; margin-top:0.3rem;">{site_description}</div>
        <div style="font-size:0.9rem; color:#9ca3af; margin-top:0.5rem;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</div>
    </header>
    
    <section class="executive-summary">
        <h2>Overall Assessment</h2>
        
        <div style="margin: 1.5rem 0;">
            <span class="overall-grade">Grade: {overall_grade}</span>
            <span style="font-size: 1.2rem; font-weight: bold;">
                {performance_level.title()} Performance ({average_score}/{max_score})
            </span>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{heuristic_count}</span>
                <span class="stat-label">Heuristics Evaluated</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{average_score}</span>
                <span class="stat-label">Average Score</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{int((average_score/max_score)*100)}%</span>
                <span class="stat-label">Overall Compliance</span>
            </div>
        </div>
        
        {overall_assessment_content}
    </section>

    <section class="instructions">
        <h3>📋 How to Use This Report</h3>
        <p><strong>This comprehensive heuristic evaluation report provides actionable insights to improve your website's user experience.</strong></p>
        
        <h4>Understanding the Scores:</h4>
        <ul>
            <li><strong>4 = Excellent:</strong> Exceeds usability standards, best practices implemented</li>
            <li><strong>3 = Good:</strong> Meets most usability standards, minor improvements needed</li>
            <li><strong>2 = Fair:</strong> Basic functionality present, moderate improvements needed</li>
            <li><strong>1 = Poor:</strong> Significant usability issues, major improvements required</li>
            <li><strong>0 = Critical:</strong> Broken functionality, immediate attention required</li>
        </ul>

        <h4>Report Structure:</h4>
        <ul>
            <li><strong>Summary Table:</strong> Quick overview of all heuristic scores</li>
            <li><strong>Detailed Analysis:</strong> In-depth evaluation of each heuristic with visual charts</li>
            <li><strong>Recommendations:</strong> Prioritized action items with implementation guidance</li>
            <li><strong>Business Impact:</strong> How each issue affects your users and business goals</li>
        </ul>

        <div class="alert">
            <strong>Important:</strong> This AI-generated analysis should be supplemented with user testing, accessibility audits, and expert UX review for comprehensive insights.
        </div>
    </section>
    
    <section>
        <h2>Summary of Scores</h2>
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Heuristic</th>
                    <th>Score</th>
                    <th>Grade</th>
                    <th>Performance Level</th>
                    <th>Pages</th>
                    <th>Confidence</th>
                </tr>
            </thead>
            <tbody>"""

    # Generate enhanced summary table rows
    for heuristic_name, data in analysis_json.items():
        try:
            score = float(data.get('total_score', 0))
        except (ValueError, TypeError):
            score = 0.0
        
        grade = data.get('grade', 'C')
        performance = data.get('performance_level', 'Fair')
        pages = data.get('pages_evaluated', 0)
        confidence = data.get('confidence_score', 'Medium')
        
        html_template += f"""
                <tr>
                    <td><strong>{heuristic_name}</strong></td>
                    <td>{score}/{max_score}</td>
                    <td class="grade-cell grade-{grade}">{grade}</td>
                    <td>{performance}</td>
                    <td>{pages}</td>
                    <td><span class="confidence-indicator confidence-{confidence.lower()}">{confidence}</span></td>
                </tr>"""

    html_template += """
            </tbody>
        </table>
    </section>"""

    # Generate detailed heuristic sections with enhanced information
    for heuristic_name, data in analysis_json.items():
        try:
            section_score = float(data.get('total_score', 0))
            section_max = int(data.get('max_score', max_score))
            grade = data.get('grade', 'C')
            performance = data.get('performance_level', 'Fair')
        except (ValueError, TypeError):
            section_score = 0.0
            section_max = max_score
            grade = 'C'
            performance = 'Fair'

        # Generate bar chart
        bar_rows = ""
        axis_ticks = ""
        
        for i in range(section_max + 1):
            axis_ticks += f'<div class="bar-axis-tick">{i}</div>'
        
        for subtopic in data.get('subtopics', []):
            try:
                score = float(subtopic.get('score', 0))
            except (ValueError, TypeError):
                score = 0.0
            
            width_percent = (score / section_max) * 100 if section_max > 0 else 0
            zero_class = ' zero' if score == 0 else ''
            impact = subtopic.get('impact_level', 'Medium')
            
            bar_rows += f"""
                <div class="bar-row">
                    <div class="bar-label">{subtopic.get('name', '')} <small>({impact} Impact)</small></div>
                    <div class="bar-bg">
                        <div class="bar-fill{zero_class}" style="width: {width_percent}%;"></div>
                    </div>
                    <div class="bar-score{zero_class}">{score}</div>
                </div>"""

        # Generate lists with proper formatting
        strengths_list = ""
        for strength in data.get('key_strengths', []):
            strengths_list += f"<li>{strength}</li>"
        
        weaknesses_list = ""
        for weakness in data.get('key_weaknesses', []):
            weaknesses_list += f"<li>{weakness}</li>"
        
        # Enhanced recommendations with detailed information
        recommendations_html = ""
        for rec in data.get('recommendations', []):
            if isinstance(rec, dict):
                priority = rec.get('priority', 'Medium')
                effort = rec.get('effort', 'Medium')
                timeframe = rec.get('timeframe', 'Short-term')
                recommendation = rec.get('recommendation', '')
                outcome = rec.get('expected_outcome', '')
                implementation = rec.get('implementation_notes', '')
                
                recommendations_html += f"""
                <div class="recommendation-item">
                    <div class="recommendation-header">
                        {priority} Priority - {effort} Effort - {timeframe}
                    </div>
                    <div><strong>Action:</strong> {recommendation}</div>
                    {f'<div><strong>Expected Outcome:</strong> {outcome}</div>' if outcome else ''}
                    {f'<div><strong>Implementation:</strong> {implementation}</div>' if implementation else ''}
                </div>"""
            else:
                recommendations_html += f"<div class='recommendation-item'>{rec}</div>"

        quick_wins_list = ""
        for win in data.get('quick_wins', []):
            quick_wins_list += f"<li>{win}</li>"

        html_template += f"""
    <section>
        <h3>Heuristic: {heuristic_name} <span class="grade-cell grade-{grade}">Grade: {grade}</span></h3>
        
        <div style="background: #f8fafc; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
            <strong>Definition:</strong> {data.get('definition', 'No definition available.')}
        </div>
        
        <div class="detailed-assessment">
            <h4>Detailed Assessment</h4>
            <div>{data.get('detailed_assessment', data.get('overall_description', 'No detailed assessment available.'))}</div>
        </div>
        
        <div class="bar-chart-container">
            <div class="bar-axis">{axis_ticks}</div>
            <div class="bar-chart">{bar_rows}</div>
        </div>
        
        <div class="impact-section">
            <h4>Business & User Impact</h4>
            <p><strong>Business Impact:</strong> {data.get('business_impact', 'Impact assessment not available.')}</p>
            <p><strong>User Experience Impact:</strong> {data.get('user_experience_impact', 'UX impact assessment not available.')}</p>
        </div>"""

        if data.get('key_strengths') or data.get('key_weaknesses'):
            html_template += f"""
        <div class="strengths-weaknesses">"""
            
            if data.get('key_strengths'):
                html_template += f"""
            <div class="strengths">
                <h4>Key Strengths</h4>
                <ul>{strengths_list}</ul>
            </div>"""
            
            if data.get('key_weaknesses'):
                html_template += f"""
            <div class="weaknesses">
                <h4>Key Weaknesses</h4>
                <ul>{weaknesses_list}</ul>
            </div>"""
            
            html_template += """</div>"""

        if data.get('quick_wins'):
            html_template += f"""
        <div class="quick-wins">
            <h4>🚀 Quick Wins</h4>
            <ul>{quick_wins_list}</ul>
        </div>"""

        if data.get('recommendations'):
            html_template += f"""
        <div class="recommendations">
            <h4>Detailed Recommendations</h4>
            {recommendations_html}
        </div>"""

        if data.get('methodology_notes'):
            html_template += f"""
        <div class="methodology">
            <h4>Methodology Notes</h4>
            <p>{data.get('methodology_notes', '')}</p>
        </div>"""

        analyzed_urls = data.get('analyzed_urls', [])
        if analyzed_urls:
            urls_html = "".join(f"<li><a href='{url}' target='_blank'>{url}</a></li>" for url in analyzed_urls)
            html_template += f"""
        <div class="analyzed-urls" style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 7px; margin: 2rem 0;">
            <h4>URLs Analyzed for this Heuristic</h4>
            <ul>{urls_html}</ul>
        </div>"""

        html_template += """</section>"""

    # Generate conclusion content
    conclusion_content = generate_conclusion_content(analysis_json, average_score, max_score)
    
    html_template += f"""
    <section style="background: #e0f2fe; border-left: 5px solid #2563eb; padding: 1.5rem 2rem; border-radius: 7px;">
        <h2>Key Findings & Next Steps</h2>
        {conclusion_content}
        
        <h3>Recommended Follow-up Actions:</h3>
        <ul>
            <li><strong>Immediate (1-2 weeks):</strong> Implement quick wins and high-priority fixes</li>
            <li><strong>Short-term (1-3 months):</strong> Address major usability issues identified</li>
            <li><strong>Long-term (3-6 months):</strong> Conduct user testing to validate improvements</li>
            <li><strong>Ongoing:</strong> Regular heuristic evaluations and user feedback collection</li>
        </ul>
        
        <div class="alert" style="margin-top: 1.5rem;">
            <strong>💡 Pro Tip:</strong> Prioritize recommendations based on business impact and implementation effort. Focus on high-impact, low-effort improvements first for maximum ROI.
        </div>
    </section>
</body>
</html>"""

    return html_template

def create_fallback_html_report(site_name: str, site_description: str) -> str:
    """Create a basic HTML report when analysis fails"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Heuristic Evaluation Report – {site_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ background: #fee; border: 1px solid #fcc; padding: 20px; border-radius: 5px; }}
        .header {{ background: #2d3e50; color: white; padding: 20px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Heuristic Evaluation Report</h1>
        <div>{site_name}</div>
        <div>{site_description}</div>
    </div>
    <div class="error">
        <h2>Report Generation Failed</h2>
        <p>Unable to generate the heuristic evaluation report. Please check:</p>
        <ul>
            <li>The website evaluation completed successfully</li>
            <li>Valid heuristic data was collected</li>
            <li>Try running the evaluation again</li>
        </ul>
    </div>
</body>
</html>
"""
