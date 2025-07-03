import streamlit as st
import requests
import fitz  # PyMuPDF
import os
import datetime
import pandas as pd

ALMM_URL = "https://mnre.gov.in/img/documents/uploads/file_f-1687167768046.pdf"  # Replace with the latest official URL
PDF_FILENAME = "latest_almm.pdf"

# Utility function to download PDF
def download_pdf(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

# Extract companies from ALMM PDF using PyMuPDF (fitz)
def extract_companies_from_pdf(filename):
    companies = []
    with fitz.open(filename) as doc:
        for page in doc:
            text = page.get_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    if "MW" in line and any(c.isalpha() for c in line):
                        companies.append(line.strip())
    return companies

# Load previous list
def load_previous_list():
    if os.path.exists("previous_list.txt"):
        with open("previous_list.txt", "r") as f:
            return f.read().splitlines()
    return []

# Save current list
def save_current_list(companies):
    with open("previous_list.txt", "w") as f:
        f.write("\n".join(companies))

# Main App
st.title("🔎 ALMM Tracker – MNRE Approved List Monitor")

if st.button("🔄 Download & Analyze Latest ALMM List"):
    with st.spinner("Downloading and processing PDF..."):
        download_pdf(ALMM_URL, PDF_FILENAME)
        current_companies = extract_companies_from_pdf(PDF_FILENAME)
        previous_companies = load_previous_list()
        added = [c for c in current_companies if c not in previous_companies]
        removed = [c for c in previous_companies if c not in current_companies]

        save_current_list(current_companies)

        st.success("ALMM List updated and analyzed.")

        # Display full list in searchable format
        st.subheader("📋 Full ALMM List (Latest)")
        df = pd.DataFrame(current_companies, columns=["Company Info"])
        search_term = st.text_input("🔍 Search company name")
        if search_term:
            df = df[df["Company Info"].str.contains(search_term, case=False)]
        st.dataframe(df, use_container_width=True)

        # Option to download as CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Table as CSV",
            data=csv,
            file_name='almm_filtered_companies.csv',
            mime='text/csv')

        # Display changes
        st.subheader("✅ New Additions")
        if added:
            st.write("\n".join(added))
        else:
            st.info("No new companies added.")

        st.subheader("❌ Removals")
        if removed:
            st.write("\n".join(removed))
        else:
            st.info("No companies removed.")

st.markdown("---")
st.caption("Built by ChatGPT – ALMM Monitor Tool with Search and Export")
