import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from src.tools import web_search, summarize_findings
from src.memory import AgentMemory

load_dotenv()

# Initialize Groq LLM — this model has reliable tool calling support
llm = ChatGroq(
    api_key=os.getenv("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"),
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0
)

# Bind tools directly to the LLM
llm_with_tools = llm.bind_tools([web_search, summarize_findings])

# Initialize memory
memory = AgentMemory()

# Initialize critic LLM for self-reflection (no tools needed)
critic_llm = ChatGroq(
    api_key=os.getenv("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"),
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0
)

SYSTEM_PROMPT = """You are ResearchMind, an expert autonomous research agent.

When given a research question:
1. ALWAYS call web_search tool first with a specific search query
2. Call web_search again with a different query to get more information
3. Synthesize all results into a detailed structured report

Your final response MUST have these exact sections:
## Research Report: [Topic Title]

### Executive Summary
[2-3 sentences summarizing key findings]

### Key Findings
[5-7 bullet points with specific facts and data]

### Detailed Analysis
[3-4 paragraphs with in-depth analysis]

### Conclusion
[2-3 sentences on key takeaways]

### Sources
[List all URLs from search results]"""


def self_reflect(query: str, response: str) -> dict:
    """
    Evaluate the quality of the research report.
    Returns score, feedback, and pass/fail status.
    """
    critique_prompt = f"""You are a strict research quality evaluator.

Research Question: {query}

Agent Response:
{response}

Evaluate on:
1. Has proper sections (Summary, Findings, Analysis, Conclusion, Sources)?
2. Contains specific facts and data points?
3. Is detailed enough (300+ words)?
4. Cites sources with URLs?

Respond EXACTLY in this format:
SCORE: [number 1-10]
FEEDBACK: [one sentence]
PASS: [YES or NO]"""

    result = critic_llm.invoke([HumanMessage(content=critique_prompt)])
    content = result.content

    score = 5
    feedback = "Needs more detail."
    passed = False

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except:
                score = 5
        elif line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()
        elif line.startswith("PASS:"):
            passed = "YES" in line.upper()

    return {"score": score, "feedback": feedback, "passed": passed}


def run_research(query: str) -> str:
    """
    Run the research agent on a given query with self-reflection loop.
    Returns a structured, self-reflected research report.
    """
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=query)
    ]

    final_response = ""

    # Agentic loop — keeps running until no more tool calls
    try:
        for _ in range(5):
            response = llm_with_tools.invoke(messages)
            messages.append(response)

            # If no tool calls, agent is done
            if not response.tool_calls:
                final_response = response.content
                break

            # Execute each tool call and add results back
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                if tool_name == "web_search":
                    result = web_search.invoke(tool_args)
                elif tool_name == "summarize_findings":
                    result = summarize_findings.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"

                from langchain_core.messages import ToolMessage
                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    )
                )

        # If agent never gave a text response, use last message content
        if not final_response:
            final_response = response.content

    except Exception as e:
        error_str = str(e)
        # Agent generated content but failed on tool format
        # Extract the report directly from the error
        if "failed_generation" in error_str:
            import re
            # Try to extract content between failed_generation key
            patterns = [
                r"'failed_generation':\s*'((?:[^'\\]|\\.)*)'\s*(?:,|\})",
                r'"failed_generation":\s*"((?:[^"\\]|\\.)*)"',
            ]
            for pattern in patterns:
                match = re.search(pattern, error_str, re.DOTALL)
                if match:
                    final_response = match.group(1)
                    final_response = final_response.replace("\\n", "\n")
                    final_response = final_response.replace("\\'", "'")
                    final_response = final_response.replace('\\"', '"')
                    break

            # If regex didn't work, do simple string extraction
            if not final_response:
                start = error_str.find("'failed_generation': '")
                if start != -1:
                    start += len("'failed_generation': '")
                    end = error_str.rfind("'}")
                    if end != -1:
                        final_response = error_str[start:end]
                        final_response = final_response.replace("\\n", "\n")
                        final_response = final_response.replace("\\'", "'")
        else:
            raise e

    # If still no response
    if not final_response:
        final_response = "I was unable to complete the research. Please try again."

    # Self-reflection quality check
    critique = self_reflect(query, final_response)

    # Add quality score to bottom of report
    quality_note = f"\n\n---\n*Research Quality Score: {critique['score']}/10*"
    final_response = final_response + quality_note

    # Save to memory
    memory.add_human(query)
    memory.add_ai(final_response)

    return final_response