import streamlit as st
import requests
import uuid
from dotenv import load_dotenv
import os

# Initialize session state for chat history and session ID
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Webhook configuration
WEBHOOK_URL = "https://diamenciarz.app.n8n.cloud/webhook/invoke_agent"  # Replace with your n8n webhook URL
# Load environment variables from .env file
load_dotenv()

# Import from env
BEARER_TOKEN = "TestCreds99@@" # os.getenv("BEARER_TOKEN")

# Streamlit app title
# Add a fixed title to the top left corner
st.markdown(
    """
    <style>
    .fixed-title {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        z-index: 1000;
        border-bottom: 1px solid #ddd;
    }
    .stApp {
        margin-top: 60px;
    }
    header, footer {
        visibility: hidden;
    }
    </style>
    <div class="fixed-title">
        <h1>Le Kahdo | (Alpha Test)</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare payload for webhook
    payload = {
        "sessionId": st.session_state.session_id,
        "chatInput": prompt
    }

    # Send request to webhook
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse response
        response_data = response.json()
        llm_response = response_data.get("output", "No response from LLM")
        
        # Add LLM response to chat history
        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.markdown(llm_response)
            
    except requests.exceptions.RequestException as e:
        error_message = f"Error communicating with LLM: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        with st.chat_message("assistant"):
            st.markdown(error_message)