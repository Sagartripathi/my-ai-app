from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Create tablesmy-ai-app
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# CORS for frontend (React dev server on Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request model
class Prompt(BaseModel):
    text: str

@app.post("/ask")
async def ask_ai(prompt: Prompt, db: Session = Depends(get_db)):
    # Load API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OpenAI API key not set. Please add it to your .env file."}

    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
    response = llm.invoke(prompt.text)

    # Save to DB
    new_message = models.Message(
        prompt=prompt.text,
        response=response.content if hasattr(response, "content") else str(response),
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"answer": response.content}
