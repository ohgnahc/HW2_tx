from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Text Summarization API",
    description="A simple API for text summarization using HuggingFace Transformers."
)

# Initialize the summarization model and tokenizer directly
logger.info("Loading summarization model 'sshleifer/distilbart-cnn-12-6'... This may take a moment.")
try:
    model_name = "sshleifer/distilbart-cnn-12-6"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise RuntimeError(f"Failed to load summarization model: {e}")


class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 130
    min_length: int = 30

class SummarizeResponse(BaseModel):
    summary: str


@app.get("/")
def read_root():
    return {"message": "Welcome to the Text Summarization API. Use POST /summarize to summarize text."}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    text_length = len(request.text.split())
    if text_length < request.min_length:
        raise HTTPException(
            status_code=400, 
            detail=f"Input text is too short. Please provide at least {request.min_length} words."
        )

    try:
        # Generate summary using model
        inputs = tokenizer(request.text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(
            inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_length=request.max_length, 
            min_length=request.min_length, 
            do_sample=False
        )
        summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return SummarizeResponse(summary=summary_text)
    except Exception as e:
        logger.error(f"Error during summarization: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the summary.")
