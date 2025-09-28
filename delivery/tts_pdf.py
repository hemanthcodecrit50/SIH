from gtts import gTTS
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def generate_tts_pdf(farmer_id, advisory):
    # TTS
    tts = gTTS(advisory, lang='en')
    tts_path = f"tts_{farmer_id}.mp3"
    tts.save(tts_path)
    print(f"TTS audio generated for {farmer_id}: {tts_path}")

    # PDF
    pdf_path = f"advisory_{farmer_id}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    c.drawString(72, height - 72, f"Advisory for Farmer {farmer_id}:")
    text_object = c.beginText(72, height - 100)
    for line in advisory.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    c.save()
    print(f"PDF generated for {farmer_id}: {pdf_path}")