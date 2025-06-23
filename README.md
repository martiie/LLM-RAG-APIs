---
title: LLM RAG API
colorFrom: indigo
colorTo: pink
sdk: docker
pinned: false
---

# LLM RAG API with Gemini + FAISS
Simple Retrieval-Augmented Generation (RAG) API built with FastAPI, SentenceTransformer, FAISS, and Gemini via Google Generative AI.

# Document QA API

ระบบ API สำหรับอัปโหลดเอกสารหลายประเภท (.txt, .pdf, .xlsx, .docx) และถามตอบข้อมูลจากเอกสารเหล่านั้น

---

## ฟีเจอร์หลัก

- อัปโหลดไฟล์เอกสารและแปลงเป็นข้อความเก็บในฐานข้อมูล JSON
  
- สร้างดัชนี FAISS เพื่อค้นหาข้อมูลบริบทอย่างรวดเร็ว
  
- ถามคำถามโดยใช้เนื้อหาจากเอกสารที่อัปโหลด
  
- เก็บประวัติคำถาม 5 ครั้งล่าสุด เพื่อช่วยให้ตอบคำถามที่ต่อเนื่องได้ดียิ่งขึ้น

---

## การติดตั้ง

1. Clone โปรเจกต์นี้

```bash
git clone <repository-url>
cd <project-folder>
```

2. ติดตั้ง dependencies
```bash
pip install -r requirements.txt
```

3.รันเซิร์ฟเวอร์ FastAPI
```bash
uvicorn app.main:app --reload
```

# API Endpoints และวิธีใช้
1. อัปโหลดไฟล์ (Upload file)
URL: /upload-file

Method: POST

รูปแบบข้อมูล: multipart/form-data

Key: file

ไฟล์ที่รองรับ: .txt, .pdf, .xlsx, .xls, .docx

## ตัวอย่าง curl
```bash
curl -X POST "http://localhost:8000/upload-file" -F "file=@path/to/yourfile.pdf"
```

## ตัวอย่าง Postman
Method: POST

URL: http://localhost:8000/upload-file

Body: เลือก form-data

ใส่ key ชื่อ file แล้วเลือกไฟล์จากเครื่อง

## Response (ตัวอย่าง)
```json
{
  "status": "uploaded",
  "title": "yourfile.pdf",
  "count": 3
}
```

หมายเหตุ:
-หากชื่อไฟล์ซ้ำกับในระบบ จะได้ response error 400 พร้อมข้อความ "หัวข้อนี้มีอยู่แล้ว"

-ไฟล์จะถูกแปลงเป็นข้อความและเก็บใน docs.json

-ดัชนี FAISS จะถูกอัปเดตใหม่ทุกครั้งหลังอัปโหลด

# 2. ถามคำถาม (Ask question)
-URL: /ask

-Method: POST

-รูปแบบข้อมูล: JSON

## Request body
```json
{
  "query": "คำถามของคุณ"
}
```
## ตัวอย่าง curl
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "ข้อมูลเกี่ยวกับการตลาดมีอะไรบ้าง?"}'

```
## ตัวอย่าง Postman
-Method: POST

-URL: http://localhost:8000/ask

-Body: raw JSON

```json
{
"query": "ข้อมูลเกี่ยวกับการตลาดมีอะไรบ้าง?"
}
```
## Response (ตัวอย่าง)
```json
{
  "answer": "ข้อมูลเกี่ยวกับการตลาดที่พบในเอกสารคือ..."
}
```
# การทำงานภายในระบบ

1. เอกสารที่อัปโหลดจะถูกแปลงเป็นข้อความ แล้วเก็บในไฟล์ docs.json
   
2.ระบบจะสร้างหรืออัปเดตดัชนี FAISS เพื่อใช้ดึงบริบทที่เกี่ยวข้องจากเอกสารเหล่านี้

3.เมื่อมีคำถาม ระบบจะดึงบริบทจากดัชนี และสร้าง prompt พร้อมคำถาม ส่งให้โมเดลภายนอก (หรือฟังก์ชัน generate_answer_from_prompt)

4.ระบบเก็บประวัติคำถามล่าสุด 5 ครั้งเพื่อใช้ช่วยให้การตอบคำถามต่อเนื่องแม่นยำ
