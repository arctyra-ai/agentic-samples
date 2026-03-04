"""Week 10: Production Deployment - Streamlit UI

Streamlit web interface for the code review multi-agent system.
Run with: streamlit run app.py

Demonstrates: Streamlit deployment, file upload, real-time agent status, structured output display.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


def mock_review(code: str, filename: str) -> dict:
    """Mock review for demonstration without API keys.
    Replace with actual code_review_agents.review_code in production.
    """
    import time
    time.sleep(0.5)  # Simulate latency
    return {
        "analyzer_findings": [
            {"line": 3, "severity": "medium", "type": "smell", "description": "Function too long"}
        ],
        "security_findings": [
            {"line": 1, "severity": "high", "vulnerability": "sql_injection",
             "description": "Potential SQL injection via string formatting"}
        ] if "f'" in code and "select" in code.lower() else [],
        "improvement_suggestions": [
            {"line": 1, "category": "documentation", "suggestion": "Add docstring", "priority": "medium"}
        ],
        "synthesized_report": {
            "summary": "Code review complete. Found potential issues.",
            "critical_issues": [],
            "recommendations": ["Add input validation", "Use parameterized queries"],
            "overall_rating": "needs_work",
        },
        "token_usage": {"total_input": 2000, "total_output": 800, "calls": 4},
    }


def run_app():
    st.set_page_config(page_title="Code Review Agent", layout="wide")
    st.title("Multi-Agent Code Review")
    st.markdown("Upload a Python file or paste code for automated review by 3 specialist agents.")

    # Sidebar
    st.sidebar.header("Configuration")
    model = st.sidebar.selectbox("Model", ["claude-sonnet-4-20250514", "gpt-4o"])
    budget = st.sidebar.slider("Budget limit ($)", 0.10, 5.00, 0.50, 0.10)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Agent Weights**")
    w_security = st.sidebar.slider("Security", 0.5, 3.0, 2.0, 0.5)
    w_analyzer = st.sidebar.slider("Analyzer", 0.5, 3.0, 1.5, 0.5)
    w_improver = st.sidebar.slider("Improver", 0.5, 3.0, 1.0, 0.5)

    # Input
    tab_upload, tab_paste = st.tabs(["Upload File", "Paste Code"])

    code = None
    filename = "pasted_code.py"

    with tab_upload:
        uploaded = st.file_uploader("Choose a Python file", type=["py"])
        if uploaded:
            code = uploaded.read().decode("utf-8")
            filename = uploaded.name

    with tab_paste:
        pasted = st.text_area("Paste code here", height=300)
        if pasted:
            code = pasted

    if code:
        st.markdown("---")
        st.subheader(f"Reviewing: {filename}")
        st.code(code, language="python")

        if st.button("Run Review", type="primary"):
            with st.spinner("Running 3 agents in parallel..."):
                # In production, replace mock_review with:
                # from week07_multi_agent_systems.code_review_agents import review_code
                # result = review_code(code, filename)
                result = mock_review(code, filename)

            # Results
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Analyzer", f"{len(result['analyzer_findings'])} issues")
                for f in result["analyzer_findings"]:
                    severity_color = {"high": "red", "medium": "orange", "low": "blue"}.get(f.get("severity"), "gray")
                    st.markdown(f"**Line {f.get('line', '?')}** ({f.get('severity', 'info')}): {f.get('description', '')}")

            with col2:
                st.metric("Security", f"{len(result['security_findings'])} issues")
                for f in result["security_findings"]:
                    st.markdown(f"**Line {f.get('line', '?')}** ({f.get('severity', 'info')}): {f.get('description', '')}")

            with col3:
                st.metric("Improver", f"{len(result['improvement_suggestions'])} suggestions")
                for f in result["improvement_suggestions"]:
                    st.markdown(f"**Line {f.get('line', '?')}** ({f.get('category', '')}): {f.get('suggestion', '')}")

            # Synthesized report
            st.markdown("---")
            st.subheader("Synthesized Report")
            report = result["synthesized_report"]
            rating = report.get("overall_rating", "unknown")
            rating_colors = {"pass": "green", "needs_work": "orange", "fail": "red"}
            st.markdown(f"**Rating:** :{rating_colors.get(rating, 'gray')}[{rating.upper()}]")
            st.markdown(f"**Summary:** {report.get('summary', 'N/A')}")

            if report.get("recommendations"):
                st.markdown("**Recommendations:**")
                for rec in report["recommendations"]:
                    st.markdown(f"- {rec}")

            # Token usage
            usage = result.get("token_usage", {})
            st.markdown("---")
            st.caption(
                f"Tokens: {usage.get('total_input', 0)} in / {usage.get('total_output', 0)} out | "
                f"API calls: {usage.get('calls', 0)}"
            )


if __name__ == "__main__":
    if STREAMLIT_AVAILABLE:
        run_app()
    else:
        print("Streamlit not installed. Run: pip install streamlit")
        print("Then: streamlit run app.py")
