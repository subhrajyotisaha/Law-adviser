import streamlit as st
import speech_recognition as sr
import os
from ask_lawyer import get_chat_response

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kokrajhar Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS (Keeping your original colors)
st.markdown("""
<style>
    .stChatInput {border-radius: 15px;}
    .css-1d391kg {padding-top: 1rem;} 
    .stButton button {width: 100%; border-radius: 8px;}
    
    /* Floating Voice Button Styling to be near bottom */
    .voice-btn-container {
        position: fixed;
        bottom: 80px;
        right: 20px;
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. VOICE TO TEXT FUNCTION ---
def listen_to_mic():
    """Captures audio from the user's microphone and converts it to text."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            status_placeholder = st.empty()
            status_placeholder.info("🎤 Listening... Speak now.")
            
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                status_placeholder.info("⏳ Processing...")
                text = recognizer.recognize_google(audio)
                status_placeholder.empty()
                return text
                
            except sr.WaitTimeoutError:
                status_placeholder.warning("❌ No speech detected.")
                return None
            except sr.UnknownValueError:
                status_placeholder.warning("❌ Could not understand.")
                return None
            except Exception as e:
                status_placeholder.error(f"Error: {e}")
                return None
    except OSError:
        st.error("❌ No Microphone Found!")
        return None

# --- 3. SIDEBAR (Only History Controls Now) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2666/2666505.png", width=80)
    st.title("Case Files")
    
    if st.button("🗑️ Clear History & Start New", type="primary"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.info("💡 **Tip:** Ask about 'Eviction', 'Inheritance', or 'Fraud'.")

# --- 4. MAIN CHAT INTERFACE ---
st.title("⚖️ Kokrajhar Legal Assistant")

# Initialize Session State (This fixes the History Issue)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. INPUT AREA (Voice + Text) ---

# Create a container for the input controls
input_container = st.container()

with input_container:
    # Voice Button - Placed right above the text input
    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("🎤 Voice Input"):
            voice_text = listen_to_mic()
            if voice_text:
                # Add voice text immediately to messages
                st.session_state.messages.append({"role": "user", "content": voice_text})
                # Trigger Rerun to process it
                st.rerun()
    
    # Text Input (Standard Streamlit Chat Input)
    user_input = st.chat_input("Type your legal question here...")

# --- 6. PROCESSING LOGIC ---
# We check if the last message was from the user (Voice or Text) and needs an answer
last_message_is_user = len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user"
# We check if we already answered it (to prevent double answers)
if last_message_is_user:
    # If the last message is user, but we haven't answered yet...
    # (Usually we handle this by appending immediate response, but let's handle the Text Input case first)
    pass

# Handle Standard Text Input
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# --- 7. GENERATE AI RESPONSE ---
# If the last message in history is from 'user', the AI needs to reply
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🧠 *Thinking...*")
        
        try:
            # FIX FOR HISTORY: Rebuild history string dynamically from actual visible messages
            # This ensures the AI sees EXACTLY what is on the screen.
            current_history_list = [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
            
            # Get last user message
            last_user_msg = st.session_state.messages[-1]["content"]
            
            # Call Backend
            full_response = get_chat_response(last_user_msg, current_history_list)
            
            message_placeholder.markdown(full_response)
            
            # Save AI response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            message_placeholder.error(f"❌ Error: {e}")
