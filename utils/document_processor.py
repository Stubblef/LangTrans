import PyPDF2
from fastapi import UploadFile, HTTPException
import io

async def process_document(file: UploadFile) -> str:
    try:
        content = ""
        if file.filename.endswith('.txt'):
            content = (await file.read()).decode('utf-8', errors='ignore')
        
        elif file.filename.endswith('.pdf'):
            pdf_bytes = await file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                content += page.extract_text()
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only .txt and .pdf files are supported")
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="Empty document or unreadable content")
            
        return content
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
