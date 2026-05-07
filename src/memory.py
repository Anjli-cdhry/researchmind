from langchain_core.messages import HumanMessage, AIMessage
import chromadb
import hashlib

class AgentMemory:
    """
    Manages both short-term conversation memory and
    long-term persistent memory using ChromaDB vector store.
    """

    def __init__(self):
        # Short-term: stores recent conversation messages
        self.history = []
        self.context_window = 10

        # Long-term: persistent ChromaDB storage
        self.chroma_client = chromadb.PersistentClient(path="./memory_store")
        self.collection = self.chroma_client.get_or_create_collection(
            name="research_memory"
        )

    def add_human(self, message: str):
        """Add a user message to short-term memory."""
        self.history.append(HumanMessage(content=message))

    def add_ai(self, message: str):
        """Add an AI response to short-term and long-term memory."""
        self.history.append(AIMessage(content=message))
        # Save to long-term memory with a unique ID
        doc_id = hashlib.md5(message[:100].encode()).hexdigest()
        self.collection.upsert(
            documents=[message],
            ids=[doc_id]
        )

    def get_recent(self):
        """Return the most recent messages within the context window."""
        return self.history[-self.context_window:]

    def search_long_term(self, query: str, n_results: int = 2) -> str:
        """
        Search long-term memory for previously researched similar topics.
        Returns relevant past research as context.
        """
        count = self.collection.count()
        if count == 0:
            return ""

        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )

        if results["documents"] and results["documents"][0]:
            past = results["documents"][0]
            return "\n\n---\n".join(past)
        return ""

    def clear(self):
        """Clear short-term conversation history."""
        self.history = []