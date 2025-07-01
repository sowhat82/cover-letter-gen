
import streamlit as st
import fitz  # PyMuPDF
import requests
import zipfile
import io
from docx import Document
from docx.shared import Pt
import os
import re

# --- CONFIG ---
st.set_page_config(page_title="AI Cover Letter Generator", layout="centered")
st.title("📄 GPT-Powered Cover Letter Generator")

# 🔑 Manually enter your OpenRouter API key here
api_key = "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"  # <-- replace this with your actual API key

if not api_key or api_key.strip() == "":
    st.error("Please enter your OpenRouter API key in the script.")
    st.stop()


headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://yourdomain.com",
    "Content-Type": "application/json",
}
url = "https://openrouter.ai/api/v1/chat/completions"

# --- Uploads ---
resume_file = st.file_uploader("📎 Upload your resume (PDF)", type=["pdf"])
jd_files = st.file_uploader("📄 Upload one or more job descriptions (TXT)", type=["txt"], accept_multiple_files=True)

# --- Helper Functions ---
def extract_text_from_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

def generate_filename_from_jd(jd_text):
    naming_prompt = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "Summarize the job description into a 3–5 word job title (no company name, no punctuation). Output only the job title."
            },
            {
                "role": "user",
                "content": jd_text
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=naming_prompt)
        title = response.json()["choices"][0]["message"]["content"].strip()
        words = title.split()
        filtered = [w for w in words if w.lower() not in ['collaborative', 'analytical', 'driven', 'stakeholder', 'leader']]
        short_name = "_".join(filtered[:4])
        return re.sub(r'[^A-Za-z0-9_]', '', short_name) or "UnnamedRole"
    except:
        return "UnnamedRole"

def generate_cover_letter(resume, jd):
    prompt = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a career assistant. Write a tailored, confident, 3-paragraph cover letter "
                    "based on the user's resume and job description. Sign off with 'Alvin Cheong'."
                )
            },
            {
                "role": "user",
                "content": f"""Here is my resume:
{resume}

Here is the job description:
{jd}"""
            }
        ]
    }

    response = requests.post(url, headers=headers, json=prompt)
    return response.json()["choices"][0]["message"]["content"]


# --- Main Logic ---
if st.button("✍️ Generate Cover Letters"):
    if not resume_file or not jd_files:
        st.warning("Please upload both your resume and job descriptions.")
        st.stop()

    resume_text = extract_text_from_pdf(resume_file)

    output_zip = io.BytesIO()
    with zipfile.ZipFile(output_zip, "w") as zipf:
        for i, jd_file in enumerate(jd_files, 1):
            jd_text = jd_file.read().decode("utf-8")
            slug = generate_filename_from_jd(jd_text)
            docx_filename = f"CoverLetter_{slug}_{i}.docx"

            cover_letter = generate_cover_letter(resume_text, jd_text)

            doc_stream = io.BytesIO()
            doc = Document()
            for para in cover_letter.strip().split("\n\n"):
                p = doc.add_paragraph(para.strip())
                p.style.font.name = 'Calibri'
                p.style.font.size = Pt(11)
            doc.save(doc_stream)
            doc_stream.seek(0)

            zipf.writestr(docx_filename, doc_stream.read())

    st.success("✅ Cover letters generated!")
    st.download_button("📥 Download All Cover Letters (ZIP)", data=output_zip.getvalue(), file_name="CoverLetters.zip", mime="application/zip")
