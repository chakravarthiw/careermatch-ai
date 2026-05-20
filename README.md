# 🎯 CareerMatch AI

Built for the Australian graduate job market using Python, Streamlit and rule-based NLP.

CareerMatch AI is a modular Python + Streamlit job application tracker designed to help job seekers manage applications, detect visa sponsorship signals, extract important job details, search for jobs, and monitor progress through an interactive dashboard.

---

# 🚀 Current Features

## 🔍 Job Search Integration
- Search Australian jobs directly inside the app
- Sponsorship-priority sorting
- One-click transfer of jobs into tracker workflow
- Adzuna API integration

## ➕ Smart Job Tracking

Paste a job description and automatically extract:

- Job title
- Company
- Location
- Salary
- Employment type
- Closing date

## 🛂 Sponsorship Detection
- Detects Australian visa sponsorship signals using rule-based NLP
- Flags sponsorship-friendly jobs
- Prioritises sponsorship jobs in search results

## 📋 Application Tracker
- Track jobs through the application pipeline
- Status management system
- Search and filtering support
- CSV export support

## 📊 Dashboard Analytics
- Application metrics
- Sponsorship analytics
- Status breakdown
- Closing soon alerts

## 🧠 Learner Memory System
- Learns repeated company names
- Stores correction history
- Improves extraction accuracy over time

## ✅ Automated Testing

Current pytest coverage includes:
- Sponsorship detection
- Closing date extraction
- Salary extraction
- Employment type extraction
- Job title extraction
- Company extraction
- Learner memory functions


---

# 💡 Why I Built This

As an international graduate in Australia, I wanted a practical tool to manage job applications, identify sponsorship-friendly roles, and avoid missing application deadlines.

This project also demonstrates my skills in:

- Python development
- Product thinking
- Data handling
- Rule-based NLP
- Modular software architecture
- Git-based development
- Testing and debugging workflows

---

# 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| Pandas | Data handling and analytics |
| openpyxl | Excel-based persistence layer |
| Regex + Rule-Based NLP | Information extraction |
| Pytest | Automated testing |
| Git + GitHub | Version control |
| Adzuna API | Job search integration |

---

# 🗺️ Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Job tracker, extraction engine, dashboard, job search | 🔄 In Progress |
| Phase 2 | ATS keyword matching | ⏳ Planned |
| Phase 3 | Resume and cover letter tailoring | ⏳ Planned |
| Phase 4 | AI-assisted application workflow | ⏳ Planned |
| Phase 5 | Streamlit Cloud deployment | ⏳ Planned |

---

# ✅ Testing

This project includes automated tests using `pytest`.

## Current test coverage

- Visa sponsorship detection
- Closing date extraction
- Job title extraction
- Company extraction
- Employment type extraction
- Salary extraction
- Learner memory functions
- Job search functionality

## Run tests

```bash
python -m pytest -v
```

---

# 🚧 Current Status

CareerMatch AI is currently in active Phase 1 development.

## Current focus

- Reliable rule-based extraction
- Stable application tracking
- Modular code architecture
- Search integration improvements
- Clean testing workflow
- Learner memory system

Future phases will introduce:
- ATS matching
- Resume tailoring
- Cover letter generation
- AI-assisted workflows

---

# ⚙️ Setup

```bash
git clone https://github.com/chakravarthiw/careermatch-ai.git

cd careermatch-ai

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py
```

---

# 📁 Project Structure

```text
careermatch-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── tracker.py
│   ├── utils.py
│   ├── learner.py
│   ├── job_search.py
│   │
│   └── tabs/
│       ├── tab_job_search.py
│       ├── tab_add_job.py
│       ├── tab_tracker.py
│       └── tab_dashboard.py
│
├── tests/
│   ├── test_utils.py
│   ├── test_learner.py
│   └── test_job_search.py
│
├── data/
│   ├── applications.xlsx
│   ├── company_memory.json
│   └── title_memory.json
│
└── docs/
    ├── add-job.png
    ├── tracker.png
    └── dashboard.png
```

---

# 📌 About

CareerMatch AI is a personal portfolio project focused on solving real-world job search problems for graduates and international students in Australia through automation, structured tracking, and intelligent extraction workflows.