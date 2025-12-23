# chatbot/graph.py

from typing import List, Dict, Any
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import (
  SystemMessage,
  HumanMessage,
  AIMessage,
  BaseMessage,
)
from langgraph.graph import StateGraph, END

from chatbot.retrieval import search_database
from settings import OPENAI_API_KEY, SYSTEM_PROMPT


llm = ChatOpenAI(
  model="gpt-4o-mini",
  api_key=OPENAI_API_KEY,
  temperature=0.2,
)

system_msg = SystemMessage(content=SYSTEM_PROMPT)


class ChatState(TypedDict):
  question: str
  history: List[BaseMessage]
  retrieved_context: str
  answer: str


def retrieve_node(state: ChatState) -> Dict[str, Any]:
  query = state["question"]
  pages = search_database(query)

  if not pages:
    context = ""
  else:
    context = "\n\n--- PAGE ----------------------\n\n".join(
      p["text"] for p in pages
    )

  return {"retrieved_context": context}


def generate_node(state: ChatState) -> Dict[str, Any]:
  history = state.get("history", [])
  question = state["question"]
  context = state["retrieved_context"]

  messages: List[BaseMessage] = [system_msg]
  messages.extend(history)

  if context.strip():
    user_msg = (
      "Here is relevant website context that may help answer the question:\n\n"
      f"{context}\n\n"
      f"Now answer the user question.\n\n"
      f"QUESTION: {question}"
    )
  else:
    user_msg = (
      "No relevant website context was found.\n"
      "You must still follow the system rules and avoid inventing facts.\n\n"
      f"QUESTION: {question}"
    )

  messages.append(HumanMessage(content=user_msg))
  resp = llm.invoke(messages)
  return {"answer": resp.content}


graph = StateGraph(ChatState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

app = graph.compile()


def run_graph(question: str, history: List[BaseMessage]) -> str:
  state: ChatState = {
    "question": question,
    "history": history,
    "retrieved_context": "",
    "answer": "",
  }
  output = app.invoke(state)
  return output["answer"]
