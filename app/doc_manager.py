import json
import os
from app.config import DOCS_JSON

def load_docs():
    if os.path.exists(DOCS_JSON):
        with open(DOCS_JSON, encoding="utf-8") as f:
            return json.load(f)
    return []

def save_docs(docs):
    with open(DOCS_JSON, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

def find_doc_by_title(docs, title):
    for i, d in enumerate(docs):
        if d["title"] == title:
            return i, d
    return -1, None
