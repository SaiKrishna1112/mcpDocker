import uuid
from typing import Dict

SESSION_STORE: Dict[str, dict] = {}
USER_TOKENS: Dict[str, str] = {}


def create_session(user_id: str, access_token: str) -> str:
    session_id = str(uuid.uuid4())

    SESSION_STORE[session_id] = {
        "user_id": user_id,
    }

    USER_TOKENS[user_id] = access_token
    return session_id


def get_token_by_session(session_id: str) -> str | None:
    session = SESSION_STORE.get(session_id)
    if not session:
        return None
    return USER_TOKENS.get(session["user_id"])


def remove_session(session_id: str):
    session = SESSION_STORE.pop(session_id, None)
    if session:
        USER_TOKENS.pop(session["user_id"], None)
