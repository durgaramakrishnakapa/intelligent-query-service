from fastapi import FastAPI
from pydantic import BaseModel
from rag.rag_service import ask_gemini


app = FastAPI()


class QuestionRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_question(request: QuestionRequest):
    result = ask_gemini(request.question)

    return {
        "answer": result["answer"],
        "show_ids": result["sources"]
    }