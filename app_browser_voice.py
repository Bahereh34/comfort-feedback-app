import streamlit as st
import streamlit.components.v1 as components
import re
from datetime import datetime
import uuid
# Uncomment if using Supabase:
# from supabase import create_client, Client

# --- Optional: Set up Supabase if needed ---
#SUPABASE_URL = "https://wgxwlildclogrdbgvtpr.supabase.co"  # ← Replace with your Supabase URL
#SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndneHdsaWxkY2xvZ3JkYmd2dHByIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAyNTM5MTIsImV4cCI6MjA2NTgyOTkxMn0.vpfHJA_9WecWpPa8g7OeFS02F391NCLJCDHFGZiTsLw"  # Replace with your anon key

#supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Initialize session state ---
if "feedback_text" not in st.session_state:
    st.session_state["feedback_text"] = ""
if "room" not in st.session_state:
    st.session_state["room"] = ""
if "user_id" not in st.session_state:
    st.session_state["user_id"] = ""

# --- App UI ---
st.title("🎙️ Real-Time Comfort Feedback")

# --- Step 1: Voice input button using JavaScript + HTML ---
st.markdown("### Voice Input (Browser-based)")

components.html(
    """
    <script>
    function recordVoiceAndSendToStreamlit() {
      const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
      recognition.lang = 'en-US';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;

      recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const streamlitEvent = new CustomEvent("streamlit:voice_transcript", {
          detail: { transcript: transcript },
        });
        window.dispatchEvent(streamlitEvent);
      };

      recognition.onerror = function(event) {
        alert("Voice recognition error: " + event.error);
      };

      recognition.start();
    }

    window.addEventListener("streamlit:voice_transcript", function(event) {
      const transcript = event.detail.transcript;
      const data = {"transcript": transcript};
      window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: data }, "*");
    });
    </script>

    <button onclick="recordVoiceAndSendToStreamlit()">🎤 Speak Now</button>
    """,
    height=100,
)

# --- Step 2: If transcript arrives, store and extract room/user ---
if "transcript" in st.session_state:
    transcript = st.session_state["transcript"]
    st.session_state["feedback_text"] = transcript

    # --- Step 3: Extract room and user ID ---
    room_match = re.search(r"room\s+(\d+)", transcript, re.IGNORECASE)
    user_match = re.search(r"user\s*(id)?\s*(\d+)", transcript, re.IGNORECASE)

    if room_match:
        st.session_state["room"] = room_match.group(1)
    if user_match:
        st.session_state["user_id"] = user_match.group(2)

    # Clean up text by removing matched parts
    cleaned = transcript
    if room_match:
        cleaned = cleaned.replace(room_match.group(0), "")
    if user_match:
        cleaned = cleaned.replace(user_match.group(0), "")
    st.session_state["feedback_text"] = cleaned.strip()

# --- UI Form ---
feedback_type = st.selectbox("Type of comfort feedback:", ["Thermal", "Visual"])
feedback_text = st.text_area("Describe your experience:", value=st.session_state["feedback_text"], key="feedback_text")
room = st.text_input("Room Number:", value=st.session_state["room"])
user_id = st.text_input("User ID:", value=st.session_state["user_id"])

# --- Submit Button ---
if st.button("Submit Feedback"):
    if feedback_text.strip() == "":
        st.warning("Please enter or speak your feedback.")
    else:
        data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "feedback_type": feedback_type.lower(),
            "feedback_text": feedback_text.strip(),
            "room": room.strip(),
            "user_id": user_id.strip()
        }
        # Submit to Supabase (optional)
        # try:
        #     supabase.table("feedback").insert(data).execute()
        #     st.success("✅ Feedback submitted successfully!")
        # except Exception as e:
        #     st.error(f"❌ Failed to submit: {e}")
        st.success("✅ Feedback submitted! (locally for now)")
        st.write(data)

        # Clear session state (optional)
        st.session_state["feedback_text"] = ""
        st.session_state["room"] = ""
        st.session_state["user_id"] = ""
