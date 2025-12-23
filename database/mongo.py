# database/mongo.py

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from pymongo import MongoClient
from settings import MONGO_URI, DB_NAME, WEBSITE_COLLECTION, USERS_COLLECTION


# ========================================================
# TIMEZONE → PAKISTAN (UTC+5)
# ========================================================
def now_pk() -> datetime:
  return datetime.utcnow() + timedelta(hours=5)


# ========================================================
# CLIENT / DB HELPERS
# ========================================================
_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
  global _client
  if _client is None:
    _client = MongoClient(MONGO_URI)
  return _client


def get_db():
  return get_client()[DB_NAME]


# ========================================================
# WEBSITE COLLECTION (VECTOR SEARCH)
# ========================================================
def get_website_col():
  return get_db()[WEBSITE_COLLECTION]


def clear_collection():
  get_website_col().delete_many({})


def insert_document(doc: Dict[str, Any]):
  get_website_col().insert_one(doc)


def fetch_all_pages() -> List[Dict[str, Any]]:
  return list(get_website_col().find({}))


# ========================================================
# USERS COLLECTION
# ========================================================
def get_users_col():
  return get_db()[USERS_COLLECTION]


def get_user_document(email: str) -> Dict[str, Any]:
  if not email:
    return {}
  return get_users_col().find_one({"email": email}) or {}


# ========================================================
# SAVE USER IF NEW / UPDATE
# ========================================================
def save_user_if_new(user_data: Dict[str, Any]):
  users = get_users_col()
  email = user_data.get("email")
  if not email:
    return None

  existing = users.find_one({"email": email})
  now = now_pk()

  if existing is None:
    doc = {
      "email": email,
      "name": user_data.get("name"),
      "phone": user_data.get("phone"),
      "created_at": now,
      "updated_at": now,
      "sessions": [],
      "analytics": [],
    }
    users.insert_one(doc)
    return doc

  users.update_one(
    {"email": email},
    {
      "$set": {
        "name": user_data.get("name", existing.get("name")),
        "phone": user_data.get("phone", existing.get("phone")),
        "updated_at": now,
      }
    },
  )
  return existing


# ========================================================
# SESSION MANAGEMENT
# ========================================================
def start_new_session(email: str, session_id: str):
  users = get_users_col()
  users.update_one(
    {"email": email},
    {
      "$push": {
        "sessions": {
          "session_id": session_id,
          "started_at": now_pk(),
          "ended_at": None,
          "messages": [],
        }
      },
      "$set": {"updated_at": now_pk()},
    },
    upsert=True,
  )


def end_session(email: str, session_id: str):
  users = get_users_col()
  users.update_one(
    {"email": email, "sessions.session_id": session_id},
    {
      "$set": {
        "sessions.$.ended_at": now_pk(),
        "updated_at": now_pk(),
      }
    },
  )


# ========================================================
# MESSAGE LOGGING
# ========================================================
def append_message(email: str, session_id: str, sender: str, msg: str):
  if not email or not msg:
    return

  users = get_users_col()
  users.update_one(
    {"email": email, "sessions.session_id": session_id},
    {
      "$push": {
        "sessions.$.messages": {
          "timestamp": now_pk(),
          "sender": sender,
          "message": msg,
        }
      },
      "$set": {"updated_at": now_pk()},
    },
    upsert=True,
  )


def get_session_messages(email: str, session_id: str) -> List[Dict[str, Any]]:
  users = get_users_col()
  doc = users.find_one({"email": email, "sessions.session_id": session_id},
                       {"sessions.$": 1})
  if doc and "sessions" in doc:
    return doc["sessions"][0].get("messages", [])
  return []


def get_last_session(email: str) -> Optional[Dict[str, Any]]:
  doc = get_users_col().find_one({"email": email})
  if not doc or "sessions" not in doc or not doc["sessions"]:
    return None
  return doc["sessions"][-1]


# ========================================================
# ANALYTICS STORAGE
# ========================================================
def save_analytics(email: str, session_id: str, analytics: Dict[str, Any]):
    users = get_users_col()

    # Check duplicate
    exists = users.find_one(
        {"email": email, "analytics.session_id": session_id},
        {"analytics.$": 1}
    )

    if exists:
        # Already exists → DO NOT save again
        return

    payload = {
        "timestamp": now_pk(),
        "session_id": session_id,
        "summary": analytics.get("summary"),
        "primary_service": analytics.get("primary_service"),
        "secondary_services": analytics.get("secondary_services", []),
        "interest_level": analytics.get("interest_level"),
        "sentiment_label": analytics.get("sentiment_label"),
        "sentiment_score": analytics.get("sentiment_score"),
    }

    users.update_one(
        {"email": email},
        {
            "$push": {"analytics": payload},
            "$set": {"updated_at": now_pk()}
        }
    )
