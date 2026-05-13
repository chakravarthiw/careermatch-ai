# 🎯 CareerMatch AI

CareerMatch AI is a Python + Streamlit job application tracker built for the Australian job market.

It helps job seekers track applications, detect visa sponsorship signals, extract closing dates from job descriptions, and monitor application progress through a dashboard.

---

## 🚀 Current Features

- 📋 Job application tracker
- 🛂 Visa sponsorship detection from job descriptions
- 📅 Closing date extraction from job descriptions
- 🔍 Filterable tracker by status and sponsorship
- 📊 Dashboard with application metrics
- ⏰ Closing soon alerts
- 📁 Excel/CSV-based tracking

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

📁 Project Structure

careermatch-ai/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── tracker.py
│   └── utils.py
│
├── data/        # Local tracker files ignored by Git
├── resumes/     # Local resume files ignored by Git
└── docs/        # Screenshots and documentation


