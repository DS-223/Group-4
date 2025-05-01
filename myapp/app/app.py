import streamlit as st
import requests
import os
import streamlit.components.v1 as components

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

    st.markdown("### Enter Property Details")
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
        endpoint = "rent" if deal_type == "Rent" else "sale"
        try:
            response = requests.post(f"{api_url}/predict/{endpoint}", json=payload)
            response.raise_for_status()
            result = response.json()

            with right:
                st.markdown("Predictions Summary")

                st.markdown("**Estimated Sell Price**")
                st.markdown(f"<h2 style='color:#1f77b4;'>${result['predicted_sell_price']:.2f}</h2>", unsafe_allow_html=True)

                st.markdown("**Estimated Rent Price**")
                st.markdown(f"<h2 style='color:#ff7f0e;'>${result['predicted_rent_price']:.2f}</h2>", unsafe_allow_html=True)

                st.markdown("**Probability of Selling Within 5 Months**")
                st.markdown(f"<h2 style='color:#2ca02c;'>{result['probability_sold_within_5_months']*100:.1f}%</h2>", unsafe_allow_html=True)

                st.markdown("### 🏠 Similar Houses")
                image_carousel = "<div style='display:flex; overflow-x:auto; gap:10px; padding:10px; scrollbar-width: none;'>"
                for image_url in result["similar_images"]:
                    image_carousel += f"""
                        <div style='flex:0 0 auto;'>
                            <img src="{image_url}" style='height:200px; border-radius:10px;'>
                        </div>
                    """
                image_carousel += "</div>"

                components.html(image_carousel, height=220, scrolling=True)

        except requests.RequestException as e:
            st.error(f"❌ Error fetching prediction: {e}")
