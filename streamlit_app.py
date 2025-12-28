import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd

st.set_page_config(page_title="Host History Pro", layout="wide")
st.title("🛡️ Host History Pro: AI Domain Analyst")

# Securely load API Keys from Streamlit Secrets
try:
    GENAI_KEY = st.secrets["GEMINI_API_KEY"]
    SECURITYTRAILS_KEY = st.secrets["SECURITYTRAILS_API_KEY"]
    genai.configure(api_key=GENAI_KEY)
except KeyError:
    st.error("Missing API Keys! Please add them to 'Secrets' in your Streamlit settings.")
    st.stop()

domain = st.text_input("Enter a domain to analyze (e.g., example.com):")

if st.button("Run AI Analysis"):
    if domain:
        # 1. Fetch DNS history from SecurityTrails
        url = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
        headers = {"APIKEY": SECURITYTRAILS_KEY, "accept": "application/json"}
        
        with st.spinner("Fetching domain history..."):
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                
                if records:
                    df = pd.DataFrame(records)
                    st.subheader("📊 Historical DNS Records")
                    st.dataframe(df)

                    # 2. Analyze results with Gemini
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Analyze these historical DNS records for {domain} and summarize major hosting changes or potential security risks: {str(records)[:2000]}"
                    
                    with st.spinner("Gemini is analyzing the data..."):
                        ai_response = model.generate_content(prompt)
                        st.subheader("🤖 AI Security Summary")
                        st.write(ai_response.text)
                else:
                    st.warning("No historical records found for this domain.")
            else:
                st.error(f"SecurityTrails Error: {response.status_code}")
    else:
        st.warning("Please enter a domain name.")
