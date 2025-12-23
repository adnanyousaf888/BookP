# chatbot/analytics.py  (FINAL BOOKPROO VERSION — FULL FILE)

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from settings import OPENAI_API_KEY


# ================================================================
# TIMEZONE → PAKISTAN (UTC+5)
# ================================================================
def now_pk():
    return datetime.utcnow() + timedelta(hours=5)


# ================================================================
# LLM (Analytics Model)
# ================================================================
analytics_llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=OPENAI_API_KEY,
    temperature=0.0,
)


# ================================================================
# BOOKPROO SERVICES — from website dropdown
# ================================================================
BOOKPROO_SERVICES = [
    "ghostwriting",
    "editing & proofreading",
    "proofreading",
    "editing",
    "cover design",
    "book cover design",
    "formatting & publishing",
    "book formatting",
    "publishing",
    "isbn & copyright",
    "audiobooks",
    "book marketing",
    "author website",
    "website development for authors",
    "author media coverage",
    "media coverage",
    "book launch",
]


# ================================================================
# SYSTEM PROMPT (Highly optimized for BookProo)
# ================================================================
ANALYTICS_SYSTEM = SystemMessage(
    content=(
        "You are an analytics engine for The Book Promoters (BookProo chatbot).\n"
        "Analyze ONLY the *user* messages. Ignore all bot/system messages.\n\n"

        "VALID SERVICES YOU MUST MATCH:\n"
        f"{', '.join(BOOKPROO_SERVICES)}\n\n"

        "Your output MUST be STRICT JSON:\n"
        "{\n"
        '  \"summary\": \"...\",\n'
        '  \"primary_service\": \"...\",\n'
        '  \"secondary_services\": [],\n'
        '  \"interest_level\": \"low|medium|high\",\n'
        '  \"sentiment_label\": \"negative|neutral|positive\",\n'
        '  \"sentiment_score\": 0.0\n'
        "}\n\n"

        "SERVICE DETECTION RULES:\n"
        "- Detect a service ONLY if the user clearly mentions it.\n"
        "- Match user message against the service list.\n"
        "- If multiple services appear → most discussed = primary.\n"
        "- Remaining = secondary_services.\n"
        "- If no match → primary_service = \"Unknown\".\n\n"

        "SUMMARY RULES:\n"
        "- 2–4 lines maximum.\n"
        "- Focus ONLY on what user wants or asks.\n\n"

        "INTEREST LEVEL RULES:\n"
        "- high    → user wants pricing, wants to start, urgent, clear buying intent.\n"
        "- medium  → user exploring services, asking details.\n"
        "- low     → vague questions / casual talk.\n\n"

        "SENTIMENT RULES:\n"
        "- Analyze ONLY user tone.\n\n"

        "IMPORTANT:\n"
        "- Output MUST be STRICT JSON. No explanations.\n"
        "- DO NOT hallucinate.\n"
        "- NEVER output text outside JSON.\n"
    )
)


# ================================================================
# Convert user messages → clean transcript
# (Do NOT include 'USER:' labels — keeps model accurate)
# ================================================================
def user_messages_to_text(msgs: List[Dict[str, Any]]) -> str:
    return "\n".join(
        m["message"].strip()
        for m in msgs
        if m.get("sender") == "user" and m.get("message")
    )


# ================================================================
# MAIN ANALYTICS FUNCTION — CALLED BY /end_chat
# ================================================================
def analyze_new_messages(new_msgs: List[Dict[str, Any]]) -> Dict[str, Any]:

    # Filter ONLY user messages
    user_msgs = [m for m in new_msgs if m.get("sender") == "user"]

    # No user messages → default analytics
    if not user_msgs:
        return {
            "timestamp": now_pk(),
            "summary": "No new user messages.",
            "primary_service": "Unknown",
            "secondary_services": [],
            "interest_level": "low",
            "sentiment_label": "neutral",
            "sentiment_score": 0.5,
        }

    transcript = user_messages_to_text(user_msgs)

    messages = [
        ANALYTICS_SYSTEM,
        HumanMessage(
            content=(
                "Analyze these user messages:\n\n"
                f"{transcript}\n\n"
                "Return STRICT JSON only."
            )
        ),
    ]

    try:
        resp = analytics_llm.invoke(messages)
        data = json.loads(resp.content.strip())

    except Exception as e:
        print("⚠ analytics error:", e)
        data = {
            "summary": "Analytics failed.",
            "primary_service": "Unknown",
            "secondary_services": [],
            "interest_level": "medium",
            "sentiment_label": "neutral",
            "sentiment_score": 0.5,
        }

    # Add timestamp to every analytics entry
    data["timestamp"] = now_pk()
    return data
