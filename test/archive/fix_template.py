import os

# UPDATED TEMPLATE: Added "| escape_tex" to ALL variables
clean_template_content = r"""%-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Template Adapted for Python Automation
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{fontawesome5}
\usepackage{multicol}
\setlength{\multicolsep}{-3.0pt}
\setlength{\columnsep}{-1pt}
\input{glyphtounicode}

\pagestyle{fancy}
\fancyhf{} 
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.6in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1.19in}
\addtolength{\topmargin}{-.7in}
\addtolength{\textheight}{1.4in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large\bfseries
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{1.0\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & \textbf{\small #2} \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{1.001\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & \textbf{\small #2}\\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.0in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

\begin{center}
    {\Huge \scshape \VAR{name | escape_tex}} \\ \vspace{1pt}
    \raisebox{-0.1\height}\faPhone\ \underline{\VAR{phone | escape_tex}}
 ~ \href{mailto:\VAR{email}}{\raisebox{-0.2\height}\faEnvelope\  \underline{\VAR{email | escape_tex}}} ~ 
    \href{\VAR{linkedin_url}}{\raisebox{-0.2\height}\faLinkedin\ \underline{/om-asanani}}  ~
    \href{\VAR{github_url}}{\raisebox{-0.2\height}\faGithub\ \underline{/LILCOOTS}}\quad
    \href{\VAR{kaggle_url}}{\raisebox{0.0\height}\faKaggle\ \underline{/omasanani}}
    \vspace{-8pt}
\end{center}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    ((* for edu in education *))
      \resumeSubheading
        {\VAR{edu.school | escape_tex}}{\VAR{edu.graduation_date | escape_tex}}
        {\VAR{edu.degree | escape_tex}}{\VAR{edu.location | escape_tex}}
    ((* endfor *))
  \resumeSubHeadingListEnd

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    ((* for job in experience *))
    \resumeSubheading
      {\VAR{job.company | escape_tex}}{\VAR{job.dates | escape_tex}}
      {\VAR{job.role | escape_tex}}{\VAR{job.location | escape_tex}}
      \resumeItemListStart
        ((* for bullet in job.bullets *))
        \resumeItem{\VAR{bullet | escape_tex}}
        ((* endfor *))
      \resumeItemListEnd
    ((* endfor *))
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \vspace{-5pt}
    \resumeSubHeadingListStart
      ((* for project in projects *))
        \resumeProjectHeading
          {\textbf{\VAR{project.name | escape_tex}} $|$ \emph{\VAR{project.tech_stack | escape_tex}}}{\VAR{project.date | escape_tex}}
          \resumeItemListStart
            ((* for bullet in project.bullets *))
            \resumeItem{\VAR{bullet | escape_tex}}
            ((* endfor *))
          \resumeItemListEnd
          \vspace{-13pt}
      ((* endfor *))
    \resumeSubHeadingListEnd
\vspace{5pt}

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: \VAR{skills.languages | escape_tex}} \\
     \textbf{Developer Tools}{: \VAR{skills.tools | escape_tex}} \\
     \textbf{Technologies/Frameworks}{: \VAR{skills.frameworks | escape_tex}} \\
    }}
 \end{itemize}
 \vspace{-11pt}

%-----------LEADERSHIP/EXTRACURRICULAR-----------
((* if leadership *))
\section{Leadership / Extracurricular}
    \resumeSubHeadingListStart
        ((* for item in leadership *))
        \resumeSubheading{\VAR{item.org | escape_tex}}{\VAR{item.date | escape_tex}}{\VAR{item.role | escape_tex}}{\VAR{item.location | escape_tex}}
            \resumeItemListStart
                ((* for bullet in item.bullets *))
                \resumeItem{\VAR{bullet | escape_tex}}
                ((* endfor *))
            \resumeItemListEnd
        ((* endfor *))
    \resumeSubHeadingListEnd
((* endif *))

\end{document}
"""

def fix_file():
    if not os.path.exists("templates"):
        os.makedirs("templates")
        
    file_path = os.path.join("templates", "resume_template.tex")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_template_content)
        
    print(f"✅ Success! Updated {file_path} with SAFER syntax (auto-escaping).")
    print("👉 Now run: python main.py")

if __name__ == "__main__":
    fix_file()