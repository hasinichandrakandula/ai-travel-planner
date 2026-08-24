import os
import requests
import streamlit as st

# Point to your active Render backend
BACKEND_URL = os.getenv("BACKEND_URL", "https://ai-travel-planner-8-75ia.onrender.com").rstrip("/")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI Travel Planner")
st.write("Discover places, hotels and restaurants with AI")

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- SIDEBAR AUTH ----------------
menu = st.sidebar.radio("Account", ["Signup", "Login"])

# ======================================================
# SIGNUP
# ======================================================
if menu == "Signup":
    st.sidebar.header("Create Account")

    signup_username = st.sidebar.text_input("Username")
    signup_email = st.sidebar.text_input("Email")
    signup_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Signup"):
        if not signup_username.strip():
            st.sidebar.error("Username cannot be empty")
        elif not signup_email.strip() or "@" not in signup_email:
            st.sidebar.error("Please enter a valid email address")
        elif not signup_password:
            st.sidebar.error("Password cannot be empty")
        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/signup",
                    json={
                        "username": signup_username.strip(),
                        "email": signup_email.strip(),
                        "password": signup_password.strip()
                    }
                )
                if response.status_code in [200, 201]:
                    data = response.json()
                    st.session_state.token = data.get("access_token")
                    st.sidebar.success("Signup successful! You are now logged in.")
                    st.rerun()
                else:
                    detail = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                    st.sidebar.error(f"Signup failed: {detail}")
            except Exception as e:
                st.sidebar.error(f"Could not connect to backend: {e}")

# ======================================================
# LOGIN
# ======================================================
elif menu == "Login":
    st.sidebar.header("Login")

    login_username = st.sidebar.text_input("Username", key="login_username")
    login_password = st.sidebar.text_input("Password", type="password", key="login_password")

    if st.sidebar.button("Login"):
        if not login_username.strip() or not login_password.strip():
            st.sidebar.error("Please enter both username and password")
        else:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/login",
                    json={
                        "username": login_username.strip(),
                        "password": login_password.strip()
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.sidebar.success("Login Successful!")
                    st.rerun()
                else:
                    st.sidebar.error("Invalid username or password")
            except Exception as e:
                st.sidebar.error(f"Could not connect to backend: {e}")

# ======================================================
# RECOMMENDATIONS
# ======================================================
st.header("🌍 Search Destination")

destination = st.text_input("Destination", placeholder="Example: Paris")

if st.button("Get Recommendations"):
    if st.session_state.token is None:
        st.warning("Please login first.")
    elif destination.strip() == "":
        st.warning("Please enter a destination.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        with st.spinner("Generating AI travel recommendations..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/recommend",
                    headers=headers,
                    json={
                        "destination": destination.strip(),
                        "preferences": [],
                        "days": 3
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("Recommendations Found!")

                    if result.get("ai_summary"):
                        st.subheader("📋 Trip Summary")
                        st.write(result["ai_summary"])

                    # Tourist Attractions
                    st.subheader("🏝 Tourist Attractions")
                    if result.get("attractions"):
                        for place in result["attractions"]:
                            st.markdown(f"### 📍 {place['name']}")
                            st.write("Address:", place.get("address", "N/A"))
                            if place.get("maps_url"):
                                st.markdown(f"[🌍 Open in OpenStreetMap]({place['maps_url']})")
                            st.write("---")
                    else:
                        st.info("No attractions found.")

                    # Hotels
                    st.subheader("🏨 Hotels")
                    if result.get("hotels"):
                        for hotel in result["hotels"]:
                            st.markdown(f"### 🏨 {hotel['name']}")
                            st.write("Address:", hotel.get("address", "N/A"))
                            if hotel.get("maps_url"):
                                st.markdown(f"[🌍 Open in OpenStreetMap]({hotel['maps_url']})")
                            st.write("---")
                    else:
                        st.info("No hotels found.")

                    # Restaurants
                    st.subheader("🍽 Restaurants")
                    if result.get("restaurants"):
                        for restaurant in result["restaurants"]:
                            st.markdown(f"### 🍴 {restaurant['name']}")
                            st.write("Address:", restaurant.get("address", "N/A"))
                            if restaurant.get("maps_url"):
                                st.markdown(f"[🌍 Open in OpenStreetMap]({restaurant['maps_url']})")
                            st.write("---")
                    else:
                        st.info("No restaurants found.")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to fetch recommendations: {e}")

# ======================================================
# HISTORY
# ======================================================
st.header("📜 My Travel History")

if st.button("Show History"):
    if st.session_state.token is None:
        st.warning("Please login first.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        try:
            response = requests.get(f"{BACKEND_URL}/history", headers=headers)
            if response.status_code == 200:
                history = response.json()
                if not history:
                    st.info("No history found.")
                else:
                    st.json(history)
            else:
                st.error(response.text)
        except Exception as e:
            st.error(f"Could not load history: {e}")