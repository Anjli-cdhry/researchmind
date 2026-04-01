import streamlit as st
import sys
import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agent import run_research

# Page configuration
st.set_page_config(
    page_title="ResearchMind",
    page_icon="🧠",
    layout="wide"
)


def generate_pdf(content: str, query: str) -> bytes:
    """
    Generate a professional PDF report from the research content.
    Returns PDF as bytes for download.
    """
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=12,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=16,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=8,
        alignment=TA_LEFT
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#666666"),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    story = []

    # Header
    story.append(Paragraph("🧠 ResearchMind", title_style))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        meta_style
    ))
    story.append(Paragraph(f"Query: {query}", meta_style))
    story.append(Spacer(1, 0.2 * inch))

    # Parse and add content
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.1 * inch))
            continue
        if line.startswith("## "):
            story.append(Paragraph(line.replace("## ", ""), heading_style))
        elif line.startswith("### "):
            story.append(Paragraph(line.replace("### ", ""), heading_style))
        elif line.startswith("* ") or line.startswith("- "):
            text = line.replace("* ", "• ").replace("- ", "• ")
            story.append(Paragraph(text, body_style))
        elif line.startswith("---"):
            story.append(Spacer(1, 0.1 * inch))
        else:
            line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
            story.append(Paragraph(line, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ── Session state initialization ─────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    # Each item: {"query": str, "response": str, "timestamp": str}
    st.session_state.history = []

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None


# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 ResearchMind")
    st.markdown("*Autonomous AI Research Agent*")
    st.divider()

    st.markdown("**Powered by:**")
    st.markdown("- 🔗 LangGraph + LangChain")
    st.markdown("- ⚡ Groq (Llama 4)")
    st.markdown("- 🔍 Tavily Web Search")
    st.markdown("- 🧠 ChromaDB Memory")
    st.divider()

    st.markdown("**Features:**")
    st.markdown("- ✅ Autonomous web research")
    st.markdown("- ✅ Self-reflection loop")
    st.markdown("- ✅ Long-term memory")
    st.markdown("- ✅ PDF export")
    st.markdown("- ✅ Research history")
    st.divider()

    # Research history section
    if st.session_state.history:
        st.markdown("**📚 Research History:**")
        for i, item in enumerate(reversed(st.session_state.history)):
            # Show first 40 chars of query as button label
            label = item["query"][:40] + "..." if len(item["query"]) > 40 else item["query"]
            if st.button(f"🔍 {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state.selected_history = item
        st.divider()

    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.selected_history = None
        st.rerun()

    # Session query count
    research_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(f"**Queries this session:** {research_count}")


# ── Main area ────────────────────────────────────────────
st.title("🧠 ResearchMind")
st.caption("Autonomous AI Research Agent — powered by LangChain + Groq + Tavily")

# Show selected history item if clicked from sidebar
if st.session_state.selected_history:
    item = st.session_state.selected_history
    st.info(f"📖 Viewing past research: **{item['query']}** — {item['timestamp']}")
    st.markdown(item["response"])
    pdf_bytes = generate_pdf(item["response"], item["query"])
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_bytes,
        file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf",
        key="pdf_history"
    )
    if st.button("✖ Close history view"):
        st.session_state.selected_history = None
        st.rerun()
    st.divider()

# Display current chat messages
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # PDF download button under each assistant message
        if msg["role"] == "assistant":
            user_query = ""
            if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
                user_query = st.session_state.messages[i - 1]["content"]
            pdf_bytes = generate_pdf(msg["content"], user_query)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key=f"pdf_{i}"
            )

# Chat input
query = st.chat_input("Enter your research topic or question...")

if query:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Run agent with streaming simulation
    with st.chat_message("assistant"):
        # Placeholder for streaming effect
        placeholder = st.empty()
        status = st.status("🔍 Researching...", expanded=True)

        with status:
            st.write("🌐 Searching the web...")
            st.write("🧠 Analyzing and synthesizing findings...")
            st.write("✍️ Generating structured report...")

        try:
            result = run_research(query)
            status.update(label="✅ Research complete!", state="complete", expanded=False)

            # Stream the response word by word
            words = result.split(" ")
            streamed = ""
            for word in words:
                streamed += word + " "
                placeholder.markdown(streamed + "▌")
                import time
                time.sleep(0.01)

            # Final clean render
            placeholder.markdown(result)

            st.session_state.messages.append({
                "role": "assistant",
                "content": result
            })

            # Save to history
            st.session_state.history.append({
                "query": query,
                "response": result,
                "timestamp": datetime.now().strftime("%b %d, %I:%M %p")
            })

            # PDF download button
            pdf_bytes = generate_pdf(result, query)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="pdf_new"
            )

        except Exception as e:
            error_msg = str(e)
            status.update(label="⚠️ Partial result", state="error", expanded=False)

            if "failed_generation" in error_msg:
                match = re.search(
                    r"'failed_generation':\s*'((?:[^'\\]|\\.)*)'\s*(?:,|\})",
                    error_msg,
                    re.DOTALL
                )
                if match:
                    content = match.group(1)
                    content = content.replace("\\n", "\n")
                    content = content.replace("\\'", "'")
                    content = content.replace('\\"', '"')

                    # Stream extracted content
                    words = content.split(" ")
                    streamed = ""
                    for word in words:
                        streamed += word + " "
                        placeholder.markdown(streamed + "▌")
                        import time
                        time.sleep(0.01)
                    placeholder.markdown(content)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": content
                    })
                    st.session_state.history.append({
                        "query": query,
                        "response": content,
                        "timestamp": datetime.now().strftime("%b %d, %I:%M %p")
                    })
                    pdf_bytes = generate_pdf(content, query)
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        key="pdf_fallback"
                    )
                else:
                    placeholder.error(f"Something went wrong: {error_msg}")
            else:
                placeholder.error(f"Something went wrong: {error_msg}")