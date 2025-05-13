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
    # Removed user_type as it's not directly used by the backend model prediction logic
    # If you needed it, you'd map it to a user_id below
    # st.markdown("### User Type", unsafe_allow_html=True)
    # user_type_selection = st.selectbox("Choose User Type", ["Agent", "Owner", "Buyer"], label_visibility="collapsed")

    st.markdown("### Enter Property Details", unsafe_allow_html=True)
    size = st.number_input("Size (sqm)", min_value=20.0, max_value=1000.0, value=75.0, key="size_input")
    floor = st.number_input("Floor", min_value=1, max_value=100, value=2, key="floor_input") # Increased max floor
    rooms = st.number_input("Number of Rooms", min_value=1, max_value=10, value=2, key="rooms_input") # Increased max rooms
    year_built = st.number_input("Year Built", min_value=1860, max_value=2024, value=2000, key="year_input") # Adjusted max year

    renovation_status = st.selectbox("Renovation Status",
                                  ["Newly Renovated", "Partially Renovated", "Not Renovated"], key="renovation_select")

    property_type = st.selectbox("Property Type", ["Apartment", "House"], key="type_select")
    # Assuming Location ID 1 is always Yerevan for now.
    # If you have multiple locations, you'd map the selection to an ID.
    location_name = st.selectbox("Location", ["Yerevan"], key="location_select")
    location_id_map = {"Yerevan": 1} # Example mapping
    location_id = location_id_map.get(location_name, 1) # Default to 1 if not found


    st.markdown("### Prediction For", unsafe_allow_html=True)
    deal_type = st.radio("Deal Type", ["Sell", "Rent"], horizontal=True, label_visibility="collapsed", key="deal_radio")

    if st.button("Evaluate Property"):
        # Build the payload matching the PropertyBase schema
        payload = {
            # --- ADDED REQUIRED FIELDS with dummy values ---
            "property_id": 0,  # Dummy Property ID
            "user_id": 0,      # Dummy User ID (or map user_type_selection if needed)

            # --- Fields from your form ---
            "size_sqm": size,
            "floor": floor,
            "rooms": rooms,
            "year_built": year_built,
            "renovation_status": renovation_status,
            "type_id": 1 if property_type == "Apartment" else 2,
            "location_id": location_id, # Use the mapped ID
            "deal_type": deal_type.lower(),

            # --- Include Optional fields as None or default if needed by backend logic ---
            # These are Optional in Pydantic, so omitting them is usually fine unless
            # your internal backend logic specifically requires them.
            "title": None,
            "status": None,
            "post_date": None, # Or date.today().isoformat() if needed
            "sell_date": None,
            "estimated_saleprice": None,
            "estimated_rentprice": None
        }

        # Pick correct endpoint name
        endpoint = "sale-cox" if deal_type == "Sell" else "rent-cox"
        full_url = f"{api_url}/predict/{endpoint}"
        st.write(f"Sending request to: {full_url}") # Debugging line
        st.write(f"Payload: {payload}")             # Debugging line

        try:
            resp = requests.post(full_url, json=payload)
            resp.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
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
                        st.json(result)


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
                         st.json(result)

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
                    st.json(result)


        except requests.exceptions.ConnectionError as e:
             st.error(f"Connection Error: Could not connect to the API at {api_url}. Is the backend running?")
             st.error(f"Details: {e}")
        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error: {e.response.status_code} {e.response.reason} for URL: {e.request.url}")
            try:
                # Try to show detailed error from FastAPI if available
                error_detail = e.response.json()
                st.error(f"API Error Detail: {error_detail}")
            except requests.exceptions.JSONDecodeError:
                st.error(f"API Response Content: {e.response.text}") # Show raw text if not JSON
        except requests.RequestException as e:
            st.error(f"Error fetching prediction: {e}")
        except Exception as e: # Catch other potential errors
            st.error(f"An unexpected error occurred: {e}")
