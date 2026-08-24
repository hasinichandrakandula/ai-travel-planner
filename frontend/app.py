import streamlit as st
import requests

BACKEND_URL = "https://ai-travel-planner-6-751n.onrender.com"

st.set_page_config(page_title="AI Travel Planner", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# --- SIDEBAR AUTH ---
with st.sidebar:
    st.title("Account")
    
    if st.session_state["token"]:
        st.success(f"Logged in as **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state["token"] = None
            st.session_state["username"] = None
            st.rerun()
    else:
        auth_mode = st.radio("Choose action", ["Signup", "Login"])
        uname = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if auth_mode == "Signup":
            email = st.text_input("Email")
            if st.button("Sign Up"):
                if not uname or not pwd or not email:
                    st.warning("Please fill in all fields.")
                else:
                    payload = {"username": uname, "email": email, "password": pwd}
                    res = requests.post(f"{BACKEND_URL}/signup", json=payload)
                    if res.status_code in [200, 201]:
                        data = res.json()
                        st.session_state["token"] = data.get("access_token")
                        st.session_state["username"] = data.get("username", uname)
                        st.success("✅ Signup successful! Logged in.")
                        st.rerun()
                    else:
                        st.error(f"❌ Signup failed: {res.text}")

        elif auth_mode == "Login":
            if st.button("Login"):
                if not uname or not pwd:
                    st.warning("Please enter username and password.")
                else:
                    payload = {"username": uname, "password": pwd}
                    res = requests.post(f"{BACKEND_URL}/login", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["token"] = data.get("access_token")
                        st.session_state["username"] = data.get("username", uname)
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

# --- MAIN SCREEN ---
st.title("✈️ AI Travel Planner")

destination = st.text_input("Where do you want to go?", "visakhapatnam")
days = st.slider("Trip Duration (Days)", 1, 7, 3)

if st.button("Generate Travel Plan"):
    if not st.session_state["token"]:
        st.warning("⚠️ Please log in or sign up using the sidebar first!")
    else:
        headers = {
            "Authorization": f"Bearer {st.session_state['token']}",
            "Content-Type": "application/json"
        }
        payload = {
            "destination": destination,
            "days": days,
            "preferences": [],
            "budget": "any"
        }

        with st.spinner("Generating plan..."):
            res = requests.post(f"{BACKEND_URL}/recommend", json=payload, headers=headers)
            
            if res.status_code == 200:
                data = res.json()

                # Trip Summary
                st.subheader("📝 Trip Summary")
                st.write(data.get("ai_summary", "No summary generated."))

                # Attractions
                st.subheader("📸 Tourist Attractions")
                attractions = data.get("attractions", [])
                if attractions:
                    for item in attractions:
                        name = item.get("name", "Unnamed")
                        addr = item.get("address", "")
                        map_url = item.get("maps_url", "#")
                        st.markdown(f"- **[{name}]({map_url})** — {addr}")
                else:
                    st.info("No attractions found.")

                # Hotels
                st.subheader("🏨 Hotels")
                hotels = data.get("hotels", [])
                if hotels:
                    for item in hotels:
                        name = item.get("name", "Unnamed")
                        addr = item.get("address", "")
                        map_url = item.get("maps_url", "#")
                        st.markdown(f"- **[{name}]({map_url})** — {addr}")
                else:
                    st.info("No hotels found.")

                # Restaurants
                st.subheader("🍽️ Restaurants")
                restaurants = data.get("restaurants", [])
                if restaurants:
                    for item in restaurants:
                        name = item.get("name", "Unnamed")
                        addr = item.get("address", "")
                        map_url = item.get("maps_url", "#")
                        st.markdown(f"- **[{name}]({map_url})** — {addr}")
                else:
                    st.info("No restaurants found.")
            else:
                st.error(f"Error ({res.status_code}): {res.text}")