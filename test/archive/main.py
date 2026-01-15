import json
import re
import os
import datetime
import ollama
from resume_builder import build_pdf

# --- CONFIGURATION ---
MODEL_NAME = "llama3.1"
DATA_DIR = "data"
PORTFOLIO_PATH = os.path.join(DATA_DIR, "master_portfolio.md")
JD_PATH = os.path.join(DATA_DIR, "job_description.txt")
STATIC_PATH = os.path.join(DATA_DIR, "static_data.json")

def load_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found at {path}")
        return None

def load_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_llm_response(prompt):
    print("Consulting Llama 3.1...")
    
    response = ollama.chat(model=MODEL_NAME, messages=[
        {'role': 'system', 'content': 'You are a professional Resume Writer. You extract facts from the user portfolio. You NEVER output placeholders like "Project Name" or "Actual Company". You output REAL data from the input.'},
        {'role': 'user', 'content': prompt}
    ], options={'num_ctx': 8192, 'temperature': 0.0})
    
    content = response['message']['content']
    
    try:
        # Regex to find JSON block
        match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Fallback: Find outer brackets
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx : end_idx + 1]
            else:
                json_str = content

        # Clean common LLM JSON errors
        json_str = re.sub(r',\s*}', '}', json_str) 
        json_str = re.sub(r',\s*]', ']', json_str)
        
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        print(content)
        return None

def normalize_keys(data):
    """
    Standardizes keys so the PDF builder never crashes.
    Fixes: "project_name" -> "name", "technologies" -> "tech_stack"
    """
    if not data: return data
    
    # 1. Fix Experience Keys
    for exp in data.get('experience', []):
        if 'bullets' not in exp and 'description' in exp:
            exp['bullets'] = exp.pop('description')
        if 'company' not in exp and 'organization' in exp:
            exp['company'] = exp.pop('organization')

    # 2. Fix Project Keys
    for p in data.get('projects', []):
        # Fix Name
        keys_to_check = ['project_name', 'title', 'Project Name', 'Name']
        for k in keys_to_check:
            if k in p and 'name' not in p:
                p['name'] = p.pop(k)
        
        # Fix Tech Stack
        stack_keys = ['technologies', 'stack', 'Tech Stack', 'skills', 'technology']
        for k in stack_keys:
            if k in p and 'tech_stack' not in p:
                val = p.pop(k)
                # Flatten lists to strings if needed
                if isinstance(val, list): 
                    p['tech_stack'] = ", ".join(val)
                else: 
                    p['tech_stack'] = str(val)

    return data

def analyze_and_tailor(jd_text, portfolio_text):
    current_date = datetime.date.today().strftime("%B %Y")
    
    prompt = f"""
    ROLE: You are an expert Technical Resume Strategist.
    
    GOAL: Tailor the resume for the attached Job Description (JD).
    
    --- JOB DESCRIPTION ---
    {jd_text[:3000]}
    
    --- MASTER PORTFOLIO ---
    {portfolio_text}
    
    --- INSTRUCTIONS ---
    
    STEP 1: EXPERIENCE SELECTION
    - You MUST select the "InfoAxon" internship.
    - Rewrite bullets to be strictly professional. NO flowery language.
    
    STEP 2: PROJECT SELECTION (CRITICAL)
    - You need to select exactly 3 projects.
    - PRIORITIZATION RULES:
      1. IGNORE simple web apps (like Pokedex, To-Do Lists, Games) UNLESS the JD specifically asks for a "Game Developer" or "Junior Frontend".
      2. PRIORITIZE "High Complexity" projects (AI Pipelines, ML Systems, Full Stack with Backend) for this role.
      3. Look for projects that use the Tech Stack mentioned in the JD.
    
    STEP 3: BULLET POINT REFINEMENT
    - Do NOT hallucinate metrics. Use the facts provided in the portfolio.
    - EXACTLY 3 BULLET POINTS per Experience and Project entry. No more, no less.
    - If the portfolio says "Result: 40% faster", write "Reduced latency by 40%...".
    
    STEP 4: SKILL EXTRACTION
    - Extract skills specifically from the selected projects and the JD.
    - FOR PROJECT TECH STACK: List ONLY the top 4-5 most critical technologies to keep the line length short.
    - FORMAT:
      * Languages: (Only programming languages, e.g., Python, C++, Java)
      * Tools: (Infrastructure & DevOps, e.g., Docker, AWS, Git)
      * Frameworks: (Libraries & APIs, e.g., Flask, React, TensorFlow)
    
    --- OUTPUT FORMAT (JSON) ---
    You must output a VALID JSON object with this EXACT structure. Do not change keys.
    {{
        "experience": [
            {{
                "company": "InfoAxon Technologies",
                "role": "AI Intern",
                "dates": "Oct 2025 - Dec 2025",
                "location": "Noida, UP",
                "bullets": [
                    "Action verb + task + quantification (STAR format)",
                    "Action verb + task + quantification"
                ]
            }}
        ],
        "projects": [
            {{
                "name": "Project Name",
                "tech_stack": "Tools, Languages, Frameworks",
                "date": "Month Year",
                "bullets": [
                    "Action verb + task + quantification",
                    "Action verb + task + quantification"
                ]
            }}
        ],
        "skills": {{
            "languages": "Python, Java...",
            "tools": "Git, Docker...",
            "frameworks": "React, Flask..."
        }}
    }}
    """
    return get_llm_response(prompt)

def clean_skills(data):
    """
    Helper to ensure skills are strings "Python, Java" 
    instead of lists ["Python", "Java"]
    """
    skills = data.get('skills', {})
    for key, val in skills.items():
        if isinstance(val, list):
            # Join list into comma-separated string
            skills[key] = ", ".join(val)
    data['skills'] = skills

    for p in data.get('projects', []):
        if 'tech_stack' in p and isinstance(p['tech_stack'], str):
            # Keep only the first 65 characters (approx 1 line width)
            if len(p['tech_stack']) > 65:
                # Cut off at the last comma to be clean
                p['tech_stack'] = p['tech_stack'][:65].rsplit(',', 1)[0]
    
    return data

def main():
    print("Loading inputs...")
    static_data = load_json(STATIC_PATH)
    portfolio = load_file(PORTFOLIO_PATH)
    jd_text = load_file(JD_PATH)

    if not (static_data and portfolio and jd_text):
        return

    # AI Processing
    tailored_data = analyze_and_tailor(jd_text, portfolio)
    if not tailored_data:
        return
    tailored_data = normalize_keys(tailored_data)
        
    with open("debug_tailored.json", "w") as f:
        json.dump(tailored_data, f, indent=4)
    print("Saved debug_tailored.json for inspection.")

    # Clean Data (Fix the List vs String issue)
    tailored_data = clean_skills(tailored_data)

    # Merge Data
    final_resume_data = {**static_data['contact_info'], **tailored_data}
    final_resume_data['education'] = static_data['education']
    final_resume_data['leadership'] = static_data['leadership']

    # Build PDF
    output_filename = os.path.join("output", f"Resume_{final_resume_data['name'].replace(' ', '_')}.pdf")
    if not os.path.exists("output"):
        os.makedirs("output")
        
    print(f"Building PDF: {output_filename}...")
    build_pdf(final_resume_data, output_filename=output_filename)

if __name__ == "__main__":
    main()