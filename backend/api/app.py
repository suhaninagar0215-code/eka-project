import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel
from backend.router.query_router import route_question

app = FastAPI()


class QueryRequest(BaseModel):
    question: str
    user: str


@app.get("/")
def home():
    return {"message": "EKA Backend Running"}


@app.post("/ask")
def ask_question(request: QueryRequest):

    response = route_question(request.question)

    return response