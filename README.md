Replace your README with:

# 📊 InsightOps

## Autonomous Business Data Analyst

InsightOps is an AI-powered business analytics application that investigates CSV datasets, identifies the single biggest business problem, investigates potential causes, provides evidence, and generates actionable recommendations.

---

# 🚀 Features

- CSV dataset upload
- Automated data profiling
- Missing-value detection
- Duplicate detection
- Numeric statistical analysis
- Regional/category comparisons
- Product analysis
- Profit margin calculation
- Correlation analysis
- Discount vs profit-margin analysis
- IQR anomaly detection
- Automatic charts
- Executive PDF reports
- Google ADK agent
- Gemini-powered reasoning
- Streamlit dashboard
- Automated tests
- Docker-ready architecture
- Cloud Run deployment ready

---

# 🧠 How InsightOps Works

CSV Dataset
     ↓
Data Profiling
     ↓
Metric Analysis
     ↓
Segment Comparison
     ↓
Profitability Analysis
     ↓
Discount Analysis
     ↓
Anomaly Detection
     ↓
Root Cause Investigation
     ↓
Evidence
     ↓
Recommendations
     ↓
Executive Report

🏗️ Architecture

                     ┌──────────────────┐
                     │       USER       │
                     │   Upload CSV     │
                     │ Business Question│
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    Streamlit     │
                     │       UI         │
                     └────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
       ┌──────────────┐               ┌──────────────┐
       │ Python Data  │               │ Google ADK   │
       │ Analysis     │               │ Agent        │
       └──────┬───────┘               └──────┬───────┘
              │                               │
              │                         Gemini Reasoning
              │                               │
              └──────────────┬────────────────┘
                             ▼
                   ┌────────────────────┐
                   │ Business Insight   │
                   │ Investigation      │
                   └─────────┬──────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
        📊 Charts        📄 Report       💡 Actions


🛠️ Technology Stack

Python
Pandas
NumPy
Matplotlib
Streamlit
Google ADK
Gemini
ReportLab
Pytest
Docker
Google Cloud Run
