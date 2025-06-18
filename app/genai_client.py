import google.generativeai as genai
from app.config import GOOGLE_API_KEY, GENAI_MODEL

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(GENAI_MODEL)

def generate_answer_from_prompt(prompt):
    response = model.generate_content(prompt)
    return response.text
