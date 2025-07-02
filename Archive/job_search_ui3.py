import streamlit as st

st.set_page_config(page_title="GPT Job Search Assistant", layout="centered")

st.title("🤖 GPT Job Search Assistant")

st.write("Upload your resume and paste job descriptions below to generate tailored cover letters.")

# Upload resume
resume_file = st.file_uploader("Upload your resume (.docx)", type=["docx"])

# Paste job descriptions
job_descriptions = st.text_area("Paste job descriptions here (one after another):", height=300)

# Submit button
if st.button("Generate Cover Letters"):
    if resume_file is None or not job_descriptions.strip():
        st.warning("Please upload your resume and paste job descriptions.")
    else:
        st.success("✅ Demo working! Replace this with actual GPT output.")
