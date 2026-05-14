# 🎯 CareerMatch AI

CareerMatch AI is a Python + Streamlit job application tracker built for the Australian job market.

It helps job seekers track applications, detect visa sponsorship signals, extract closing dates from job descriptions, and monitor application progress through a dashboard.

---

## 🚀 Current Features

- Paste a job description and auto-fill key fields
- Extracts job title, company, location, salary, employment type and closing date
- Detects visa sponsorship signals for Australian job ads
- Tracks application status across the job search pipeline
- Dashboard for application metrics and closing-soon alerts
- Learner memory system for repeated company detection
- Automated test coverage with pytest
- Excel-based local storage

---

## 💡 Why I Built This

As an international graduate in Australia, I wanted a practical tool to manage job applications, identify sponsorship-friendly roles, and avoid missing application deadlines.

This project also demonstrates my skills in Python, data handling, text processing, product thinking, and Git-based development.

---

## 🛠 Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web interface |
| Pandas | Data handling and analytics |
| openpyxl | Excel-based persistence layer |
| Regex + Rule-Based NLP | Information extraction from job descriptions |
| Git + GitHub | Version control and project management |

---

## 🗺️ Roadmap
| Phase | Description | Status |
|---|---|---|
| Phase 1 | Job tracker, extraction engine, dashboard | 🔄 In Progress |
| Phase 2 | ATS keyword matching | ⏳ Planned |
| Phase 3 | Resume and cover letter tailoring | ⏳ Planned |
| Phase 4 | Job discovery integration | ⏳ Planned |
| Phase 5 | Streamlit Cloud deployment | ⏳ Planned |

---

## ⚙️ Setup

```bash
git clone https://github.com/chakravarthiw/careermatch-ai.git
cd careermatch-ai

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py

---
## ✅ Testing

This project includes automated tests using `pytest`.

Current tests cover:
- Visa sponsorship detection
- Closing date extraction
- Job title extraction
- Company extraction
- Employment type extraction
- Salary extraction
- Learner memory functions

Run tests:

```bash
python -m pytest -v

---

## 🚧 Current Status

CareerMatch AI is currently in active Phase 1 development.

The focus is on building a reliable rule-based extraction engine, stable application tracking, and a clean testing workflow before adding ATS matching and resume tailoring.

---

## 📁 Project Structure

careermatch-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── tracker.py
│   ├── utils.py
│   └── learner.py
│
├── tests/
│   ├── test_utils.py
│   └── test_learner.py
│
├── data/        # Local tracker files ignored by Git
└── docs/        # Screenshots and documentation

---

