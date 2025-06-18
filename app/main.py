from fastapi import FastAPI, HTTPException, UploadFile, File
from io import BytesIO
import PyPDF2
import pandas as pd
import docx

from app.config import GOOGLE_API_KEY
from app.models import DocItem, TitleItem
from app.doc_manager import load_docs, save_docs, find_doc_by_title
from app.embedder import embed_texts, embed_text
from app.faiss_indexer import FaissIndexer
from app.genai_client import generate_answer_from_prompt

app = FastAPI()

documents = load_docs()

faiss_indexer = None
def rebuild_faiss():
    global faiss_indexer
    if not documents:
        faiss_indexer = None
        return
    vectors = embed_texts([d["content"] for d in documents])
    dim = vectors.shape[1]
    faiss_indexer = FaissIndexer(dim)
    faiss_indexer.build_index(vectors)

rebuild_faiss()

def retrieve_context(query, top_k=3):
    if not faiss_indexer or not documents:
        return []
    query_vec = embed_text(query).reshape(1, -1)
    _, indices = faiss_indexer.search(query_vec, top_k)
    return [documents[i]["content"] for i in indices[0]]

# เก็บประวัติคำถาม-คำตอบล่าสุด 5 คู่
history = []

def generate_answer(query):
    global history

    # สร้างข้อความประวัติเป็น string
    history_text = ""
    for i, (q, a) in enumerate(history[-5:], 1):
        history_text += f"คำถาม {i}: {q}\nคำตอบ {i}: {a}\n"

    context = retrieve_context(query)
        
    if not context:
        prompt = f"""
            คุณเป็นผู้ช่วยที่เชี่ยวชาญ ชื่อ"นิตยา"(ผู้หญิง) กรุณาตอบคำถามโดยอิงจากประวัติคำถาม-คำตอบก่อนหน้า*ถ้า*เกี่ยวข้องกับคำถามล่าสุด
            ประวัติคำถาม-คำตอบ:
            {history_text}
            
            คำถามใหม่: {query}
            คำตอบ:
            """
        return generate_answer_from_prompt(prompt).strip()

    context_text = "\n".join(context)

    prompt = f"""
            คุณเป็นผู้ช่วยที่เชี่ยวชาญ ชื่อ"นิตยา"(ผู้หญิง) กรุณาตอบคำถามโดยอิงจากเนื้อหาต่อไปนี้และประวัติคำถาม-คำตอบก่อนหน้า*ถ้า*เกี่ยวข้องกับคำถามล่าสุด
            
            ประวัติคำถาม-คำตอบ:
            {history_text}
            
            เนื้อหาประกอบ:
            {context_text}
            
            คำถามใหม่: {query}
            คำตอบ:
            """

    answer = generate_answer_from_prompt(prompt).strip()
    if not answer:
        return "ไม่สามารถให้คำตอบได้ในขณะนี้"

    # บันทึกคำถาม-คำตอบล่าสุดลง history
    history.append((query, answer))

    return answer

@app.post("/")
def clear_history():
    global history
    history = [] 
    return {"message": "ล้างประวัติคำถามเรียบร้อยแล้ว"}

@app.get("/chat")
def chat(query: str):
    try:
        answer = generate_answer(query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/titles")
def get_titles():
    return {"titles": [doc["title"] for doc in documents]}

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    if any(d["title"] == filename for d in documents):
        raise HTTPException(status_code=400, detail="หัวข้อนี้มีอยู่แล้ว")

    if filename.endswith(".txt"):
        content = (await file.read()).decode("utf-8")

    elif filename.endswith(".pdf"):
        pdf_bytes = await file.read()
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        content = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        excel_bytes = await file.read()
        df = pd.read_excel(BytesIO(excel_bytes))
        content = df.to_csv(index=False)

    elif filename.endswith(".docx"):
        doc_bytes = await file.read()
        doc = docx.Document(BytesIO(doc_bytes))
        content = "\n".join(p.text for p in doc.paragraphs)

    else:
        raise HTTPException(status_code=400, detail="ไฟล์ประเภทนี้ยังไม่รองรับ")

    documents.append({"title": filename, "content": content})
    save_docs(documents)
    rebuild_faiss()

    return {"status": "uploaded", "title": filename, "count": len(documents)}

@app.put("/update")
async def update_text(doc: DocItem):
    idx, _ = find_doc_by_title(documents, doc.title)
    if idx == -1:
        raise HTTPException(status_code=404, detail="ไม่พบหัวข้อที่ต้องการแก้ไข")

    documents[idx]["content"] = doc.content
    save_docs(documents)
    rebuild_faiss()
    return {"status": "updated", "title": doc.title}

@app.delete("/delete-by-title")
async def delete_by_title(item: TitleItem):
    global documents
    new_docs = [d for d in documents if d["title"] != item.title]
    if len(new_docs) == len(documents):
        raise HTTPException(status_code=404, detail="ไม่พบหัวข้อ")
    documents = new_docs
    save_docs(documents)
    rebuild_faiss()
    return {"status": "deleted", "remaining": len(documents)}
