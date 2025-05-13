import streamlit as st
import requests
import os

st.set_page_config(layout="wide", page_title="House Price Prediction")

# Set API URL
api_url = os.getenv("API_URL", "http://localhost:8000")

# Enhanced CSS with visual effects
st.markdown("""
    <style>
        .stApp {
            background-color: #f8f9fa;
            background-image: radial-gradient(#e9ecef 1px, transparent 1px);
            background-size: 20px 20px;
        }

        /* Form container */
        .st-emotion-cache-1jicfl2 {
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            padding: 2rem;
            margin-bottom: 2rem;
        }

        /* Title bar */
        .title-container {
            background: linear-gradient(135deg, #1f77b4 0%, #025a96 100%);
            padding: 1.5em;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Updated input styles */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stSelectbox>div>div>div,
        .stRadio div[role="radiogroup"] > div {
            background-color: white !important;
            color: #0074D9 !important;
            border: 1px solid #ced4da;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }

        .stNumberInput input {
            background-color: white !important;
            color: #0074D9 !important;
        }

        .stNumberInput>div>div>input {
            background-color: white !important;
            color: #0074D9 !important;
        }

        .stNumberInput>div>div {
            background-color: white !important;
            border-color: #ced4da !important;
        }
        /* number input hover state */
        .stNumberInput:hover>div>div>input {
            background-color: blue !important;
            color: blue !important;
        }

        
        /* number input focus state */
        .stNumberInput>div>div>input:focus {
            background-color: white !important;
            color: #0074D9 !important;
        }

        /* Dropdown menu styling */
        .stSelectbox [data-baseweb="select"] div {
            background-color: white !important;
            color: #0074D9 !important;
        }

        /* Dropdown options */
        [data-baseweb="popover"] div {
            background-color: white !important;
            color: #0074D9 !important;
        }

        /* Fix number input arrows */
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        input[type="number"] {
            -moz-appearance: textfield;
            color: #0074D9 !important;
        }

        /* Hover states */
        .stTextInput>div>div>input:hover,
        .stNumberInput>div>div>input:hover,
        .stSelectbox>div>div>div:hover,
        .stRadio div[role="radiogroup"] > div:hover {
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.1);
        }

        /* Focus states */
        .stTextInput>div>div>input:focus,
        .stNumberInput>div>div>input:focus,
        .stSelectbox>div>div>div:focus,
        .stRadio div[role="radiogroup"] > div:focus {
            border-color: #1f77b4;
            box-shadow: 0 0 0 3px rgba(31, 119, 180, 0.2);
        }

        /* Radio buttons */
        .stRadio div[role="radiogroup"] label div {
            color: #0074D9 !important;
        }

        [data-baseweb="radio"] div:first-child {
            border-color: #1f77b4 !important;
        }

        /* Labels */
        label {
            color: #0074D9 !important;
            font-weight: 600;
            margin-bottom: 0.5rem !important;
            display: block;
        }

        /* Button styling */
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
            background-color: lightblue;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }

        /* Section headers */
        h3, div[data-testid="stMarkdownContainer"] h3 {
            color: #1f77b4 !important;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 0.5rem;
            margin-top: 1.5rem !important;
        }

        /* Prediction card */
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
    user_type_selection = st.selectbox("Choose User Type", ["Agent", "Owner", "Buyer"], label_visibility="collapsed")

    st.markdown("### Enter Property Details", unsafe_allow_html=True)
    size = st.number_input("Size (sqm)", min_value=20.0, max_value=1000.0, value=75.0, key="size_input")
    floor = st.number_input("Floor", min_value=1, max_value=100, value=2, key="floor_input")
    rooms = st.number_input("Number of Rooms", min_value=1, max_value=10, value=2, key="rooms_input")
    year_built = st.number_input("Year Built", min_value=1860, max_value=2024, value=2000, key="year_input")

    renovation_status = st.selectbox("Renovation Status",
                                  ["Newly Renovated", "Partially Renovated", "Not Renovated"], key="renovation_select")

    property_type = st.selectbox("Property Type", ["Apartment", "House"], key="type_select")
    
    distinct_name = st.selectbox("Location", ["Kentron", "Arabkir", "Avan", "Davtashen", "Erebuni", "Malatia-Sebastia",
    "Nor Nork", "Nork-Marash", "Shengavit", "Kanaker-Zeytun", "Ajapnyak", "Nubarashen"], key="location_select")
    location_id_map = {"Kentron": 1}
    location_id = location_id_map.get(distinct_name, 1)

    st.markdown("### Prediction For", unsafe_allow_html=True)
    deal_type = st.radio("Deal Type", ["Sell", "Rent"], horizontal=True, label_visibility="collapsed", key="deal_radio")

    if st.button("Evaluate Property"):
        payload = {
            "property_id": 0,
            "user_id": 0,
            "size_sqm": size,
            "floor": floor,
            "rooms": rooms,
            "year_built": year_built,
            "renovation_status": renovation_status,
            "type_id": 1 if property_type == "Apartment" else 2,
            "location_id": location_id,
            "deal_type": deal_type.lower(),
            "title": None,
            "status": None,
            "post_date": None,
            "sell_date": None,
            "estimated_saleprice": None,
            "estimated_rentprice": None
        }

        endpoint = "sale-cox" if deal_type == "Sell" else "rent-cox"
        full_url = f"{api_url}/predict/{endpoint}"

        try:
            resp = requests.post(full_url, json=payload)
            resp.raise_for_status()
            result = resp.json()

            with right:
                st.markdown("### 📈 Predictions Summary", unsafe_allow_html=True)

                if deal_type == "Sell":
                    if "predicted_sale_price" in result:
                        price = result["predicted_sale_price"]
                        st.markdown(f"""
                            <div class="prediction-card">
                              <h4 style="color:#0074D9; margin-top:0;">Estimated Sale Price</h4>
                              <h2 style="color:#1f77b4; margin-bottom:0;">${price:,.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("Prediction response missing 'predicted_sale_price'.")

                else:  # Rent
                    if "predicted_rent_price" in result:
                        price = result["predicted_rent_price"]
                        st.markdown(f"""
                            <div class="prediction-card">
                              <h4 style="color:#0074D9; margin-top:0;">Estimated Rent Price</h4>
                              <h2 style="color:#1f77b4; margin-bottom:0;">${price:,.2f}</h2>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                         st.error("Prediction response missing 'predicted_rent_price'.")

                if "prob_sold_within_5_months" in result:
                    prob = result["prob_sold_within_5_months"] * 100
                    st.markdown(f"""
                        <div class="prediction-card">
                          <h4 style="color:#0074D9; margin-top:0;">Probability of Selling Within 5 Months</h4>
                          <h2 style="color:#1f77b4; margin-bottom:0;">{prob:.1f}%</h2>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Prediction response missing 'prob_sold_within_5_months'.")

        except requests.exceptions.ConnectionError as e:
             st.error(f"Connection Error: Could not connect to the API at {api_url}. Is the backend running?")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e.response.status_code} {e.response.reason}")
            try:
                error_detail = e.response.json()
                st.error(f"API Error Detail: {error_detail}")
            except:
                st.error(f"API Response Content: {e.response.text}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")