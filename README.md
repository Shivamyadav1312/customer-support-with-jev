# 🚀 Customer Support Triage with Jev

**Intelligent Customer Support Triage & Automation using TypeSafe AI (System One), Deterministic Guardrails, and LangChain + Groq**

---

## 📌 Architecture Overview

This project implements a multi-tier customer support triage system:

```
                      +-------------------------------+
                      |     Customer Support Ticket   |
                      +---------------+---------------+
                                      |
                                      v
                      +-------------------------------+
                      |   1. Jev Decision Layer       |
                      |   (TypeSafe AI System One)    |
                      +---------------+---------------+
                                      |
                     [department, urgency, refund, human_review]
                                      |
                                      v
                      +-------------------------------+
                      |   2. Deterministic Guardrails |
                      |   (Business Rules in Code)    |
                      +---------------+---------------+
                                      |
                        [escalate / safe queue route]
                                      |
                                      v
                      +-------------------------------+
                      |   3. LangChain + Groq LLM     |
                      |   (Constrained Reply Draft)   |
                      +-------------------------------+
```

1. **Jev Decision Layer (`services/jev_service.py`)**: TypeSafe's System One API classifies the ticket into `department` (billing, technical, account, general), scores `urgency` (0–3 rubric), evaluates `refund_related` probability, and estimates `human_review` need.
2. **Deterministic Automation (`choose_route`)**: Code-level deterministic rules evaluate confidence and risk thresholds to decide whether the ticket is safely automated or escalated to a human specialist.
3. **LangChain + Groq Layer (`services/response_chain.py`)**: Drafts a concise (under 120 words), non-committal support response respecting the triage classification.

---

## ⚙️ Configuration & `.env`

Create and configure your `.env` file in the project root (a template is available in `.env.example`):

```bash
cp .env.example .env
```

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TYPESAFE_API_KEY` | **Yes** (for live Jev) | `your_typesafe_api_key` | API key from [TypeSafe AI](https://typesafe.ai) |
| `TYPESAFE_MODEL` | No | `jev-latest` | Model used for System One decision evaluation |
| `TYPESAFE_API_URL` | No | `https://api.typesafe.ai/v1/systemone` | TypeSafe API endpoint |
| `TYPESAFE_TIMEOUT` | No | `30` | Timeout in seconds for HTTP requests |
| `GROQ_API_KEY` | Optional | `your_groq_api_key` | API key from [Groq Console](https://console.groq.com) |
| `GROQ_MODEL` | Optional | `llama-3.1-8b-instant` | Model for drafting natural language replies |

---

## 🚀 Running the Streamlit Frontend

The Streamlit frontend provides an interactive, production-grade triage dashboard:

```bash
# Launch Streamlit interface
streamlit run streamlit_app.py
```

Or using the Python launcher:
```bash
py -3.14 -m streamlit run streamlit_app.py
```

Access the dashboard in your browser at: **`http://localhost:8501`**

### Streamlit Features:
- **Live vs. Simulation Mode**: Test immediately even before adding API keys using the built-in simulation engine.
- **Dynamic Key Configuration**: Update and save TypeSafe & Groq credentials directly from the sidebar.
- **Configurable Guardrails**: Adjust thresholds for Human Review Probability, Urgency Escalation, and Min Confidence.
- **Preloaded Demo Tickets**: One-click test scenarios for billing duplicates, CSV technical bugs, and account lockouts.
- **KPI Metrics & Progress Visuals**: Color-coded urgency indicators, refund probability gauges, and routing banners.
- **Audit & JSON Inspector**: Full breakdown of API payloads and session history.

---

## 🌐 Running the FastAPI Backend (Alternative)

If you prefer to run the FastAPI REST API server alongside Streamlit:

```bash
uvicorn app:app --port 8080 --reload
```

- **API Root**: `http://localhost:8080/`
- **Swagger Docs**: `http://localhost:8080/docs`
- **Health Check**: `http://localhost:8080/health`
- **Triage API**: `POST http://localhost:8080/api/analyze`

---

## 📁 Project Structure

```
├── .env                  # Local secret keys (ignored by git)
├── .env.example          # Environment variables template
├── streamlit_app.py      # Streamlit triage dashboard & frontend
├── app.py                # FastAPI server & route handlers
├── requirements.txt      # Project dependencies (FastAPI, Streamlit, LangChain, Groq)
├── demo_tickets.json     # Preloaded ticket scenarios
└── services/
    ├── jev_service.py    # TypeSafe System One API client
    └── response_chain.py # LangChain + ChatGroq response chain
```