from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database
from langchain_openai import ChatOpenAI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables from .env
load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=database.engine)


app = FastAPI()




# CORS for frontend - allow all origins in production, localhost in development
allowed_origins = ["*"]
 # In production, you should specify your actual frontend domain

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
    print("api_key",api_key)

    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not set. Please add it to your .env file.")

    try:
        # Call OpenAI
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
        response = llm.invoke(prompt.text)
        answer_text = response.content if hasattr(response, "content") else str(response)

        # Save to DB
        new_message = models.Message(
            prompt=prompt.text,
            response=answer_text,
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        return {"answer": answer_text}

    except Exception as e:
        error_str = str(e)
        debug = os.getenv("DEBUG") == "1"
        # Handle specific OpenAI quota error
        if "insufficient_quota" in error_str or "429" in error_str:
            detail = "OpenAI API quota exceeded. Please check your account or billing details."
            if debug:
                detail = f"{detail} | raw: {error_str}"
            raise HTTPException(status_code=402, detail=detail)
        elif "Invalid API key" in error_str or "incorrect API key" in error_str:
            detail = "Invalid OpenAI API key. Please check your .env file."
            if debug:
                detail = f"{detail} | raw: {error_str}"
            raise HTTPException(status_code=401, detail=detail)
        else:
            # Generic fallback for other errors
            detail = f"An unexpected error occurred: {error_str}" if debug else "An unexpected error occurred"
            raise HTTPException(status_code=500, detail=detail)

@app.get("/diagnostics/openai")
def diagnostics_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    has_key = bool(api_key)
    
    # Mask the key for security (show first 8 and last 4 chars)
    masked_key = None
    if api_key:
        if len(api_key) > 12:
            masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        else:
            masked_key = "***masked***"
    
    try:
        if not has_key:
            raise ValueError("OPENAI_API_KEY missing")
        # Minimal call: create client and inspect model attribute resolution by a no-op invoke
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
        _ = str(llm)
        return {
            "openaiKeyLoaded": has_key, 
            "apiKey": masked_key,
            "model": "gpt-4o-mini", 
            "status": "ok"
        }
    except Exception as e:
        debug = os.getenv("DEBUG") == "1"
        return {
            "openaiKeyLoaded": has_key,
            "apiKey": masked_key,
            "model": "gpt-4o-mini",
            "status": "error",
            "error": str(e) if debug else "error",
        }

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    messages = db.query(models.Message).order_by(models.Message.id.desc()).all()
    return [
        {"id": m.id, "prompt": m.prompt, "response": m.response} for m in messages
    ]

@app.get("/")
def root():
    return {"message": "AI Chatbot API is running!", "endpoints": ["/ask", "/history", "/health", "/diagnostics/openai"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=False)