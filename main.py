from fastapi import FastAPI, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import Request
import uvicorn
from utils.document_processor import process_document
from utils.llm_handler import translate_and_summarize
import os

app = FastAPI()

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SUPPORTED_LANGUAGES = ["en", "zh", "es", "fr", "de", "ja", "ko"]

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "languages": SUPPORTED_LANGUAGES}
    )

@app.post("/translate")
async def translate_document(
    file: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    content = await process_document(file)
    result = await translate_and_summarize(content, source_lang, target_lang)
    return {"summary": result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
