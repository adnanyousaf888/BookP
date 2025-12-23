# chatbot/chatbot.py

from typing import List, Dict, Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from chatbot.graph import run_graph
from chatbot.retrieval import search_database


# --------------------------------------------------
# FORMAT CHAT HISTORY (Mongo → LangChain)
# --------------------------------------------------
def format_history(history_docs: List[Dict[str, Any]]):
    """
    Convert MongoDB session messages into LangChain message objects.
    """
    lc_history = []

    for item in history_docs:
        sender = item.get("sender")
        msg = (item.get("message") or "").strip()

        if not msg:
            continue

        if sender == "system":
            continue

        if sender == "user":
            lc_history.append(HumanMessage(content=msg))
        else:
            lc_history.append(AIMessage(content=msg))

    return lc_history


# --------------------------------------------------
# BUILD CONTEXT FROM WEBSITE DATA
# --------------------------------------------------
def build_context(docs: List[Dict[str, Any]]) -> str:
    """
    Combine retrieved MongoDB website documents into a single context string.
    """
    if not docs:
        return ""

    parts = []
    for d in docs:
        text = (d.get("text") or "").strip()
        if text:
            parts.append(text)

    return "\n\n".join(parts)


# --------------------------------------------------
# MAIN ANSWER FUNCTION (USED BY API)
# --------------------------------------------------
def answer_from_database(
    email: str,
    query: str,
    history_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Retrieve website data from MongoDB and answer using LangGraph.
    """

    # 1️⃣ Convert MongoDB chat logs → LangChain history
    lc_history = format_history(history_docs)

    # 2️⃣ Retrieve relevant website content
    retrieved_docs = search_database(query)
    context = build_context(retrieved_docs)

    # 🔍 DEBUG (VERY IMPORTANT — keep for now)
    print("🔍 Retrieved docs:", len(retrieved_docs))
    print("📄 Context length:", len(context))

    # 3️⃣ If NO website data → strict fallback (system prompt rule)
    if not context.strip():
        return {
            "response": (
                "Thanks for your question. "
                "I don’t see specific details about this in my current data, "
                "but I’d be happy to help guide you."
            ),
            "analytics": {},
        }

    # 4️⃣ Inject website context into LangGraph
    # We pass it as a SYSTEM message so the model is forced to use it
    system_context = SystemMessage(
        content=f"Website data (use ONLY this information):\n\n{context}"
    )

    # 5️⃣ Call LangGraph with context + history
    answer = run_graph(
        question=query,
        history=[system_context] + lc_history,
    )

    return {
        "response": str(answer),
        "analytics": {},
    }
