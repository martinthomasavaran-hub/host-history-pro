import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd

# Page Config
st.set_page_config(page_title="Domain Security Analyzer", layout="wide")
st.title("🛡️ Domain History & AI Analyst")

# Securely get API Keys from Streamlit Secrets
try:
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    SECURITYTRAILS_KEY = st.secrets["SECURITYTRAILS_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
except KeyError:
    st.error("Please add GEMINI_API_KEY and SECURITYTRAILS_API_KEY to your Streamlit Secrets.")
    st.stop()

# UI Layout
domain = st.text_input("Enter a domain to analyze (e.g., google.com):")

if st.button("Analyze Domain"):
    if domain:
        # 1. Fetch data from SecurityTrails
        url = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
        headers = {"apikey": SECURITYTRAILS_KEY}
        
        with st.spinner("Fetching domain history..."):
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                
                if records:
                    df = pd.DataFrame(records)
                    st.subheader("Historical DNS Records")
                    st.dataframe(df) # Display the professional data table

                    # 2. Analyze with Gemini
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Analyze these historical DNS records for {domain} and summarize major hosting changes or security risks: {str(records)[:2000]}"
                    
                    with st.spinner("Gemini is analyzing the data..."):
                        ai_response = model.generate_content(prompt)
                        st.subheader("AI Security Summary")
                        st.write(ai_response.text)
                else:
                    st.warning("No records found for this domain.")
            else:
                st.error(f"Error fetching data: {response.status_code}")
    else:
        st.warning("Please enter a domain name.")
