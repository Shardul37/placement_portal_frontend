import streamlit as st
import pandas as pd
import requests
import os
from supabase import create_client
from dotenv import load_dotenv
import math

# Load environment variables
load_dotenv(dotenv_path="../.env")

# Configuration - Adjust this value to experiment with AI response height
AI_RESPONSE_HEIGHT = 540  # Change this value to adjust AI chat window height

st.set_page_config(
    page_title="PlacementAI Portal",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.cache_data(ttl=600)
def load_supabase_data():
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            st.error("Supabase credentials not found in environment variables.")
            return pd.DataFrame()
        
        supabase_client = create_client(supabase_url, supabase_key)
        response = supabase_client.from_("placements").select("phase, company_name, job_role, gross_salary_btech, ctc_btech, currency, job_requirements, job_info, company_info, additional_details, job_location").execute()
        
        if not response.data:
            st.error("No data found in the 'placements' table.")
            return pd.DataFrame()
            
        df = pd.DataFrame(response.data)
        # Remove the ID column if it exists
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        # Reset index to get clean 0, 1, 2... numbering
        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error loading data from Supabase: {e}")
        return pd.DataFrame()

def get_dynamic_height(text, line_height=22, max_height=640, min_height=100):
    """Calculate height dynamically based on text length, limited to table height."""
    if not text:
        return min_height
    lines = text.count("\n") + math.ceil(len(text) / 80)  # Approx line breaks
    height = lines * line_height
    # Ensure the AI chat never exceeds the table height (640px)
    return min(max_height, max(min_height, height))

def main():
    if "show_ai" not in st.session_state:
        st.session_state.show_ai = False
    if "ai_response" not in st.session_state:
        st.session_state.ai_response = ""

    # CSS for dynamic box and reduced padding
    st.markdown("""
        <style>
        /* Reduce default Streamlit padding - Multiple selectors for compatibility */
        .main .block-container {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
            max-width: none !important;
        }
        
        .block-container {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
            max-width: none !important;
        }
        
        .css-1d391kg {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
        }
        
        .css-18e3th9 {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
        }
        
        .css-1lcbmhc {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
        }
        
        /* Remove sidebar padding if any */
        section[data-testid="stSidebar"] {
            width: 0 !important;
            min-width: 0 !important;
        }
        
        /* Alternative approach - target by data attributes */
        [data-testid="stAppViewContainer"] > .main {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
        }
        
        [data-testid="stAppViewContainer"] {
            padding: 1.5rem 2rem 2.5rem 2rem !important; /* top right bottom left */
        }
        
        .response-box {
            background-color: #1f2937;
            border: 1px solid #4b5563;
            border-radius: 8px;
            padding: 1rem;
            overflow-y: auto;
            color: white;
            margin-top: 0.5rem;
            box-sizing: border-box;
        }

        /* Header toggle button spacing */
        .header-toggle {
            margin-top: 1.3rem; /* adjust if needed */
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("## 📊 IIT Bombay Placement Data 2024-25")
    with col2:
        st.markdown('<div class="header-toggle">', unsafe_allow_html=True)
        if st.button("🤖 Toggle AI Assistant"):
            st.session_state.show_ai = not st.session_state.show_ai
        st.markdown('</div>', unsafe_allow_html=True)

    # Load data
    df = load_supabase_data()
    if df.empty:
        st.error("No data available.")
        return

    if st.session_state.show_ai:
        table_col, ai_col = st.columns([3, 1], gap="medium")

        with table_col:
            st.dataframe(df, height=640, use_container_width=True, hide_index=False)

        with ai_col:
            st.subheader("AI Assistant")
            user_query = st.text_area("Your Question:", height=100)

            if st.button("Ask Agent"):
                if user_query:
                    backend_url = "http://127.0.0.1:8000/agent/chat"
                    try:
                        with st.spinner("Thinking..."):
                            response = requests.post(backend_url, json={"query": user_query})
                        if response.status_code == 200:
                            result = response.json()
                            st.session_state.ai_response = result['response']
                        else:
                            st.error(f"Error from backend: {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the FastAPI backend.")
                else:
                    st.warning("Please enter a question.")

            if st.session_state.ai_response:
                # Use configurable height for AI response
                dynamic_height = get_dynamic_height(st.session_state.ai_response, max_height=AI_RESPONSE_HEIGHT)
                st.markdown(
                    f"<div class='response-box' style='height:{dynamic_height}px'>{st.session_state.ai_response}</div>",
                    unsafe_allow_html=True
                )

    else:
        st.dataframe(df, height=640, use_container_width=True, hide_index=False)

if __name__ == "__main__":
    main()







