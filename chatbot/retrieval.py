# chatbot/retrieval.py

import math
import re
from typing import List, Dict

from embeddings.embedder import embed_text
from database.mongo import get_website_col


# ----------------------------------
# QUERY NORMALIZATION (VERY IMPORTANT)
# ----------------------------------
def normalize_query(query: str) -> str:
    """
    Make user queries less strict so semantic + keyword search works
    even if wording is different from website text.
    """
    q = query.lower().strip()

    mappings = {
        "who are you": "about us",
        "tell me about you": "about us",
        "about book promoters": "about us",
        "company information": "about us",
        "what is bookproo": "about us",
        "what do you do": "services",
        "what services do you offer": "services",
        "services offered": "services",
        "list of services": "services",
    }

    for key, value in mappings.items():
        if key in q:
            return value

    return q


# ----------------------------------
# COSINE SIMILARITY
# ----------------------------------
def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))

    if na == 0 or nb == 0:
        return 0.0

    return dot / (na * nb)


# ----------------------------------
# KEYWORD FALLBACK (RELAXED)
# ----------------------------------
def escape_regex(text: str) -> str:
    return re.escape(text)


def keyword_fallback(query: str) -> List[Dict]:
    """
    Fallback keyword search using OR logic (not AND),
    so partial matches like 'about us' still work.
    """
    col = get_website_col()

    query = query.lower()
    keywords = [escape_regex(k) for k in query.split() if k.strip()]

    if not keywords:
        return []

    conditions = [{"text": {"$regex": k, "$options": "i"}} for k in keywords]

    results = list(
        col.find(
            {"$or": conditions},  # 🔥 FIX: OR instead of AND
            {"_id": 0, "url": 1, "text": 1, "embedding": 1},
        )
    )

    return results


# ----------------------------------
# HYBRID SEARCH (SEMANTIC + KEYWORD)
# ----------------------------------
def search_database(query: str, top_k: int = 5) -> List[Dict]:
    col = get_website_col()

    # 🔥 Normalize query first
    normalized_query = normalize_query(query)

    # ----------------------------------
    # SEMANTIC SEARCH
    # ----------------------------------
    query_emb = embed_text(normalized_query)

    docs = list(
        col.find(
            {"embedding": {"$exists": True}},
            {"_id": 0, "url": 1, "text": 1, "embedding": 1},
        )
    )

    scored = []
    for d in docs:
        sim = cosine_similarity(query_emb, d["embedding"])
        scored.append((sim, d))

    scored.sort(key=lambda x: x[0], reverse=True)

    # 🔥 LOWER THRESHOLD (was too strict)
    semantic_results = [
        doc for sim, doc in scored if sim >= 0.15
    ][:top_k]

    if semantic_results:
        return semantic_results

    # ----------------------------------
    # KEYWORD FALLBACK
    # ----------------------------------
    print("⚠ Semantic search failed → falling back to keyword search")

    keyword_results = keyword_fallback(normalized_query)
    return keyword_results[:top_k]
