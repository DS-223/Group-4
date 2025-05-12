import streamlit as st
import requests
import os

st.set_page_config(layout="wide", page_title="House Price Prediction")

# Set API URL
api_url = os.getenv("API_URL", "http://localhost:8000")

# Enhanced CSS with visual effects
st.markdown("""
    <style>
        /* Main background with subtle texture */
        .stApp {
            background-color: #f8f9fa;
            background-image: radial-gradient(#e9ecef 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        /* Form container styling */
        .st-emotion-cache-1jicfl2 {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        /* Title bar with gradient */
        .title-container {
            background: linear-gradient(135deg, #1f77b4 0%, #025a96 100%);
            padding: 1.5em;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Input fields with hover effects */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stSelectbox>div>div>div {
            background-color: white;
            color: black;
            border: 1px solid #ced4da;
            border-radius: 8px;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
        }
        
        .stTextInput>div>div>input:hover,
        .stNumberInput>div>div>input:hover,
        .stSelectbox>div>div>div:hover {
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
        }
        
        .stTextInput>div>div>input:focus,
        .stNumberInput>div>div>input:focus,
        .stSelectbox>div>div>div:focus {
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.2);
        }
        
        /* Labels with better spacing */
        label {
            color: #0074D9 !important;
            font-weight: 600;
            margin-bottom: 0.5rem !important;
            display: block;
        }
        
        /* Enhanced button with hover effect */
        .stButton>button {
            background-color: #1f77b4;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 200px;
            margin: 1.5rem auto 0;
            display: block;
        }
        
        .stButton>button:hover {
            background-color: #025a96;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
        
         /* Radio button text - guaranteed black */
        .stRadio div[role="radiogroup"] label div {
            color: black !important;
        }
        
        /* Selected radio button indicator */
        [data-baseweb="radio"] div:first-child {
            border-color: #1f77b4 !important;
        }
        
        
        /* Section headers - FIX FOR WHITE TEXT ISSUE */
        h3 {
            color: #1f77b4 !important;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 0.5rem;
            margin-top: 1.5rem !important;
        }
        
        /* Specific fix for Prediction For header */
        div[data-testid="stMarkdownContainer"] h3 {
            color: #1f77b4 !important;
        }
        
        /* Prediction results styling */
        .prediction-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            border-left: 4px solid #1f77b4;
        }
    </style>
""", unsafe_allow_html=True)

# Enhanced title bar
st.markdown("""
    <div class="title-container">
        <h1 style="color:white; margin:0;">House Price Prediction</h1>
        <p style="color:rgba(255,255,255,0.8); margin:0.5rem 0 0;">Get accurate property valuation in seconds</p>
    </div>
""", unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown("### User Type", unsafe_allow_html=True)
    user_type = st.selectbox("Choose User Type", ["Agent", "Owner", "Buyer"], label_visibility="collapsed")

    st.markdown("### Enter Property Details", unsafe_allow_html=True)
    size = st.number_input("Size (sqm)", min_value=20.0, max_value=1000.0, value=75.0)
    floor = st.number_input("Floor", min_value=1, max_value=12, value=2)
    rooms = st.number_input("Number of Rooms", min_value=1, max_value=6, value=2)
    year_built = st.number_input("Year Built", min_value=1860, max_value=2023, value=2000)
    
    renovation_status = st.selectbox("Renovation Status", 
                                  ["Newly Renovated", "Partially Renovated", "Not Renovated"])
    
    property_type = st.selectbox("Property Type", ["Apartment", "House"])
    location = st.selectbox("Location", ["Yerevan"])
    
    # Fixed "Prediction For" header - now will appear in blue
    st.markdown("### Prediction For", unsafe_allow_html=True)
    deal_type = st.radio("", ["Sell", "Rent"], horizontal=True, label_visibility="collapsed")

    if st.button("Evaluate Property"):
        payload = {
            "size_sqm": size,
            "floor": floor,
            "rooms": rooms,
            "year_built": year_built,
            "renovation_status": renovation_status,
            "type_id": 1 if property_type == "Apartment" else 2,
            "location_id": 1,
            "deal_type": deal_type.lower(),
            "user_type": user_type.lower()
        }
        endpoint = "sale" if deal_type == "Sell" else "rent"
        try:
            response = requests.post(f"{api_url}/predict/{endpoint}", json=payload)
            response.raise_for_status()
            price_result = response.json()

            prob_response = requests.post(f"{api_url}/predict/cox", json=payload)
            prob_response.raise_for_status()
            prob_result = prob_response.json()

            with right:
                st.markdown("### 📈 Predictions Summary", unsafe_allow_html=True)
                
                st.markdown("""
                <div class="prediction-card">
                    <h4 style="color:#0074D9; margin-top:0;">Estimated Sell Price</h4>
                    <h2 style="color:#1f77b4; margin-bottom:0;">${:,.2f}</h2>
                </div>
                """.format(price_result['predicted_sell_price']), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="prediction-card">
                    <h4 style="color:#0074D9; margin-top:0;">Estimated Rent Price</h4>
                    <h2 style="color:#1f77b4; margin-bottom:0;">${:,.2f}</h2>
                </div>
                """.format(price_result['predicted_rent_price']), unsafe_allow_html=True)
                
                st.markdown("""
                <div class="prediction-card">
                    <h4 style="color:#0074D9; margin-top:0;">Probability of Selling Within 5 Months</h4>
                    <h2 style="color:#1f77b4; margin-bottom:0;">{:.1f}%</h2>
                </div>
                """.format(price_result['probability_sold_within_5_months']*100), unsafe_allow_html=True)

        except requests.RequestException as e:
            st.error(f"Error fetching prediction: {e}")