import os
import json
import datetime
from .utils import get_llm_response

def generate_interview_guide(jd_text, resume_data, base_filename):
    print("🎤 Consulting Interview Coach...")

    prompt = f"""
    ROLE: Expert Technical Interviewer & Career Coach.
    GOAL: Prepare the candidate (Om Asanani) for an interview by generating Questions AND Ideal Answers.
    
    --- JOB DESCRIPTION ---
    {jd_text}
    
    --- CANDIDATE RESUME (Source of Truth for Answers) ---
    {json.dumps(resume_data, indent=2)}
    
    --- INSTRUCTIONS ---
    1. ANALYZE: Look for matches between the JD and the Candidate's Projects.
    2. GENERATE:
       - **Strategy Log:** Brief reasoning on why you picked these topics.
       - **The Hook:** A 30-second elevator pitch for the candidate.
       - **Technical Questions:** 5-7 hard questions about their SPECIFIC projects (e.g., "How did you optimize the RAG pipeline?").
       - **Suggested Answers:** For each technical question, write a "Model Answer" in the first person ("I did..."). 
         - USE FACTS FROM THE RESUME. 
         - Mention specific tools (Docker, Redis, etc.) and metrics (<50ms latency).
       - **Behavioral:** 1 STAR method question with key talking points.

    --- REQUIRED JSON OUTPUT FORMAT ---
    {{
        "strategy_log": "...",
        "hook": "...",
        "technical_q_and_a": [
            {{
                "question": "...",
                "answer": "..."
            }}
        ],
        "behavioral": {{
            "question": "...",
            "talking_points": "..."
        }}
    }}
    """
    
    # Get structured JSON from Gemini
    data = get_llm_response(prompt)
    if not data:
        print("❌ Error: Could not generate interview prep."); return

    # --- FORMATTING THE OUTPUT AS TEXT ---
    output_text = []
    output_text.append("="*50)
    output_text.append("INTERVIEW PREP GUIDE (WITH ANSWERS)")
    output_text.append(f"Target: {base_filename}")
    output_text.append(f"Date: {datetime.date.today()}")
    output_text.append("="*50)
    
    output_text.append("\n🧠 STRATEGY LOG")
    output_text.append(data.get("strategy_log", "No strategy provided."))
    
    output_text.append("\n🎤 THE HOOK")
    output_text.append(f"\"{data.get('hook', '')}\"")
    
    output_text.append("\n🔧 TECHNICAL DEEP DIVE")
    # Loop through the new Q&A structure
    qa_list = data.get("technical_q_and_a", [])
    if isinstance(qa_list, list):
        for idx, item in enumerate(qa_list, 1):
            q = item.get('question', 'Unknown Question')
            a = item.get('answer', 'No answer provided.')
            output_text.append(f"\nQ{idx}: {q}")
            output_text.append(f"💡 ANSWER: {a}")
            output_text.append("-" * 20)
    else:
        output_text.append("No technical questions generated.")

    output_text.append("\n⭐ BEHAVIORAL STAR")
    beh = data.get("behavioral", {})
    if isinstance(beh, dict):
        output_text.append(f"Q: {beh.get('question', '')}")
        output_text.append(f"🗣️ POINTS: {beh.get('talking_points', '')}")
    else:
        output_text.append(str(beh))
    
    output_text.append("\n" + "="*50)

    # Save to file
    if not os.path.exists("interview_prep"): os.makedirs("interview_prep")
    filename = f"Prep_{base_filename}.txt"
    full_path = os.path.join("interview_prep", filename)
    
    with open(full_path, "w", encoding='utf-8') as f:
        f.write("\n".join(output_text))
        
    print(f"✅ Interview Prep saved to: {full_path}")