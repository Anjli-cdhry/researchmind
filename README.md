# 🧠 ResearchMind — Autonomous AI Research Agent

An autonomous AI research agent that conducts deep web research, synthesizes findings, and delivers structured, cited reports with self-reflection quality scoring.

## 🎥 Demo
[YouTube Demo Link] — https://youtu.be/zsxBNxHsN7Y

## ✨ Features

- 🔍 **Autonomous Web Research** — Uses Tavily API to search and retrieve real-time information
- 🧠 **Self-Reflection Loop** — Agent evaluates its own output quality and retries if score < 7/10
- 💾 **Long-Term Memory** — ChromaDB stores past research for context-aware responses
- 📄 **PDF Export** — Download any research report as a professional PDF
- 📚 **Research History** — Sidebar tracks all past queries in the session
- ⚡ **Streaming Response** — Real-time word-by-word response rendering

## 🏗️ Architecture
```
User Query
    ↓
LLM Planner (Llama 4 via Groq)
    ↓
Tool Router
    ↓
Web Search (Tavily) + Summarizer
    ↓
Memory Module (ChromaDB)
    ↓
Self-Reflection + Quality Score
    ↓
Structured Research Report
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Llama 4 Scout via Groq |
| Agent Framework | LangGraph + LangChain |
| Web Search | Tavily API |
| Long-term Memory | ChromaDB |
| UI | Streamlit |
| PDF Generation | ReportLab |

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Groq API key (free at console.groq.com)
- Tavily API key (free at app.tavily.com)

### Installation
```bash
# Clone the repository
git clone https://github.com/Anjli-cdhry/researchmind.git
cd researchmind

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your API keys to .env
```

### Environment Variables

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Run the Application
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 📁 Project Structure
```
researchmind/
├── src/
│   ├── agent.py      # Core agent with ReAct loop + self-reflection
│   ├── tools.py      # Web search + summarization tools
│   └── memory.py     # Short-term + long-term memory module
├── app.py            # Streamlit UI with streaming + PDF export
├── requirements.txt  # Project dependencies
└── .env              # API keys (not committed)
```

## 🧠 How It Works

1. **User submits a research query** via the chat interface
2. **LLM Planner** breaks the query into search tasks
3. **Tool Router** executes web searches using Tavily API
4. **Memory Module** stores and retrieves context from ChromaDB
5. **Self-Reflection Loop** scores the output (1-10) and retries if quality is low
6. **Structured Report** is generated with Executive Summary, Key Findings, Analysis, Conclusion, and Sources
7. **PDF Export** allows downloading the complete research report


