"""Streamlit Frontend for Jev Smart Support Triage.

Combines TypeSafe AI (System One) for structured decision intelligence,
deterministic business guardrails for routing, and LangChain + Groq for customer response drafting.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import streamlit as st

# Initialize environment
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH, override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jev-support-streamlit")

# Page Configuration
st.set_page_config(
    page_title="Jev Smart Support Triage",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Custom Styling (CSS)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Global Typography & Spacing */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(12px);
    }

    .hero-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }

    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }

    .badge-jev {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #818cf8;
    }

    .badge-langchain {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.4);
        color: #34d399;
    }

    .badge-groq {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #fbbf24;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
        max-width: 800px;
        line-height: 1.5;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }

    .metric-label {
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }

    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 4px;
    }

    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
    }

    /* Route Decision Banner */
    .route-banner {
        border-radius: 14px;
        padding: 20px 24px;
        margin: 16px 0;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .route-escalated {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(185, 28, 28, 0.05) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .route-automated {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(5, 150, 105, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .route-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .route-header-escalated {
        color: #f87171;
    }

    .route-header-automated {
        color: #34d399;
    }

    .route-destination {
        font-size: 1.4rem;
        font-weight: 800;
        color: #f8fafc;
        margin: 0;
    }

    .route-reason {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin: 0;
    }

    /* Reply Container */
    .reply-box {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #818cf8;
        border-radius: 10px;
        padding: 18px 20px;
        color: #e2e8f0;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* Pill Badges */
    .status-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .status-active { background: rgba(16, 185, 129, 0.2); color: #34d399; }
    .status-warning { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .status-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Helper Functions & Business Logic
# -----------------------------------------------------------------------------
def load_preset_tickets() -> list[dict[str, str]]:
    """Loads demo tickets from demo_tickets.json or returns default presets."""
    tickets_path = BASE_DIR / "demo_tickets.json"
    if tickets_path.exists():
        try:
            with open(tickets_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load demo_tickets.json: {e}")

    return [
        {
            "name": "Billing + Refund",
            "ticket": "I was charged twice for my Pro subscription this morning. I need the duplicate charge refunded because our finance team is closing the books today. Please help ASAP.",
        },
        {
            "name": "Technical Bug",
            "ticket": "My CSV export stopped working after today's update. I can still use the dashboard, but I need the export for a report tomorrow.",
        },
        {
            "name": "Account Access",
            "ticket": "I cannot access the workspace after my admin changed my email address. Please restore access.",
        },
    ]


def choose_route_custom(
    department: str,
    dept_conf: float,
    urgency: float,
    human_prob: float,
    human_thresh: float = 0.65,
    dept_thresh: float = 0.60,
    urgency_thresh: float = 2.50,
) -> tuple[str, bool, str]:
    """Deterministic routing guardrail based on configurable business rules."""
    reasons = []
    if human_prob >= human_thresh:
        reasons.append(f"Human review prob ({human_prob:.2f} >= {human_thresh:.2f})")
    if dept_conf < dept_thresh:
        reasons.append(f"Dept confidence low ({dept_conf:.2f} < {dept_thresh:.2f})")
    if urgency >= urgency_thresh:
        reasons.append(f"Urgency score high ({urgency:.2f} >= {urgency_thresh:.2f})")

    needs_human = len(reasons) > 0

    if needs_human:
        return (
            f"{department.title()} → Human specialist",
            True,
            "Escalated: " + ", ".join(reasons),
        )

    return (
        f"{department.title()} queue",
        False,
        "Safe for normal automated queue routing",
    )


def simulate_jev_decision(ticket: str) -> Any:
    """Provides a deterministic mock decision when running in Demo/Offline mode."""
    lower = ticket.lower()
    
    # Classify department based on keywords
    if any(k in lower for k in ["charge", "refund", "invoice", "billing", "subscription", "price", "credit", "money"]):
        dept = "billing"
        dept_conf = 0.94
        refund_prob = 0.92 if "refund" in lower or "charge" in lower else 0.45
        urg = 2.70 if any(k in lower for k in ["asap", "closing books", "immediately", "urgent"]) else 1.80
    elif any(k in lower for k in ["csv", "export", "error", "bug", "crash", "stopped working", "api", "dashboard"]):
        dept = "technical"
        dept_conf = 0.88
        refund_prob = 0.05
        urg = 2.10 if "tomorrow" in lower or "blocking" in lower else 1.40
    elif any(k in lower for k in ["login", "password", "access", "workspace", "email", "admin", "permissions"]):
        dept = "account"
        dept_conf = 0.91
        refund_prob = 0.02
        urg = 2.20
    else:
        dept = "general"
        dept_conf = 0.72
        refund_prob = 0.10
        urg = 1.00

    human_review = 0.82 if (refund_prob > 0.7 or urg >= 2.5 or "admin" in lower) else 0.28

    class MockJevDecision:
        def __init__(self):
            self.department = dept
            self.department_confidence = dept_conf
            self.urgency_score = urg
            self.urgency_confidence = 0.91
            self.refund_probability = refund_prob
            self.human_review_probability = human_review
            self.model = "jev-latest (simulated)"

    return MockJevDecision()


def simulate_draft_reply(ticket: str, decision: Any, route: str) -> str:
    """Generates a realistic draft response when running offline or without Groq."""
    dept = decision.department
    if decision.human_review_probability >= 0.65 or decision.urgency_score >= 2.5:
        return (
            f"Hello, thank you for reaching out. We have received your request regarding your {dept} inquiry "
            f"and escalated it directly to our specialist team for priority review. "
            f"A team member will inspect your case and follow up with an update shortly."
        )
    return (
        f"Hello, thank you for contacting support. We have routed your request to our {dept.title()} team. "
        f"Our team is currently investigating your ticket and will get back to you with next steps soon."
    )


def save_env_file(keys: dict[str, str]) -> None:
    """Updates the .env file with new keys."""
    existing: dict[str, str] = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    existing.update(keys)

    lines = [
        "# ==============================================================================",
        "# Customer Support Triage with Jev - Environment Configuration",
        "# ==============================================================================",
        "",
        "# --- TypeSafe / Jev API ---",
        f"TYPESAFE_API_KEY={existing.get('TYPESAFE_API_KEY', 'your_typesafe_api_key')}",
        f"TYPESAFE_MODEL={existing.get('TYPESAFE_MODEL', 'jev-latest')}",
        f"TYPESAFE_API_URL={existing.get('TYPESAFE_API_URL', 'https://api.typesafe.ai/v1/systemone')}",
        f"TYPESAFE_TIMEOUT={existing.get('TYPESAFE_TIMEOUT', '30')}",
        "",
        "# --- Groq API / LangChain ---",
        f"GROQ_API_KEY={existing.get('GROQ_API_KEY', 'your_groq_api_key')}",
        f"GROQ_MODEL={existing.get('GROQ_MODEL', 'llama-3.1-8b-instant')}",
        "",
    ]
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# -----------------------------------------------------------------------------
# Initialize Session State
# -----------------------------------------------------------------------------
presets = load_preset_tickets()

if "ticket_input" not in st.session_state:
    st.session_state.ticket_input = presets[0]["ticket"]

if "history" not in st.session_state:
    st.session_state.history = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None


# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/langchain-ai/langchain/master/docs/static/img/langchain_logo.png",
        width=48,
    ) if False else None
    st.title("⚡ Triage Settings")

    # API Keys Status check
    current_typesafe_key = os.getenv("TYPESAFE_API_KEY", "").strip()
    current_groq_key = os.getenv("GROQ_API_KEY", "").strip()

    has_valid_typesafe = bool(current_typesafe_key and current_typesafe_key != "your_typesafe_api_key")
    has_valid_groq = bool(current_groq_key and current_groq_key != "your_groq_api_key")

    # Simulation vs Live Mode
    st.subheader("🎯 Execution Mode")
    mode_options = ["Live API (TypeSafe + Groq)", "Simulation / Demo Mode"]
    default_mode_index = 0 if has_valid_typesafe else 1
    
    selected_mode = st.radio(
        "Select processing mode:",
        options=mode_options,
        index=default_mode_index,
        help="Use 'Simulation / Demo Mode' if you want to explore the UI without making live external API calls.",
    )
    is_live_mode = selected_mode == "Live API (TypeSafe + Groq)"

    # Service Status Pills
    st.write("---")
    st.subheader("🔌 API Credentials")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if has_valid_typesafe:
            st.markdown('<span class="status-badge status-active">TypeSafe: Active</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-warning">TypeSafe: Unset</span>', unsafe_allow_html=True)
    with col_s2:
        if has_valid_groq:
            st.markdown('<span class="status-badge status-active">Groq: Active</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-warning">Groq: Unset</span>', unsafe_allow_html=True)

    with st.expander("🔑 Configure API Keys & Models", expanded=not has_valid_typesafe):
        st.caption("Values entered here will be used in the session and can be saved to `.env`.")
        
        input_typesafe_key = st.text_input(
            "TypeSafe API Key",
            value=current_typesafe_key if current_typesafe_key != "your_typesafe_api_key" else "",
            type="password",
            placeholder="ts_...",
            help="Required for Live TypeSafe Jev triage analysis.",
        )
        
        input_typesafe_model = st.text_input(
            "TypeSafe Model",
            value=os.getenv("TYPESAFE_MODEL", "jev-latest"),
            placeholder="jev-latest",
        )

        input_groq_key = st.text_input(
            "Groq API Key",
            value=current_groq_key if current_groq_key != "your_groq_api_key" else "",
            type="password",
            placeholder="gsk_...",
            help="Optional. Used by LangChain to draft customer responses.",
        )

        input_groq_model = st.selectbox(
            "Groq Model",
            options=["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
            index=0,
        )

        if st.button("💾 Save Keys to .env", use_container_width=True):
            updated_dict = {
                "TYPESAFE_MODEL": input_typesafe_model.strip() or "jev-latest",
                "GROQ_MODEL": input_groq_model,
            }
            if input_typesafe_key.strip():
                updated_dict["TYPESAFE_API_KEY"] = input_typesafe_key.strip()
                os.environ["TYPESAFE_API_KEY"] = input_typesafe_key.strip()
            if input_groq_key.strip():
                updated_dict["GROQ_API_KEY"] = input_groq_key.strip()
                os.environ["GROQ_API_KEY"] = input_groq_key.strip()

            save_env_file(updated_dict)
            st.success("Configuration saved to .env!")
            time.sleep(0.5)
            st.rerun()

    # Deterministic Business Rules
    st.write("---")
    st.subheader("🛡️ Business Guardrails")
    st.caption("Adjust the thresholds that trigger escalation to a human specialist.")

    human_threshold = st.slider(
        "Human Review Prob Escalation",
        min_value=0.0,
        max_value=1.0,
        value=0.65,
        step=0.05,
        help="If Jev human review probability is >= this threshold, escalate to human.",
    )

    dept_threshold = st.slider(
        "Min Department Confidence",
        min_value=0.0,
        max_value=1.0,
        value=0.60,
        step=0.05,
        help="If department confidence is < this threshold, escalate for verification.",
    )

    urgency_threshold = st.slider(
        "Urgency Escalation Score (0–3)",
        min_value=0.0,
        max_value=3.0,
        value=2.50,
        step=0.1,
        help="If urgency score is >= this threshold, escalate immediately.",
    )

    # History & Clear
    st.write("---")
    st.metric("Total Triaged Tickets", len(st.session_state.history))
    if st.session_state.history and st.button("🧹 Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.latest_result = None
        st.rerun()


# -----------------------------------------------------------------------------
# Main Application Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-badges">
            <span class="badge-pill badge-jev">⚡ TypeSafe Jev System One</span>
            <span class="badge-pill badge-langchain">🦜️ LangChain Chain</span>
            <span class="badge-pill badge-groq">🚀 Groq LLM Draft</span>
            <span class="badge-pill" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #cbd5e1;">🛡️ Deterministic Guardrails</span>
        </div>
        <h1 class="hero-title">Jev Smart Support Triage</h1>
        <p class="hero-subtitle">
            Jev makes the structured decision. Deterministic business rules govern routing & escalation. 
            LangChain & Groq draft safe, contextual customer replies.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Ticket Input Area & Preset Buttons
# -----------------------------------------------------------------------------
st.markdown("### 📥 Customer Support Ticket")

# Preset selection buttons
st.write("**Quick Preloaded Examples:**")
cols = st.columns(len(presets) + 1)

for idx, p in enumerate(presets):
    with cols[idx]:
        if st.button(f"📋 {p['name']}", key=f"preset_{idx}", use_container_width=True):
            st.session_state.ticket_input = p["ticket"]
            st.rerun()

with cols[-1]:
    if st.button("🎲 Random Sample", key="random_sample", use_container_width=True):
        selected_p = random.choice(presets)
        st.session_state.ticket_input = selected_p["ticket"]
        st.rerun()

ticket_text = st.text_area(
    "Ticket Body",
    value=st.session_state.ticket_input,
    height=130,
    placeholder="Paste or write customer ticket here...",
    label_visibility="collapsed",
)
st.session_state.ticket_input = ticket_text

# Action Controls
col_btn1, col_btn2, col_info = st.columns([1.5, 1, 3.5])

with col_btn1:
    analyze_clicked = st.button("⚡ Analyze & Triage Ticket", type="primary", use_container_width=True)

with col_btn2:
    if st.button("Clear Input", use_container_width=True):
        st.session_state.ticket_input = ""
        st.rerun()

with col_info:
    if is_live_mode:
        st.info("🌐 Mode: **Live API** (Connecting to TypeSafe & Groq)", icon="ℹ️")
    else:
        st.warning("🧪 Mode: **Simulation Demo** (Instant local mock evaluation)", icon="⚡")


# -----------------------------------------------------------------------------
# Analysis Execution
# -----------------------------------------------------------------------------
if analyze_clicked:
    clean_ticket = ticket_text.strip()
    if len(clean_ticket) < 5:
        st.error("Please enter a valid ticket (at least 5 characters).")
    else:
        with st.spinner("Analyzing ticket with Jev decision model..."):
            start_time = time.time()
            decision = None
            reply = ""
            error_msg = None

            if is_live_mode:
                try:
                    # Dynamically set in-memory environment variables from sidebar inputs if provided
                    if input_typesafe_key.strip():
                        os.environ["TYPESAFE_API_KEY"] = input_typesafe_key.strip()
                    if input_groq_key.strip():
                        os.environ["GROQ_API_KEY"] = input_groq_key.strip()

                    from services.jev_service import analyze_ticket
                    decision = analyze_ticket(clean_ticket)

                except Exception as exc:
                    logger.exception("Live Jev analysis failed")
                    error_msg = str(exc)
                    st.error(
                        f"⚠️ Live Jev API call failed: {exc}\n\n"
                        "💡 Tip: Switch to 'Simulation / Demo Mode' in the sidebar to test without active API keys."
                    )
            else:
                # Simulation mode
                time.sleep(0.4)  # Subtle realistic touch
                decision = simulate_jev_decision(clean_ticket)

            if decision is not None:
                # Deterministic Route Decision
                route, needs_human, rule_reason = choose_route_custom(
                    department=decision.department,
                    dept_conf=decision.department_confidence,
                    urgency=decision.urgency_score,
                    human_prob=decision.human_review_probability,
                    human_thresh=human_threshold,
                    dept_thresh=dept_threshold,
                    urgency_thresh=urgency_threshold,
                )

                # Suggested Reply Drafting
                if is_live_mode:
                    try:
                        from services.response_chain import draft_reply
                        reply = draft_reply(clean_ticket, decision, route)
                    except Exception as exc:
                        logger.warning(f"Live reply generation failed: {exc}")
                        reply = (
                            "Jev triage succeeded, but LangChain/Groq reply drafting was skipped "
                            f"or encountered an issue: {exc}"
                        )
                else:
                    reply = simulate_draft_reply(clean_ticket, decision, route)

                elapsed = time.time() - start_time

                result_data = {
                    "timestamp": time.strftime("%H:%M:%S"),
                    "ticket": clean_ticket,
                    "model": getattr(decision, "model", "jev-latest"),
                    "department": decision.department,
                    "department_confidence": float(decision.department_confidence),
                    "urgency_score": float(decision.urgency_score),
                    "urgency_confidence": float(decision.urgency_confidence),
                    "refund_probability": float(decision.refund_probability),
                    "human_review_probability": float(decision.human_review_probability),
                    "route": route,
                    "needs_human": needs_human,
                    "rule_reason": rule_reason,
                    "reply": reply,
                    "latency": round(elapsed, 2),
                    "mode": "Live" if is_live_mode else "Simulation",
                }

                st.session_state.latest_result = result_data
                st.session_state.history.insert(0, result_data)


# -----------------------------------------------------------------------------
# Results Presentation
# -----------------------------------------------------------------------------
res = st.session_state.latest_result

if res:
    st.write("---")
    st.markdown("## 📊 Triage Breakdown")

    tab_overview, tab_json, tab_history = st.tabs(["🚀 Triage Overview", "🔍 Raw JSON & Audit", "📜 Session History"])

    # ---------------- TAB 1: OVERVIEW ----------------
    with tab_overview:
        # 1. Jev Decision Metrics
        st.markdown("#### 1️⃣ Jev Decision Layer (System One)")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        # Department Card
        with col_m1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">🏢 Target Department</div>
                    <div class="metric-value">{res['department'].title()}</div>
                    <div class="metric-sub">Confidence: <strong>{res['department_confidence']*100:.1f}%</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(res['department_confidence'], 0.0), 1.0))

        # Urgency Card
        with col_m2:
            urg_val = res['urgency_score']
            urg_color = "#34d399" if urg_val < 1.0 else ("#fbbf24" if urg_val < 2.0 else ("#f97316" if urg_val < 2.5 else "#f87171"))
            urg_label = "Low" if urg_val < 1.0 else ("Medium" if urg_val < 2.0 else ("High" if urg_val < 2.5 else "Critical"))
            
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">⏱️ Urgency Score (0–3)</div>
                    <div class="metric-value" style="color: {urg_color}">{urg_val:.2f} <span style="font-size: 0.9rem; font-weight:600;">({urg_label})</span></div>
                    <div class="metric-sub">Rubric Confidence: <strong>{res['urgency_confidence']*100:.1f}%</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(urg_val / 3.0, 0.0), 1.0))

        # Refund Probability Card
        with col_m3:
            refund_val = res['refund_probability']
            refund_color = "#f87171" if refund_val >= 0.5 else "#34d399"
            
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">💰 Refund Risk</div>
                    <div class="metric-value" style="color: {refund_color}">{refund_val*100:.1f}%</div>
                    <div class="metric-sub">TypeSafe Noul Probability</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(refund_val, 0.0), 1.0))

        # Human Review Card
        with col_m4:
            hr_val = res['human_review_probability']
            hr_color = "#f87171" if hr_val >= 0.65 else "#34d399"
            
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">👤 Human Review Prob</div>
                    <div class="metric-value" style="color: {hr_color}">{hr_val*100:.1f}%</div>
                    <div class="metric-sub">Escalation Gate Assessment</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(hr_val, 0.0), 1.0))

        st.write("")

        # 2. Deterministic Business Automation
        st.markdown("#### 2️⃣ Deterministic Automation & Routing Guardrail")
        is_esc = res['needs_human']
        banner_cls = "route-escalated" if is_esc else "route-automated"
        hdr_cls = "route-header-escalated" if is_esc else "route-header-automated"
        hdr_icon = "🚨 ESCALATED ACTION REQUIRED" if is_esc else "✅ AUTOMATED QUEUE ROUTE"

        st.markdown(
            f"""
            <div class="route-banner {banner_cls}">
                <div class="route-header {hdr_cls}">
                    <span>{hdr_icon}</span>
                </div>
                <h3 class="route-destination">{res['route']}</h3>
                <p class="route-reason"><strong>Trigger Reason:</strong> {res['rule_reason']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        # 3. LangChain Suggested Reply
        st.markdown("#### 3️⃣ Suggested AI Response (LangChain + Groq)")
        st.caption("AI-generated draft complying with SaaS support guardrails (under 120 words, non-committal on unverified claims).")

        st.markdown(
            f"""
            <div class="reply-box">
                {res['reply']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Word count & copy tool
        reply_words = len(res['reply'].split())
        col_r1, col_r2 = st.columns([1, 4])
        with col_r1:
            st.caption(f"📝 Word Count: **{reply_words} words**")
        with col_r2:
            st.caption(f"⚡ Latency: **{res['latency']}s** | Model: **{res['model']}** | Engine: **{res['mode']}**")

    # ---------------- TAB 2: RAW JSON ----------------
    with tab_json:
        st.markdown("#### Complete Decision Payload")
        st.caption("Structured JSON output reflecting the Jev decision dictionary, deterministic routing, and suggested response.")
        st.json(res)

    # ---------------- TAB 3: HISTORY ----------------
    with tab_history:
        st.markdown("#### Triaged Tickets in This Session")
        if not st.session_state.history:
            st.info("No tickets triaged yet.")
        else:
            for i, h in enumerate(st.session_state.history):
                esc_tag = "🚨 Escalated" if h["needs_human"] else "✅ Safe Queue"
                with st.expander(f"[{h['timestamp']}] {h['department'].title()} - {h['route']} ({esc_tag})"):
                    st.write(f"**Ticket:** {h['ticket']}")
                    st.write(f"**Reason:** {h['rule_reason']}")
                    st.write(f"**Urgency:** {h['urgency_score']:.2f} | **Refund Prob:** {h['refund_probability']*100:.1f}%")
                    st.info(f"**Draft Reply:** {h['reply']}")
