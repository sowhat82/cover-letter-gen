import streamlit as st
from docx import Document
import requests

st.set_page_config(page_title="GPT Job Search Assistant", layout="wide")
st.title("🎯 GPT-Powered Job Search Assistant")

st.markdown("Upload your **resume** and paste a **job description** to generate a tailored cover letter.")

resume_file = st.file_uploader("Upload Resume (Word format)", type=["docx"])
job_description = st.text_area("Paste Job Description")

if st.button("Generate Cover Letter"):
    if resume_file is None or not job_description.strip():
        st.warning("Please upload a resume and paste a job description.")
    else:
        # Read resume content
        resume_doc = Document(resume_file)
        resume_text = "\n".join([para.text for para in resume_doc.paragraphs])

        # Call GPT (example uses OpenRouter-style payload)
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a professional career coach."},
                {"role": "user", "content": f"Resume:\n{resume_text}\n\nJob Description:\n{job_description}\n\nWrite a tailored, professional cover letter."}
            ]
        }

        headers = {
            "Authorization": "Bearer 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"
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            st.success("✅ Cover letter generated!")

            st.download_button(
                label="📄 Download Cover Letter (Word)",
                data=content.encode('utf-8'),
                file_name="cover_letter.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            st.text_area("Preview:", value=content, height=300)
        else:
            st.error("❌ Error calling the API.")
