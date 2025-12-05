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
AI_RESPONSE_HEIGHT = 510  # Change this value to adjust AI chat window height

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
        response = supabase_client.from_("placements").select("phase, company_name, job_role, job_location, gross_salary_btech, ctc_btech, currency, job_requirements, job_info, company_info, additional_details").execute()
        
        if not response.data:
            st.error("No data found in the 'placements' table.")
            return pd.DataFrame()
            
        df = pd.DataFrame(response.data)
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        st.error(f"Error loading data from Supabase: {e}")
        return pd.DataFrame()

def get_dynamic_height(text, line_height=22, max_height=640, min_height=100):
    """Calculate height dynamically based on text length, limited to table height."""
    if not text:
        return min_height
    lines = text.count("\n") + math.ceil(len(text) / 80)
    height = lines * line_height
    return min(max_height, max(min_height, height))

def main():
    if "show_ai" not in st.session_state:
        st.session_state.show_ai = False
    if "ai_response" not in st.session_state:
        st.session_state.ai_response = ""

    # Optimized CSS with proper mobile/desktop handling
    st.markdown("""
        <style>
        /* Desktop padding - preserve current UI */
        @media (min-width: 768px) {
            .main .block-container,
            .block-container,
            [data-testid="stAppViewContainer"] > .main,
            [data-testid="stAppViewContainer"] {
                padding: 1.5rem 2rem 2.5rem 2rem !important;
                max-width: none !important;
            }
        }
        
        /* Mobile padding - maintain left padding, reduce right for columns */
        @media (max-width: 767px) {
            .main .block-container,
            .block-container,
            [data-testid="stAppViewContainer"] > .main,
            [data-testid="stAppViewContainer"] {
                padding: 1.5rem 0.5rem 2.5rem 2rem !important;
                max-width: none !important;
            }
            
            /* Ensure columns use full width on mobile */
            .stColumn {
                padding-left: 0 !important;
                padding-right: 0 !important;
            }
        }
        
        /* Legacy CSS class overrides for compatibility */
        .css-1d391kg,
        .css-18e3th9,
        .css-1lcbmhc {
            padding: inherit !important;
        }
        
        /* Remove sidebar padding */
        section[data-testid="stSidebar"] {
            width: 0 !important;
            min-width: 0 !important;
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
            max-height: 510px !important;
        }

        .header-toggle {
            margin-top: 1.3rem;
        }

        /* Column reordering: AI on top for mobile, table left/AI right for desktop */
        @media (max-width: 767px) {
            div.stHorizontalBlock.st-emotion-cache-1g9ga1i.eceldm42 {
                display: flex;
                flex-direction: column;
            }
            div.stHorizontalBlock.st-emotion-cache-1g9ga1i.eceldm42 > div:nth-child(1) {
                order: 2; /* Table second on mobile */
            }
            div.stHorizontalBlock.st-emotion-cache-1g9ga1i.eceldm42 > div:nth-child(2) {
                order: 1; /* AI first on mobile */
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("## 📊 IIT Bombay Placement Data 2024‑25")
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
        # Table first, AI second for proper desktop layout (table left, AI right)
        table_col, ai_col = st.columns([3, 1], gap="medium")

        with table_col:
            st.dataframe(df, height=640, use_container_width=True, hide_index=False)

        with ai_col:
            st.subheader("AI Assistant 🤖")
            user_query = st.text_area(
                "Your Question:", 
                height=100,
                placeholder="Ask me anything about the placement data \neg: what ML algorithms do companies ask?"
            )

            if st.button("Ask Agent"):
                st.error("A̶P̶I̶ ̶k̶a̶ ̶b̶i̶l̶l̶ ̶t̶e̶r̶a̶ ̶b̶a̶a̶p̶ ̶b̶h̶a̶r̶e̶g̶a̶?̶  \nOwner may have taken AI service down due to high api usage")
              # if user_query:
            #     backend_url = "https://placement-portal-backend-1znu.onrender.com/agent/chat"
            #     try:
            #         with st.spinner("Thinking..."):
            #             response = requests.post(backend_url, json={"query": user_query})
            #         if response.status_code == 200:
            #             result = response.json()
            #             st.session_state.ai_response = result['response']
            #         else:
            #             st.error(f"Error from backend: {response.text}")
            #     except requests.exceptions.ConnectionError:
            #         st.error("A̶P̶I̶ ̶k̶a̶ ̶b̶i̶l̶l̶ ̶t̶e̶r̶a̶ ̶b̶a̶a̶p̶ ̶b̶h̶a̶r̶e̶g̶a̶?̶  \nOwner may have taken AI service down due to high api usage")
            # else:
            #     st.warning("Please enter a question.")

            if st.session_state.ai_response:
                dynamic_height = get_dynamic_height(st.session_state.ai_response, max_height=AI_RESPONSE_HEIGHT)
                st.markdown(
                    f"<div class='response-box' style='height:{dynamic_height}px'>{st.session_state.ai_response}</div>",
                    unsafe_allow_html=True
                )

    else:
        st.dataframe(df, height=640, use_container_width=True, hide_index=False)

if __name__ == "__main__":
    main()







