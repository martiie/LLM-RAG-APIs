from sentence_transformers import SentenceTransformer
from app.config import EMBED_MODEL_NAME

embed_model = SentenceTransformer(EMBED_MODEL_NAME)

def embed_texts(texts):
    return embed_model.encode(texts, convert_to_numpy=True)

def embed_text(text):
    return embed_model.encode([text], convert_to_numpy=True)[0]
