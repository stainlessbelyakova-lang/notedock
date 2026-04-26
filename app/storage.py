import json
import uuid
from datetime import datetime
from app.config import NOTES_FILE, DATA_DIR


def ensure_storage():
    DATA_DIR.mkdir(exist_ok=True)

    if not NOTES_FILE.exists():
        NOTES_FILE.write_text("[]", encoding="utf-8")


def load_notes():
    ensure_storage()

    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_notes(notes):
    ensure_storage()

    with open(NOTES_FILE, "w", encoding="utf-8") as file:
        json.dump(notes, file, indent=4, ensure_ascii=False)


def create_note():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return {
        "id": str(uuid.uuid4()),
        "title": "New Note",
        "content": "",
        "created_at": now,
        "updated_at": now,
        "pinned": False
    }


def update_time(note):
    note["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")