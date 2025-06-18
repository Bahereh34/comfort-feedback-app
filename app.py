"""

# --- Supabase Configuration ---
SUPABASE_URL = "https://wgxwlildclogrdbgvtpr.supabase.co"  # Replace with your URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndneHdsaWxkY2xvZ3JkYmd2dHByIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyNTM5MTIsImV4cCI6MjA2NTgyOTkxMn0.vpfHJA_9WecWpPa8g7OeFS02F391NCLJCDHFGZiTsLw"  # Replace with your anon key
"""
import streamlit as st
import speech_recognition as sr
from supabase import create_client, Client
from datetime import datetime
import uuid
import re

# --- Supabase Configuration ---
SUPABASE_URL = "https://wgxwlildclogrdbgvtpr.supabase.co"  # ← Replace with your Supabase URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndneHdsaWxkY2xvZ3JkYmd2dHByIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyNTM5MTIsImV4cCI6MjA2NTgyOTkxMn0.vpfHJA_9WecWpPa8g7OeFS02F391NCLJCDHFGZiTsLw"  # Replace with your anon key

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Initialize session state ---
if "feedback_text" not in st.session_state:
    st.session_state["feedback_text"] = ""
if "room" not in st.session_state:
    st.session_state["room"] = ""
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

# --- Streamlit UI ---
st.title("🎙️ Real-Time Comfort Feedback")

feedback_type = st.selectbox("Type of comfort feedback:", ["Thermal", "Visual"])

# Text inputs pre-filled from session state
feedback_text = st.text_area(
    "Describe your experience (or use voice input):",
    value=st.session_state["feedback_text"]
)
room = st.text_input("Room/Location (optional)", value=st.session_state["room"])
user_id = st.text_input("User ID (optional)", value=st.session_state["user_id"])

# --- Voice Input Function ---
def extract_room_user(transcript):
    room_match = re.search(r"room\s+(\d+)", transcript, re.IGNORECASE)
    user_match = re.search(r"user\s*(id)?\s*(\d+)", transcript, re.IGNORECASE)

    room_number = room_match.group(1) if room_match else ""
    user_number = user_match.group(2) if user_match else ""

    cleaned = transcript
    if room_match:
        cleaned = cleaned.replace(room_match.group(0), "")
    if user_match:
        cleaned = cleaned.replace(user_match.group(0), "")

    return cleaned.strip(), room_number, user_number

# --- Record Voice Button ---
if st.button("🎤 Record Voice Input"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Please speak clearly.")
        audio = recognizer.listen(source, phrase_time_limit=5)

    try:
        transcript = recognizer.recognize_google(audio)
        st.success(f"📝 You said: {transcript}")

        feedback_cleaned, extracted_room, extracted_user = extract_room_user(transcript)

        # Update session state
        st.session_state["feedback_text"] = feedback_cleaned
        st.session_state["room"] = extracted_room
        st.session_state["user_id"] = extracted_user

    except sr.UnknownValueError:
        st.error("❌ Could not understand your voice.")
    except sr.RequestError as e:
        st.error(f"❌ Error from Google Speech API: {e}")

# --- Submit Button ---
if st.button("Submit Feedback"):
    final_feedback = feedback_text.strip() or st.session_state["feedback_text"].strip()
    final_room = room.strip() or st.session_state["room"].strip()
    final_user_id = user_id.strip() or st.session_state["user_id"].strip()

    if final_feedback == "":
        st.warning("Please enter or record your feedback.")
    else:
        data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "feedback_type": feedback_type.lower(),
            "feedback_text": final_feedback,
            "room": final_room,
            "user_id": final_user_id
        }
        try:
            supabase.table("feedback").insert(data).execute()
            st.success("✅ Feedback submitted successfully!")

            # Clear session state after submit
            st.session_state["feedback_text"] = ""
            st.session_state["room"] = ""
            st.session_state["user_id"] = ""
        except Exception as e:
            st.error(f"❌ Failed to submit: {e}")
