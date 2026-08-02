import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI Travel Planner")
st.write("Discover places, hotels and restaurants with AI")

# ---------------- SESSION ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio(
    "Account",
    ["Signup", "Login"]
)

# ======================================================
# SIGNUP
# ======================================================
# ======================================================
# SIGNUP
# ======================================================
if menu == "Signup":
    
    st.sidebar.header("Create Account")

    signup_username = st.sidebar.text_input("Username")

    signup_email = st.sidebar.text_input("Email")

    signup_password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Signup"):

        st.write("DEBUG EMAIL:", repr(signup_email))

        if signup_email.strip() == "":
            st.sidebar.error("Email cannot be empty")

        elif "@" not in signup_email:
            st.sidebar.error("Please enter a valid email address")

        else:
            response = requests.post(
                f"{BACKEND_URL}/signup",
                json={
                    "username": signup_username,
                    "email": signup_email,
                    "password": signup_password
                }
            )
        if response.ok:
            st.sidebar.success("Signup successful! Please login.")
        else:
          st.sidebar.error(response.text)
# ======================================================
# LOGIN
# ======================================================
elif menu == "Login":

    st.sidebar.header("Login")

    login_username = st.sidebar.text_input(
        "Username",
        key="login_username"
    )

    login_password = st.sidebar.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.sidebar.button("Login"):

        response = requests.post(
            f"{BACKEND_URL}/login",
            json={
                "username": login_username,
                "password": login_password
            }
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.token = data["access_token"]

            st.sidebar.success("Login Successful!")

        else:
            st.sidebar.error("Invalid email or password")

# ======================================================
# RECOMMENDATIONS
# ======================================================

st.header("🌍 Search Destination")

destination = st.text_input(
    "Destination",
    placeholder="Example: Paris"
)

if st.button("Get Recommendations"):

    if st.session_state.token is None:

        st.warning("Please login first.")

    elif destination.strip() == "":

        st.warning("Please enter a destination.")

    else:

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{BACKEND_URL}/recommend",
            headers=headers,
            json={
                "destination": destination
            }
        )

        if response.status_code == 200:

            result = response.json()

        if response.status_code == 200:
    
            result = response.json()

            st.success("Recommendations Found!")

            # ==========================
            # Tourist Attractions
            # ==========================
            st.subheader("🏝 Tourist Attractions")

            if result.get("attractions"):
                for place in result["attractions"]:
                    st.markdown(f"### 📍 {place['name']}")
                    st.write("📍 Address:", place["address"])

                    if place.get("maps_url"):
                        st.markdown(f"[🌍 Open in OpenStreetMap]({place['maps_url']})")

                    st.write("---")
            else:
                st.info("No attractions found.")

            # ==========================
            # Hotels
            # ==========================
            st.subheader("🏨 Hotels")

            if result.get("hotels"):
                for hotel in result["hotels"]:
                    st.markdown(f"### 🏨 {hotel['name']}")
                    st.write("📍 Address:", hotel["address"])

                    if hotel.get("maps_url"):
                        st.markdown(f"[🌍 Open in OpenStreetMap]({hotel['maps_url']})")

                    st.write("---")
            else:
                st.info("No hotels found.")

              # ==========================
              # Restaurants
              # ==========================
            st.subheader("🍽 Restaurants")
              
              
            if result.get("restaurants"):
                  for restaurant in result["restaurants"]:
                      st.markdown(f"### 🍴 {restaurant['name']}")
                      st.write("📍 Address:", restaurant["address"])
              
                      if restaurant.get("maps_url"):
                          st.markdown(f"[🌍 Open in OpenStreetMap]({restaurant['maps_url']})")
              
                      st.write("---")
            else:
                  st.info("No restaurants found.")
              
# ======================================================
# HISTORY
# ======================================================

st.header("📜 My Travel History")

if st.button("Show History"):

    if st.session_state.token is None:

        st.warning("Please login first.")

    else:

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.get(
            f"{BACKEND_URL}/history",
            headers=headers
        )

        if response.status_code == 200:

            history = response.json()

            if len(history) == 0:
                st.info("No history found.")
            else:
                st.json(history)
        else:
            st.error(response.text)