import requests
import streamlit as st
import json
from datetime import datetime

# Configuration
DIFY_API_KEY = "app-ZSuN7aogNY7G9OdIq10sW6Sd"
DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"

# Page configuration
st.set_page_config(
    page_title="Dify AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .assistant-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

def send_message_to_dify(question, conversation_id=""):
    """Send message to Dify API and return response"""
    headers = {
        'Authorization': f'Bearer {DIFY_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Try with 'question' parameter first (as indicated by the error)
    payload = {
        "inputs": {},
        "question": question,
        "response_mode": "blocking",
        "user": st.session_state.get("user_id", "streamlit_user")
    }
    
    # Only add conversation_id if it exists
    if conversation_id:
        payload["conversation_id"] = conversation_id
    
    try:
        response = requests.post(DIFY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            # Try alternative payload formats
            try:
                error_details = e.response.json()
                st.write("Debug - First attempt error:", error_details)
                
                # Try with 'query' instead
                payload_alt = payload.copy()
                payload_alt["query"] = payload_alt.pop("question")
                
                st.write("Debug - Trying with 'query' parameter...")
                response = requests.post(DIFY_API_URL, headers=headers, json=payload_alt, timeout=30)
                response.raise_for_status()
                return response.json(), None
                
            except requests.exceptions.HTTPError as e2:
                # Try completions endpoint instead
                try:
                    st.write("Debug - Trying completions endpoint...")
                    completions_url = "https://api.dify.ai/v1/completions"
                    payload_completions = {
                        "inputs": {},
                        "query": question,
                        "response_mode": "blocking",
                        "user": st.session_state.get("user_id", "streamlit_user")
                    }
                    
                    response = requests.post(completions_url, headers=headers, json=payload_completions, timeout=30)
                    response.raise_for_status()
                    return response.json(), None
                    
                except requests.exceptions.RequestException as e3:
                    error_msg = f"All API attempts failed. Last error: {str(e3)}"
                    if hasattr(e3, 'response') and e3.response is not None:
                        try:
                            error_details = e3.response.json()
                            error_msg += f"\nDetails: {error_details}"
                        except:
                            error_msg += f"\nResponse: {e3.response.text}"
                    return None, error_msg
        
        # Handle other HTTP errors
        error_msg = f"HTTP Error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                error_msg += f"\nDetails: {error_details}"
            except:
                error_msg += f"\nResponse: {e.response.text}"
        return None, error_msg
        
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        error_msg = f"API Error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                error_msg += f"\nDetails: {error_details}"
            except:
                error_msg += f"\nResponse: {e.response.text}"
        return None, error_msg

def display_chat_history():
    """Display chat history with custom styling"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🤖 {message["content"]}</div>', 
                       unsafe_allow_html=True)

def clear_chat_history():
    """Clear chat history and reset conversation"""
    st.session_state.messages = []
    st.session_state.conversation_id = ""
    st.session_state.total_tokens = 0
    st.rerun()

def main():
    # Initialize session state
    initialize_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🤖 Dify AI Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar for settings and info
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # User ID input
        user_id = st.text_input("User ID", value=st.session_state.get("user_id", "streamlit_user"))
        st.session_state.user_id = user_id
        
        # API status
        st.header("📊 Status")
        if st.session_state.conversation_id:
            st.success(f"🔗 Connected")
            st.info(f"Conversation ID: {st.session_state.conversation_id[:8]}...")
        else:
            st.info("🆕 New conversation")
        
        st.metric("Messages", len(st.session_state.messages))
        if st.session_state.total_tokens > 0:
            st.metric("Tokens Used", st.session_state.total_tokens)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            clear_chat_history()
        
        # Export chat
        if st.session_state.messages:
            chat_export = {
                "conversation_id": st.session_state.conversation_id,
                "messages": st.session_state.messages,
                "timestamp": datetime.now().isoformat()
            }
            st.download_button(
                "📥 Export Chat",
                data=json.dumps(chat_export, indent=2),
                file_name=f"dify_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat container
        chat_container = st.container()
        with chat_container:
            if st.session_state.messages:
                display_chat_history()
            else:
                st.info("👋 Welcome! Ask me anything to get started.")
        
        # Chat input
        prompt = st.chat_input("Type your message here...", key="chat_input")
        
        if prompt:
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Show user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Show assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                
                # Show loading spinner
                with st.spinner("🤔 Thinking..."):
                    response_data, error = send_message_to_dify(
                        prompt, 
                        st.session_state.conversation_id
                    )
                
                if error:
                    st.error(f"❌ {error}")
                    full_response = "Sorry, I encountered an error. Please try again."
                elif response_data:
                    # Extract response data
                    full_response = response_data.get('answer', 'No response received')
                    
                    # Update conversation ID
                    new_conversation_id = response_data.get('conversation_id', '')
                    if new_conversation_id:
                        st.session_state.conversation_id = new_conversation_id
                    
                    # Update token usage if available
                    metadata = response_data.get('metadata', {})
                    usage = metadata.get('usage', {})
                    if 'total_tokens' in usage:
                        st.session_state.total_tokens += usage['total_tokens']
                else:
                    full_response = "No response received from the API."
                
                # Display the response
                message_placeholder.markdown(full_response)
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })
    
    with col2:
        # Quick actions or additional info
        st.header("🚀 Quick Actions")
        
        sample_questions = [
            "Hello! How can you help me?",
            "What's the weather like?",
            "Tell me a joke",
            "Explain artificial intelligence"
        ]
        
        st.write("**Try these questions:**")
        for question in sample_questions:
            if st.button(question, key=f"sample_{hash(question)}", use_container_width=True):
                # Simulate clicking the chat input
                st.session_state.sample_question = question
                st.rerun()
        
        # Handle sample question selection
        if hasattr(st.session_state, 'sample_question'):
            question = st.session_state.sample_question
            del st.session_state.sample_question
            
            # Process the sample question
            st.session_state.messages.append({"role": "user", "content": question})
            
            with st.spinner("🤔 Thinking..."):
                response_data, error = send_message_to_dify(
                    question, 
                    st.session_state.conversation_id
                )
            
            if not error and response_data:
                full_response = response_data.get('answer', 'No response received')
                new_conversation_id = response_data.get('conversation_id', '')
                if new_conversation_id:
                    st.session_state.conversation_id = new_conversation_id
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": full_response
                })
            
            st.rerun()

if __name__ == "__main__":
    main()
