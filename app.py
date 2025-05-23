import streamlit as st
import openai
import requests
import json
from datetime import datetime
import time

# Configure the page
st.set_page_config(
    page_title="DFY Bot Assistant",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = "app-nBkI63qeFoHR4urOdmX3ej5S"

class DFYBot:
    def __init__(self, api_key):
        self.api_key = api_key
        # If using OpenAI API
        openai.api_key = api_key
        
    def chat_with_bot(self, message, conversation_history=None):
        """
        Send message to DFY bot and get response
        """
        try:
            # Method 1: Using OpenAI API (if your bot uses OpenAI)
            messages = [
                {"role": "system", "content": "You are a helpful DFY (Done For You) assistant that helps users with various tasks and questions."}
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or gpt-4 if available
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Method 2: Custom API endpoint (uncomment and modify if needed)
            return self.custom_api_call(message, conversation_history)
    
    def custom_api_call(self, message, conversation_history=None):
        """
        Alternative method for custom API endpoints
        Modify the URL and payload according to your bot's API specification
        """
        try:
            # Replace with your actual API endpoint
            api_url = "https://your-dfy-bot-api.com/chat"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "message": message,
                "conversation_id": st.session_state.get('conversation_id', None),
                "history": conversation_history or []
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'Sorry, I could not process your request.')
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize the bot
@st.cache_resource
def initialize_bot():
    return DFYBot(st.session_state.api_key)

# Main app
def main():
    st.title("🤖 DFY Bot Assistant")
    st.markdown("### Your AI-Powered Done For You Assistant")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input (pre-filled with your key)
        api_key = st.text_input(
            "API Key", 
            value=st.session_state.api_key,
            type="password",
            help="Your DFY Bot API Key"
        )
        
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            st.rerun()
        
        st.divider()
        
        # Bot settings
        st.subheader("Bot Settings")
        bot_mode = st.selectbox(
            "Bot Mode",
            ["General Assistant", "Task Helper", "Content Creator", "Business Advisor"],
            help="Select the type of assistance you need"
        )
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Session Stats")
        st.metric("Messages Sent", len([msg for msg in st.session_state.messages if msg["role"] == "user"]))
        st.metric("Responses Received", len([msg for msg in st.session_state.messages if msg["role"] == "assistant"]))
    
    # Main chat interface
    bot = initialize_bot()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("DFY Bot is thinking..."):
                try:
                    # Prepare conversation history for context
                    conversation_history = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in st.session_state.messages[:-1]  # Exclude the current message
                    ]
                    
                    response = bot.chat_with_bot(prompt, conversation_history)
                    st.markdown(response)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Powered by DFY Bot | Built with Streamlit</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

# Additional utility functions
def export_conversation():
    """Export conversation to JSON file"""
    if st.session_state.messages:
        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages
        }
        return json.dumps(conversation_data, indent=2)
    return None

def load_conversation(uploaded_file):
    """Load conversation from uploaded JSON file"""
    try:
        data = json.load(uploaded_file)
        if "messages" in data:
            st.session_state.messages = data["messages"]
            return True
    except Exception as e:
        st.error(f"Error loading conversation: {str(e)}")
    return False

# Advanced features (uncomment to enable)
"""
# File upload capability
def handle_file_upload():
    uploaded_file = st.file_uploader(
        "Upload a file for the bot to analyze",
        type=['txt', 'pdf', 'docx', 'csv']
    )
    
    if uploaded_file is not None:
        # Process the file based on type
        file_content = process_uploaded_file(uploaded_file)
        return file_content
    return None

def process_uploaded_file(uploaded_file):
    # Add file processing logic here
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode('utf-8')
    # Add more file type handlers as needed
    return "File uploaded successfully"
"""
