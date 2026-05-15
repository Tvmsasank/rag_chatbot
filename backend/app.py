from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from query import ask

app = FastAPI()

# ---- CORS FIX ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "RAG Chatbot API Running"}

@app.get("/chat")
def chat(q: str):
    answer, _ = ask(q)
    return {"answer": answer}