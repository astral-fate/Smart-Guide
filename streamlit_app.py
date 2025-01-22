import streamlit as st
import os
from datetime import datetime
import uuid
from openai import OpenAI

# Initialize OpenAI client
class OpenAIClient:
    def __init__(self):
        self.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OpenAI API key not found in environment variables or Streamlit secrets")
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_response(self, prompt: str, context: str = None) -> tuple[str, bool]:
        """Generate a response using the OpenAI API"""
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
        """Create messages for the OpenAI API"""
        base_prompt = {
            "role": "system",
            "content": """You are a knowledgeable Saudi Arabia tourism expert. 
            Provide detailed recommendations based on the user's preferences.
            Be specific about locations, activities, and cultural considerations.
            Keep responses friendly and informative.
            
            Important guidelines:
            1. Focus on practical recommendations
            2. Include cultural sensitivity tips
            3. Suggest specific places and activities
            4. Mention estimated costs when relevant
            5. Include safety tips and best times to visit"""
        }
        
        messages = [base_prompt]
        
        if context:
            messages.append({"role": "system", "content": f"Previous context: {context}"})
        
        messages.append({"role": "user", "content": prompt})
        return messages

# Set page configuration
st.set_page_config(
    page_title="Saudi Tourism Assistant",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Main title and description
st.title("🌴 Saudi Tourism Assistant")
st.markdown("""
    Welcome to your personal Saudi Arabia travel planner! Get customized recommendations 
    based on your preferences and ask questions about your upcoming trip.
""")

# Initialize OpenAI client
try:
    client = OpenAIClient()
except Exception as e:
    st.error(f"Failed to initialize AI service: {str(e)}")
    st.stop()

# Sidebar with preferences form
with st.sidebar:
    st.header("✈️ Trip Preferences")
    
    with st.form("trip_preferences"):
        location = st.selectbox(
            "📍 Destination",
            ["Riyadh", "Jeddah", "Mecca", "Medina", "AlUla"],
            key="location"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            budget = st.number_input("💰 Budget", min_value=0, value=1000)
        with col2:
            currency = st.selectbox("Currency", ["SAR", "USD", "EUR"])
        
        trip_type = st.selectbox(
            "🎯 Trip Type",
            ["Religious", "Entertainment", "Business", "Cultural"],
            key="trip_type"
        )
        
        family = st.text_input("👨‍👩‍👦 Family Composition (e.g., 2 adults, 1 child)")
        duration = st.number_input("📅 Duration (days)", min_value=1, value=1)
        
        submitted = st.form_submit_button("Get Recommendations")
        
        if submitted:
            with st.spinner("Generating recommendations..."):
                initial_prompt = f"""Please provide a personalized travel recommendation for Saudi Arabia based on these preferences:
                Location: {location}
                Budget: {budget} {currency}
                Trip Type: {trip_type}
                Family: {family}
                Duration: {duration} days
                
                Please include:
                1. Suggested itinerary
                2. Accommodation recommendations
                3. Must-visit attractions
                4. Local customs and etiquette
                5. Budget breakdown
                6. Travel tips"""
                
                response, success = client.generate_response(initial_prompt)
                
                if success:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    st.success("Recommendations generated!")
                else:
                    st.error("Failed to generate recommendations. Please try again.")

# Main chat interface
st.header("💭 Chat with Your Travel Assistant")

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong><br>{message["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong><br>{message["content"]}
            </div>
        """, unsafe_allow_html=True)

# Chat input
with st.container():
    user_input = st.text_area("Ask a question about your trip:", height=100, key="user_input")
    
    if st.button("Send", key="send_button"):
        if user_input:
            with st.spinner("Generating response..."):
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
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

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <small>Saudi Tourism Assistant - Your personal guide to exploring Saudi Arabia</small>
    </div>
""", unsafe_allow_html=True)
