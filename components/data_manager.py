import json
import os
from datetime import datetime

DATA_FILE = "user_data.json"

def _load_data():
    if not os.path.exists(DATA_FILE):
        return {"history": [], "bookmarks": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"history": [], "bookmarks": []}

def _save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def add_to_history(url, title):
    if url.startswith("file://") or url.startswith("chrome://"):
        return # Don't log local files if you prefer, but let's log everything except homepage for now
    
    data = _load_data()
    # Avoid duplicate consecutive entries
    if data["history"] and data["history"][-1]["url"] == url:
        return

    entry = {
        "url": url,
        "title": title,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["history"].append(entry)
    _save_data(data)

def get_history():
    return _load_data().get("history", [])

def clear_history():
    data = _load_data()
    data["history"] = []
    _save_data(data)

def get_bookmarks():
    return _load_data().get("bookmarks", [])

def add_bookmark(url, title):
    data = _load_data()
    # Check if already bookmarked
    for b in data["bookmarks"]:
        if b["url"] == url:
            return
    data["bookmarks"].append({"url": url, "title": title})
    _save_data(data)

def remove_bookmark(url):
    data = _load_data()
    data["bookmarks"] = [b for b in data["bookmarks"] if b["url"] != url]
    _save_data(data)

def is_bookmarked(url):
    data = _load_data()
    for b in data["bookmarks"]:
        if b["url"] == url:
            return True
    return False

def get_settings():
    data = _load_data()
    return data.get("settings", {"search_engine": "DuckDuckGo"})

def save_settings(settings):
    data = _load_data()
    data["settings"] = settings
    _save_data(data)
