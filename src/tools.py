import os
from dotenv import load_dotenv
from tavily import TavilyClient
from langchain_core.tools import tool

load_dotenv()

# Initialize Tavily client with API key from environment
tavily = TavilyClient(api_key=os.getenv("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"))

@tool
def web_search(query: str) -> str:
    """Search the web for current and accurate information on any topic."""
    try:
        results = tavily.search(query=query, max_results=5)
        output = ""
        for r in results["results"]:
            output += f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n\n"
        return output if output else "No results found."
    except Exception as e:
        return f"Search failed: {str(e)}"

@tool
def summarize_findings(text: str) -> str:
    """Summarize and structure research findings into a clean, readable report."""
    return f"=== RESEARCH SUMMARY ===\n{text}\n========================"