import os
import re
import datetime
from src.utils import load_file, load_json, get_llm_response
from src.resume_builder import build_pdf
import src.interview_agent as interview_agent 

# --- CONFIGURATION ---
DATA_DIR = "data"
PORTFOLIO_PATH = os.path.join(DATA_DIR, "master_portfolio.md")
JD_PATH = os.path.join(DATA_DIR, "job_description.txt")
STATIC_PATH = os.path.join(DATA_DIR, "static_data.json")

def escape_latex_chars(text):
    """
    CRITICAL FIX: Converts special characters to safe LaTeX equivalents.
    Prevents < becoming ! and % crashing the build.
    """
    if not isinstance(text, str): return text
    
    # 1. Strip Markdown Artifacts (Remove **bold**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text).replace('*', '')

    # 2. Escape LaTeX Special Chars (Order matters!)
    replacements = {
        '&': r'\&',        # Ampersand
        '%': r'\%',        # Percent
        '$': r'\$',        # Dollar sign
        '#': r'\#',        # Hashtag
        '_': r'\_',        # Underscore
        '{': r'\{',        # Curly braces
        '}': r'\}',
        '<': r'$<$',       # Less than (Math mode)
        '>': r'$>$',       # Greater than (Math mode)
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    return text

def recursive_sanitize(obj):
    """Recursively applies LaTeX escaping to any strings in a dict/list."""
    if isinstance(obj, str):
        return escape_latex_chars(obj)
    elif isinstance(obj, list):
        return [recursive_sanitize(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: recursive_sanitize(v) for k, v in obj.items()}
    return obj

def sanity_check(data):
    """Guardrail: Fixes layout breaking issues AND sanitizes LaTeX"""
    print("🛡️  Running Sanity Checks & LaTeX Cleaning...")
    
    # 1. Clean Experience (Company Names & Roles)
    for exp in data.get('experience', []):
        company = exp.get('company', '')
        
        # --- CHANGE IS HERE: We removed the re.sub trimming logic ---
        # Now it will just keep the full company name found in your resume.
            
        if not exp.get('role'):
            print(f"   ⚠️  Warning: Missing role for {company}. Defaulting to 'Intern'.")
            exp['role'] = "Intern"
            
        # Sanitize Content (Strip Markdown + Escape LaTeX)
        exp['company'] = escape_latex_chars(exp.get('company', ''))
        exp['role'] = escape_latex_chars(exp.get('role', ''))
        exp['location'] = escape_latex_chars(exp.get('location', ''))
        
        if 'bullets' in exp and isinstance(exp['bullets'], list):
            exp['bullets'] = [escape_latex_chars(b.strip()) for b in exp['bullets'] if isinstance(b, str)]

    # 2. Fix Projects
    for p in data.get('projects', []):
        stack = p.get('tech_stack', '')
        if len(stack) > 90:
            stack = stack[:90].rsplit(',', 1)[0]
        
        # Sanitize Content
        p['name'] = escape_latex_chars(p.get('name', ''))
        p['tech_stack'] = escape_latex_chars(stack.strip())

        if 'bullets' in p and isinstance(p['bullets'], list):
            clean_bullets = [escape_latex_chars(b.strip()) for b in p['bullets'] if isinstance(b, str)]
            if len(clean_bullets) > 3:
                clean_bullets = clean_bullets[:3]
            p['bullets'] = clean_bullets
            
    # 3. Clean Skills
    if 'skills' in data:
        for cat, val in data['skills'].items():
            if isinstance(val, str):
                data['skills'][cat] = escape_latex_chars(val)
            elif isinstance(val, list):
                data['skills'][cat] = escape_latex_chars(", ".join(val))
            
    return data

def normalize_keys(data):
    if not data: return data
    data = {k.lower(): v for k, v in data.items()}

    for exp in data.get('experience', []):
        if 'bullets' not in exp and 'description' in exp: 
            exp['bullets'] = exp.pop('description')
        if 'role' not in exp:
            for k in ['title', 'position', 'job_title', 'designation']:
                if k in exp:
                    exp['role'] = exp.pop(k); break
    
    for p in data.get('projects', []):
        if 'name' not in p:
            for k in ['project_name', 'title', 'Name']: 
                if k in p: p['name'] = p.pop(k)
        if 'tech_stack' not in p:
            for k in ['technologies', 'stack', 'skills']:
                if k in p: 
                    val = p.pop(k)
                    p['tech_stack'] = ", ".join(val) if isinstance(val, list) else str(val)
    return data

def clean_skills(data):
    skills = data.get('skills', {})
    if skills:
        skills = {k.lower(): v for k, v in skills.items()}
    for key, val in skills.items():
        if isinstance(val, list): skills[key] = ", ".join(val)
    data['skills'] = skills
    return data

def analyze_and_tailor(jd_text, portfolio_text):
    prompt = f"""
    ROLE: Resume Strategist (ATS Optimizer).
    TASK: Tailor the resume to match the JD using IMPACTFUL, CONCISE points.

    --- JOB DESCRIPTION ---
    {jd_text}

    --- MASTER PORTFOLIO ---
    {portfolio_text}

    --- STRATEGY INSTRUCTIONS ---
    1. SELECTION:
       - Pick the most relevant Internship/Experience.
       - Pick exactly 3 Projects that best match the JD.

    2. STYLE (CONCISE & IMPACTFUL):
       - Do NOT be verbose. Recruiters scan resumes in 6 seconds.
       - Use Strong Action Verbs (e.g., Engineered, Orchestrated, Optimized).
       - Include Metrics where possible (e.g., "Reduced latency by 40%", "Handled 10k+ requests").
       - Keep bullet points sharp and to the point.
       - CRITICAL: Do NOT use Markdown formatting (no **bold**, no *italics*). Write PLAIN TEXT only.

    3. TECH STACK: 
       - List 3-5 specific tools per project. If a project uses only "Node.js", add concepts (e.g. "Node.js, Streams, Async/Await").

    --- OUTPUT FORMAT (JSON) ---
    {{
        "meta": {{ "company": "...", "role": "..." }},
        "resume": {{
            "experience": [
                {{ "company": "...", "role": "...", "dates": "...", "location": "...", "bullets": ["Action verb + task + result", "Action verb + task + result"] }}
            ],
            "projects": [ {{ "name": "...", "tech_stack": "...", "bullets": [...] }} ],
            "skills": {{ "languages": "...", "tools": "...", "frameworks": "..." }}
        }}
    }}
    """
    return get_llm_response(prompt)

def main():
    print("📂 Loading inputs...")
    static_data = load_json(STATIC_PATH)
    portfolio = load_file(PORTFOLIO_PATH)
    jd_text = load_file(JD_PATH)

    if not (static_data and portfolio and jd_text): return

    # --- PHASE 1: GENERATE RESUME ---
    print("\n--- PHASE 1: TAILORING RESUME ---")
    response = analyze_and_tailor(jd_text, portfolio)
    if not response: 
        print("❌ AI returned no response."); return

    response = {k.lower(): v for k, v in response.items()}

    meta = response.get('meta', {})
    resume_data = response.get('resume', {})

    company = meta.get('company') or "Unknown_Company"
    role = meta.get('role') or "Unknown_Role"
    clean_company = re.sub(r'[^a-zA-Z0-9]', '', company)
    clean_role = re.sub(r'[^a-zA-Z0-9]', '', role)
    base_name = f"{clean_company}_{clean_role}"
    
    print(f"🎯 Target: {role} @ {company}")

    # DATA CLEANING
    resume_data = normalize_keys(resume_data)
    resume_data = sanity_check(resume_data) # Cleans AI data
    resume_data = clean_skills(resume_data)
    
    # --- CRITICAL FIX: Sanitize Static Data (Education & Leadership) ---
    # This prevents crashes from symbols like "%" in "93%"
    static_data = recursive_sanitize(static_data)
    # -------------------------------------------------------------------
    
    final_data = {**static_data['contact_info'], **resume_data}
    final_data['education'] = static_data['education']
    final_data['leadership'] = static_data['leadership']

    pdf_filename = f"Resume_Om_Asanani_{base_name}.pdf"
    output_path = os.path.join("output", pdf_filename)
    if not os.path.exists("output"): os.makedirs("output")
    
    print(f"🔨 Building PDF: {output_path}...")
    build_pdf(final_data, output_filename=output_path)

    # --- PHASE 2: INTERVIEW PREP ---
    print("\n--- PHASE 2: GENERATING INTERVIEW PREP ---")
    interview_agent.generate_interview_guide(jd_text, resume_data, base_name)

if __name__ == "__main__":
    main()