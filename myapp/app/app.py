import streamlit as st
import requests
import os

st.set_page_config(layout="wide", page_title="House Price Prediction")

# Set API URL
api_url = os.getenv("API_URL", "http://localhost:8000")

# Custom CSS for blue styling
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background-color: #1f77b4;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1.5em;
        }
        .stSelectbox>div>div>div {
            background-color: #e6f0fa;
        }
        .stTextInput>div>div>input, .stNumberInput>div>input {
            background-color: #e6f0fa;
        }
    </style>
""", unsafe_allow_html=True)

# Title bar with blue background
st.markdown('<div style="background-color:#1f77b4;padding:1em;text-align:center;border-radius:10px">'
            '<h1 style="color:white;">House Price Prediction</h1></div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    st.markdown("### 👤 User Type")
    user_type = st.selectbox("Choose User Type", ["Agent", "Owner", "Buyer"])

    st.markdown("###Enter Property Details")
    size = st.number_input("Size (sqm)", min_value=20.0, max_value=1000.0, value=75.0)
    floor = st.number_input("Floor", min_value=1, max_value=12, value=2)
    rooms = st.number_input("Number of Rooms", min_value=1, max_value=6, value=2)
    year_built = st.number_input("Year Built", min_value=1860, max_value=2023, value=2000)
    renovation_status = st.selectbox("Renovation Status", ["Newly Renovated", "Partially Renovated", "Not Renovated"])
    property_type = st.selectbox("Property Type", ["Apartment", "House"])
    location = st.selectbox("Location", ["Yerevan"])  # placeholder
    deal_type = st.radio("Prediction For", ["Sell", "Rent"])

    
    if st.button("Evaluate"):
        payload = {
            "size_sqm": size,
            "floor": floor,
            "rooms": rooms,
            "year_built": year_built,
            "renovation_status": renovation_status,
            "type_id": 1 if property_type == "Apartment" else 2,
            "location_id": 1,  # Update with real IDs if needed
            "deal_type": deal_type.lower(),
            "user_type": user_type.lower()
        }

        try:
            response = requests.post(f"{api_url}/predict", json=payload)
            response.raise_for_status()
            result = response.json()

            with right:
                st.markdown("### 📊 The most optimal price based on your preference")
                st.markdown(f"<h2 style='color:#1f77b4;'>${result['predicted_price']}</h2>", unsafe_allow_html=True)
                st.markdown("### 🏠 Similar Houses")
                cols = st.columns(3)
                for idx, image_url in enumerate(result["similar_images"]):
                    cols[idx % 3].image(image_url, use_column_width=True)

        except requests.RequestException as e:
            st.error(f"❌ Error fetching prediction: {e}")
