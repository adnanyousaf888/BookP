# server.py  (BookProo backend)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

from chatbot.chatbot import answer_from_database
from chatbot.analytics import analyze_new_messages

from database.mongo import (
    save_user_if_new,
    start_new_session,
    end_session,
    append_message,
    get_session_messages,
    get_user_document,
    save_analytics,
)

# ======================================================
# APP
# ======================================================
app = FastAPI()

# ======================================================
# CORS (safe for now, tighten later)
# ======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# SERVE FRONTEND (STATIC FILES)
# ======================================================
# This exposes:
# /frontend/book-proo.css
# /frontend/book-proo.js
app.mount(
    "/frontend",
    StaticFiles(directory="frontend"),
    name="frontend"
)

# Main UI
@app.get("/")
def serve_home():
    return FileResponse("frontend/book-proo.html")

# ======================================================
# REQUEST MODELS
# ======================================================
class StartChat(BaseModel):
    name: str
    email: str
    phone: str


class ChatMessage(BaseModel):
    email: str
    session_id: str
    message: str


class EndChat(BaseModel):
    email: str
    session_id: str

# ======================================================
# START CHAT
# ======================================================
@app.post("/start_chat")
async def start_chat(req: StartChat):

    save_user_if_new({
        "name": req.name,
        "email": req.email,
        "phone": req.phone,
    })

    session_id = uuid.uuid4().hex
    start_new_session(req.email, session_id)

    welcome = (
        f"Hi {req.name}! I’m BookProo, your assistant from The Book Promoters. "
        f"How can I help you today?"
    )

    append_message(req.email, session_id, "bot", welcome)

    return {
        "session_id": session_id,
        "welcome": welcome,
    }

# ======================================================
# CHAT MESSAGE
# ======================================================
@app.post("/chat_message")
async def chat_message(req: ChatMessage):

    try:
        append_message(req.email, req.session_id, "user", req.message)

        raw_history = get_session_messages(req.email, req.session_id)

        result = answer_from_database(
            email=req.email,
            query=req.message,
            history_docs=raw_history,
        )

        reply = result.get("response", "Sorry, something went wrong.")

        append_message(req.email, req.session_id, "bot", reply)

        return {"reply": reply}

    except Exception as e:
        print("❌ Error in /chat_message:", e)
        return {"reply": "Sorry, something went wrong on my side."}

# ======================================================
# END CHAT (ANALYTICS ONCE)
# ======================================================
@app.post("/end_chat")
async def end_chat(req: EndChat):

    try:
        user_doc = get_user_document(req.email)
        if not user_doc:
            return {"status": "user_not_found"}

        existing = [
            a for a in user_doc.get("analytics", [])
            if a.get("session_id") == req.session_id
        ]
        if existing:
            return {"status": "already_processed"}

        end_session(req.email, req.session_id)

        history = get_session_messages(req.email, req.session_id)
        if not history:
            return {"status": "no_messages"}

        analytics = analyze_new_messages(history)
        save_analytics(req.email, req.session_id, analytics)

        return {"status": "ok"}

    except Exception as e:
        print("❌ Error in /end_chat:", e)
        return {"status": "error"}
