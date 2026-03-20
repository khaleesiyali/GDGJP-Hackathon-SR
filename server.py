#  uv add fastapi uvicorn livekit-api
# npm install @livekit/components-react @livekit/components-styles livekit-client
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from livekit.api import AccessToken, VideoGrants
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from pdf_generate import smart_fill_pdf
import tempfile

load_dotenv(".env.local")
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_token")
def get_livekit_token(room_name: str, participant_name: str):
    """
    Send get request to my local server:
    http://localhost:8000/get_token?room_name=test-room&participant_name=user1
    """
    # Grant API token for frontteam and Users..?
    grant = VideoGrants(room_join=True, room=room_name)
    
    access_token = AccessToken(
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET")
    )
    access_token.with_identity(participant_name)
    access_token.with_grants(grant)

    # return
    return {"token": access_token.to_jwt()}

@app.post("/generate-pdf")
async def generate_pdf(request: Request):
    """
    Generate a filled PDF from form data
    POST body should be JSON with form field values
    """
    try:
        from reportlab.pdfgen import canvas as rl_canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from pypdf import PdfReader, PdfWriter
        import tempfile
        import os
        
        form_data = await request.json()
        
        # Register the font
        font_path = os.path.join(os.path.dirname(__file__), "Font", "NotoSansJP-Medium.ttf")
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('NotoSans', font_path))
        
        # Load the blank PDF template
        template_path = Path(__file__).parent / "blank_form.pdf"
        
        # Create a temporary file for the transparent text layer
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            transparent_text_path = tmp_file.name
        
        # Create a canvas for the transparent text
        c = rl_canvas.Canvas(transparent_text_path)
        c.setFont('NotoSans', 10) if os.path.exists(font_path) else c.setFont('Helvetica', 10)
        
        # Load the mapping JSON
        mapping_path = Path(__file__).parent / "心身障碍者福祉手当認定申請書Mapping.json"
        if mapping_path.exists():
            with open(mapping_path, 'r', encoding='utf-8') as f:
                mapping_data = json.load(f)
                mapping = mapping_data.get("mapping", {})
            
            # Use smart_fill_pdf to fill the canvas
            smart_fill_pdf(form_data, mapping, c)
        
        c.save()
        
        # Merge the transparent text layer with the blank form
        pdf_reader_blank = PdfReader(str(template_path))
        pdf_reader_text = PdfReader(transparent_text_path)
        pdf_writer = PdfWriter()
        
        for i in range(len(pdf_reader_blank.pages)):
            page = pdf_reader_blank.pages[i]
            if i < len(pdf_reader_text.pages):
                page.merge_page(pdf_reader_text.pages[i])
            pdf_writer.add_page(page)
        
        # Write the final PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as output_file:
            output_path = output_file.name
            pdf_writer.write(output_file)
        
        # Clean up temporary file
        try:
            os.unlink(transparent_text_path)
        except:
            pass
        
        # Return the PDF file
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=f"form_{form_data.get('applicant_name', 'unknown')}.pdf"
        )
    
    except Exception as e:
        import traceback
        print(f"Error generating PDF: {traceback.format_exc()}")
        return {"error": str(e)}, 500

# uv run uvicorn server:app --reload

#I Think you need to use Livekit React SDK to coonect to AI Agent?
#After the token is fetched, we should use LiveKitRoom to wrap our voice interface?? I still need to look into that.
