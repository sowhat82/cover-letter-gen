# 📦 Install (only needed on first run)
# !pip install streamlit python-docx PyMuPDF requests

import streamlit as st
import fitz  # PyMuPDF
import requests
import re
from docx import Document
from docx.shared import Pt
from io import BytesIO

# 🛡️ OpenRouter API key (replace with your real key)
api_key = "sk-...your-key-here..."

# 🔗 API setup
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://yourdomain.com",
    "Content-Type": "application/json",
}
url = "https://openrouter.ai/api/v1/chat/completions"

# 📄 Extract text from uploaded PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc])

# 🧠 Generate filename
def generate_filename_from_jd(jd_text):
    prompt = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "Summarize the job description into a 3–5 word job title (no company name, no punctuation). Output only the job title."},
            {"role": "user", "content": jd_text}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=prompt)
        title = res.json()["choices"][0]["message"]["content"].strip()
        words = title.split()
        filtered = [w for w in words if w.lower() not in ['collaborative', 'analytical', 'driven', 'stakeholder', 'leader', 'techsavvy', 'datafocused']]
        return re.sub(r'[^A-Za-z0-9_]', '', "_".join(filtered[:4])) or "UnnamedRole"
    except:
        return "UnnamedRole"

# ✍️ Generate cover letter
def generate_cover_letter(resume_text, jd):
    prompt = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a career assistant. Write a tailored, confident, 3-paragraph cover letter based on the user's resume and job description. Sign off with 'Alvin Cheong'."},
            {"role": "user", "content": f"Here is my resume:\n{resume_text}\n\nHere is the job description:\n{jd}"}
        ]
    }
    res = requests.post(url, headers=headers, json=prompt)
    return res.json()["choices"][0]["message"]["content"]

# 📄 Save letter to Word
def generate_word_doc(letter_text):
    buffer = BytesIO()
    doc = Document()
    for para in letter_text.strip().split("\n\n"):
        p = doc.add_paragraph(para.strip())
        p.style.font.name = 'Calibri'
        p.style.font.size = Pt(11)
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# 🖼️ Streamlit UI
st.title("GPT Cover Letter Generator")

resume_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
job_input = st.text_area("Paste one or more job descriptions, separated by ===")

if st.button("Generate Cover Letters"):
    if resume_file is None or not job_input.strip():
        st.warning("Please upload a resume and provide job descriptions.")
    else:
        st.info("Generating cover letters...")
        resume_text = extract_text_from_pdf(resume_file)
        job_descriptions = [j.strip() for j in job_input.split("===") if j.strip()]
        
        for i, jd in enumerate(job_descriptions, 1):
            job_slug = generate_filename_from_jd(jd)
            filename = f"CoverLetter_{job_slug}_{i}.docx"
            letter = generate_cover_letter(resume_text, jd)
            word_bytes = generate_word_doc(letter)

            st.download_button(
                label=f"Download {filename}",
                data=word_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
