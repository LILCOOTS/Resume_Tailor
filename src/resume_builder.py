import os
import subprocess
import jinja2

# CONFIGURATION
LATEX_COMPILER = 'pdflatex'

def escape_latex_chars(val):
    """
    CRITICAL CHANGE: This function now does NOTHING.
    
    Why?
    Because main1.py already cleans the data (converting % to \%, etc.).
    If we escape it again here, we get double-backslashes (\\%) which crashes LaTeX.
    """
    return val 

def build_pdf(data, template_name="resume_template.tex", output_filename="Generated_Resume.pdf"):
    
    template_loader = jinja2.FileSystemLoader(searchpath="./templates")
    latex_env = jinja2.Environment(
        loader=template_loader,
        block_start_string='((*',    
        block_end_string='*))',      
        variable_start_string='\\VAR{',
        variable_end_string='}',
        comment_start_string='\\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    )
    
    # We keep the filter registration so the template doesn't crash,
    # but the function itself now passes the text through unchanged.
    latex_env.filters['escape_tex'] = escape_latex_chars

    def clean_text(obj):
        if isinstance(obj, str):
            return obj.replace("\n", " ").replace("\r", "").strip()
        elif isinstance(obj, list):
            return [clean_text(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: clean_text(v) for k, v in obj.items()}
        return obj

    # Clean the data before rendering
    data = clean_text(data)

    try:
        template = latex_env.get_template(template_name)
        rendered_tex = template.render(data)

        output_tex = "temp_build.tex"
        with open(output_tex, "w", encoding='utf-8') as f:
            f.write(rendered_tex)

        print(f"   (Compiling {output_tex}...)")
        
        # DEBUG COMPILER
        process = subprocess.run(
            [LATEX_COMPILER, '-interaction=nonstopmode', output_tex], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if os.path.exists("temp_build.pdf"):
            if os.path.exists(output_filename):
                os.remove(output_filename) 
            os.rename("temp_build.pdf", output_filename)
            print(f"✅ PDF Generated Successfully: {output_filename}")
            
            # Cleanup
            for ext in ['.aux', '.log', '.out', '.tex']:
                if os.path.exists(f"temp_build{ext}"):
                    os.remove(f"temp_build{ext}")
        else:
            print("\n❌ PDF GENERATION FAILED!")
            print("------------------------------------------------")
            print("LaTeX Error Log (Last 20 lines):")
            log_output = process.stdout if process.stdout else process.stderr
            if log_output:
                print("\n".join(log_output.splitlines()[-20:]))
            else:
                print("No output captured from pdflatex.")
            print("------------------------------------------------")
            
    except jinja2.TemplateSyntaxError as e:
        print(f"\nTEMPLATE ERROR in {template_name}:")
        print(f"   Line {e.lineno}: {e.message}")
        print("   -> Check for typos in your ((* ... *)) blocks.\n")
    except Exception as e:
        print(f"System Error: {e}")

if __name__ == "__main__":
    # Test Data
    dummy_data = {
        "name": "Test User", "email": "test@test.com", "phone": "123",
        "linkedin_url": "link", "github_url": "git", "kaggle_url": "kag",
        "education": [{"school": "Test U", "graduation_date": "2025", "degree": "BS", "location": "City"}],
        "experience": [], "projects": [], "skills": {"languages": "Py", "tools": "Git", "frameworks": "Flask"},
        "leadership": []
    }
    
    if not os.path.exists("templates"):
        os.makedirs("templates")
    print("Builder ready. Running test build...")
    build_pdf(dummy_data)