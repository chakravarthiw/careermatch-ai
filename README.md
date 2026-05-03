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

## 🛠️ Tech Stack

- Python
- Streamlit
- Pandas
- openpyxl
- Regex
- Git + GitHub

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

🗺️ Roadmap
Phase 1: Application tracker, sponsorship detection, closing date extraction, dashboard
Phase 2: ATS keyword matching and resume-job fit score
Phase 3: Job link discovery using search APIs
Phase 4: AI-assisted resume and cover letter tailoring
Phase 5: Streamlit Cloud deployment and screenshots

💡 Why I Built This

As an international graduate in Australia, I wanted a practical tool to manage job applications, identify sponsorship-friendly roles, and avoid missing application deadlines.

This project also demonstrates my skills in Python, data handling, text processing, product thinking, and Git-based development.

👤 Author

Chakravarthi Waghulabaranan
Master of Data Science, RMIT University
Melbourne, Australia
