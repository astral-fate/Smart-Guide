# streamlit_app.py
import streamlit as st
import os
from openai import OpenAI
import uuid
from datetime import datetime
import json

# Initialize OpenAI client
class OpenAIClient:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_response(self, prompt: str, context: str = None) -> tuple[str, bool]:
        try:
            messages = self._create_messages(prompt, context)
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("OpenAI returned an empty response")
            
            return content, True
                
        except Exception as e:
            error_msg = str(e)
            return error_msg, False
    
    def _create_messages(self, prompt: str, context: str = None) -> list:
        base_prompt = {
            "role": "system",
            "content": """You are a knowledgeable Saudi Arabia tourism expert. 
            Provide detailed recommendations based on the user's preferences.
            Be specific about locations, activities, and cultural considerations.
            Keep responses friendly and informative."""
        }
        
        messages = [base_prompt]
        
        if context:
            messages.append({"role": "system", "content": f"Previous context: {context}"})
        
        messages.append({"role": "user", "content": prompt})
        return messages

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Set page config
st.set_page_config(page_title="Saudi Tourism Assistant", layout="wide")

# Main title
st.title("Saudi Tourism Assistant")

# Sidebar with preferences form
with st.sidebar:
    st.header("Trip Preferences")
    
    location = st.selectbox(
        "Destination",
        ["Riyadh", "Jeddah", "Mecca", "Medina", "AlUla"],
        key="location"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        budget = st.number_input("Budget", min_value=0, value=1000)
    with col2:
        currency = st.selectbox("Currency", ["SAR", "USD", "EUR"])
    
    trip_type = st.selectbox(
        "Trip Type",
        ["Religious", "Entertainment", "Business", "Cultural"],
        key="trip_type"
    )
    
    family = st.text_input("Family Composition (e.g., 2 adults, 1 child)")
    duration = st.number_input("Duration (days)", min_value=1, value=1)
    
    if st.button("Get Recommendations"):
        try:
            client = OpenAIClient()
            initial_prompt = f"""Please provide a personalized travel recommendation for Saudi Arabia based on these preferences:
            Location: {location}
            Budget: {budget} {currency}
            Trip Type: {trip_type}
            Family: {family}
            Duration: {duration} days"""
            
            response, success = client.generate_response(initial_prompt)
            
            if success:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                st.error("Failed to generate recommendations. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Main chat interface
chat_container = st.container()

# Display chat history
with chat_container:
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.text_area("You:", value=message["content"], height=100, disabled=True)
        else:
            st.text_area("Assistant:", value=message["content"], height=200, disabled=True)

# Chat input
user_input = st.text_input("Ask a question about your trip:", key="user_input")

if st.button("Send"):
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        try:
            client = OpenAIClient()
            
            # Get context from recent messages
            recent_messages = st.session_state.chat_history[-5:]
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
            
            response, success = client.generate_response(user_input, context)
            
            if success:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                st.experimental_rerun()
            else:
                st.error("Failed to generate response. Please try again.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# requirements.txt
requirements = """
streamlit==1.31.0
openai==1.53.0
python-dotenv==1.0.0
"""

with open("requirements.txt", "w") as f:
    f.write(requirements)
