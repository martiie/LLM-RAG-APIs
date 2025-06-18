from sentence_transformers import SentenceTransformer
# from app.config import EMBED_MODEL_NAME
import os
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['HF_HOME'] = '/tmp/huggingface'
os.environ['SENTENCE_TRANSFORMERS_HOME'] = '/tmp/sentence_transformers'

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts):
    return embed_model.encode(texts, convert_to_numpy=True)

def embed_text(text):
    return embed_model.encode([text], convert_to_numpy=True)[0]
