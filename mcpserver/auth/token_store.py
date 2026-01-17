import uuid
import json
import os
from typing import Dict
from pathlib import Path

# Persistent storage file
STORAGE_FILE = Path.home() / ".oxyloans_sessions.json"

def _load_storage():
    if STORAGE_FILE.exists():
        return json.loads(STORAGE_FILE.read_text())
    return {"sessions": {}, "tokens": {}}

def _save_storage(data):
    STORAGE_FILE.write_text(json.dumps(data, indent=2))

SESSION_STORE: Dict[str, dict] = {}
USER_TOKENS: Dict[str, str] = {}

# Load on startup
_data = _load_storage()
SESSION_STORE.update(_data.get("sessions", {}))
USER_TOKENS.update(_data.get("tokens", {}))


def create_session(user_id: str, access_token: str) -> str:
    session_id = str(uuid.uuid4())

    SESSION_STORE[session_id] = {
        "user_id": user_id,
    }

    USER_TOKENS[user_id] = access_token
    
    # Persist to disk
    _save_storage({"sessions": SESSION_STORE, "tokens": USER_TOKENS})
    
    return session_id


def get_user_id_by_session(session_id: str) -> str | None:
    session = SESSION_STORE.get(session_id)
    if not session:
        return None
    return session.get("user_id")


def get_token_by_session(session_id: str) -> str | None:
    session = SESSION_STORE.get(session_id)
    if not session:
        return None
    return USER_TOKENS.get(session["user_id"])


def remove_session(session_id: str):
    session = SESSION_STORE.pop(session_id, None)
    if session:
        USER_TOKENS.pop(session["user_id"], None)
        _save_storage({"sessions": SESSION_STORE, "tokens": USER_TOKENS})
