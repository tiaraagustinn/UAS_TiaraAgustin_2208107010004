import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai import types

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# inisialisasi Gemini client dan konfigurasi
MODEL = "gemini-2.0-flash"
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(title="Intelligent Email Writer API")

# schema request
class EmailRequest(BaseModel):
    category: str
    recipient: str
    subject: str
    tone: str
    language: str
    urgency_level: Optional[str] = "Biasa"
    points: List[str]
    example_email: Optional[str] = None

# fungsi untuk membentuk prompt teks dari data input pengguna
def build_prompt(body: EmailRequest) -> str:
    """
    menghasilkan prompt teks berdasarkan data yang diberikan oleh pengguna.

    fungsi ini membangun struktur prompt yang berisi:
    - Bahasa dan nada email.
    - Informasi penerima dan subjek.
    - Kategori dan tingkat urgensi.
    - Poin-poin isi email yang harus disertakan.
    - (Opsional) Contoh email sebelumnya sebagai referensi.

    prompt ini akan digunakan sebagai input untuk LLM seperti Gemini.
    """
    lines = [
        f"Tolong buatkan email dalam {body.language.lower()} yang {body.tone.lower()}",
        f"kepada {body.recipient}.",
        f"Subjek: {body.subject}.",
        f"Kategori email: {body.category}.",
        f"Tingkat urgensi: {body.urgency_level}.",
        "",
        "Isi email harus mencakup poin-poin berikut:",
    ]
    for point in body.points:
        lines.append(f"- {point}")
    if body.example_email:
        lines += ["", "Contoh email sebelumnya:", body.example_email]
    lines.append("")
    lines.append("Buat email yang profesional, jelas, dan padat.")
    return "\n".join(lines)

# endpoint untuk generate email   ### UNTUK KODE NYA BISA DIUBAH SESUAI KEBUTUHAN ###
@app.post("/generate/")
async def generate_email(req: EmailRequest):
    # ubah request menjadi prompt teks dengan fungsi build_prompt
    prompt = build_prompt(req)

    try:
        # TODO: kirim prompt ke Gemini API
        model = genai.GenerativeModel(model_name=MODEL)
        response = model.generate_content(
                contents=prompt,
                generation_config=types.GenerationConfig(
                    max_output_tokens=1000,  # Adjust as needed
                    temperature=0.7,         # Adjust for creativity/formality
                )
            )

        # TODO: ambil hasil teks dari response dan simpan ke variabel
        generated = response.text

        # TODO: validasi hasil respon
        if not generated or generated.strip() == "":
                raise HTTPException(status_code=500, detail="Tidak ada hasil yang dihasilkan oleh Gemini API")

        return {"generated_email": generated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghasilkan email: {str(e)}")