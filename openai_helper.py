import streamlit as st
from openai import OpenAI
import os

class OpenAIClient:
    def __init__(self):
        self.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise Exception("OpenAI API key not found in environment variables or Streamlit secrets")
        
        self.client = OpenAI(
            api_key=self.api_key
        )
    
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
