from sentence_transformers import SentenceTransformer
from app.config import EMBED_MODEL_NAME
import os
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'

embed_model = SentenceTransformer(EMBED_MODEL_NAME)

def embed_texts(texts):
    return embed_model.encode(texts, convert_to_numpy=True)

def embed_text(text):
    return embed_model.encode([text], convert_to_numpy=True)[0]
