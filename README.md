# 🚀 Resume-Tailor - Automated Resume Orchestrator

**Resume-Tailor** is a local-first automation tool that **tailors your resume** to specific job descriptions (JDs) and **generates a personalized interview prep guide** using Google's Gemini 2.5 Flash.

It ensures your resume is ATS-optimized, visually dense (but readable), and strictly formatted, while also acting as an expert career coach to prep you for the interview.

---

## ✨ Features

### 📄 1. Intelligent Resume Tailoring
- **Context-Aware Selection**: Analyzes your `Master Portfolio` to select the most relevant Experience and Projects for the target JD.
- **ATS Optimization**: Rephrases bullet points to match JD keywords while maintaining truthfulness.
- **Strict Formatting**: Enforces "3 bullets per item" rule with a mix of punchy 1-liners and detailed 2-liners.
- **LaTeX PDF Generation**: Compiles a professional, distinctively styled PDF resume (no generic Word docs!).
- **Dynamic Tech Stack**: auto-adjusts skill lists to prevent line overflows.

### 🎤 2. Interview Prep Agent
- **Strategic Analysis**: Explains *why* certain projects were highlighted.
- **The "Hook"**: Generates a 30-second elevator pitch tailored to the role.
- **Hard Technical Questions**: Predicts 5-7 deep-dive technical questions based on your specific project architecture.
- **Model Answers**: Provides first-person, fact-based answers using your exact metrics (e.g., "<50ms latency").
- **Behavioral Prep**: Prepares STAR method responses.

### 🛡️ 3. Robust Engineering
- **Latex Sanitization**: Automatically escapes special characters (`&`, `%`, `$`) to prevent build crashes.
- **Data Validation**: detailed sanity checks to ensure JSON integrity before generation.
- **Local-First**: All data stays on your machine (except the prompt sent to Gemini API).

---

## 🛠️ Prerequisites

- **Python 3.8+**
- **LaTeX Distribution**: You need `pdflatex` installed and in your PATH.
  - Windows: [MiKTeX](https://miktex.org/download) or [TeX Live](https://www.tug.org/texlive/).
  - Mac/Linux: `TeX Live`.
- **Google Gemini API Key**: Get one [here](https://aistudio.google.com/).

---

## 🚀 Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/local_job_agent.git
    cd local_job_agent
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install google-genai python-dotenv jinja2
    ```

3.  **Environment Configuration**
    Create a `.env` file in the root directory:
    ```ini
    GEMINI_API_KEY=your_api_key_here
    ```

---

## 📂 Data Preparation

The agent relies on three key files in the `data/` directory.

### 1. `data/master_portfolio.md`
This is your "Database of Everything". Dump every project, internship, and skill here. The AI will cherry-pick from this.
**Format:**
```markdown
## EXPERIENCE_ENTRY
Title: ...
Company: ...
Content:
- Bullet 1
- Bullet 2

## PROJECT_ENTRY
Name: FoodShare
Type: Full Stack
...
-- CONTENT --
Context: ...
Action: ...
Result: ...
```

### 2. `data/job_description.txt`
Paste the raw text of the Job Description you are applying for.

### 3. `data/static_data.json`
Contains your constant contact info and education details.
```json
{
    "contact_info": {
        "name": "Om Asanani",
        "email": "...",
        "phone": "...",
        "linkedin": "...",
        "github": "...",
        "portfolio": "..."
    },
    "education": [ ... ],
    "leadership": [ ... ]
}
```

---

## 🖥️ Usage

Run the main agent script:

```bash
python main1.py
```

### What happens next?
1.  **Phase 1 (Resume)**: The AI analyzes the files, selects the best content, rewrites it, and generates a PDF in `output/`.
    - *Example Output:* `output/Resume_Om_Asanani_Powerplay_BackendIntern.pdf`
2.  **Phase 2 (Interview)**: The Interview Agent reads the *generated* resume and the JD to create a prep guide.
    - *Example Output:* `interview_prep/Prep_Powerplay_BackendIntern.txt`

---

## 🧩 Project Structure

```
local_job_agent/
├── data/                  # Input data (JD, Portfolio, Static info)
├── templates/             # LaTeX templates
│   └── resume_template.tex
├── output/                # Generated PDFs
├── interview_prep/        # Generated Prep Guides
├── test/                  # Archived/Unused scripts
├── src/                   # Core Logic Modules
│   ├── resume_builder.py
│   ├── interview_agent.py
│   └── utils.py
└── main1.py               # Main Entry Point
```

---

## 🐛 Troubleshooting

-   **Unicode Errors?** The script automatically strips emojis and unsupported chars for LaTeX compatibility.
-   **PDF Generation Failed?** Check the console output. It usually means a LaTeX syntax error. The script prints the last 20 lines of the log.
-   **API Errors?** Ensure your `GEMINI_API_KEY` is valid and has credits.

---

## 📜 License
MIT
