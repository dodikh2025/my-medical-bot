import streamlit as st
import requests
import json
from datetime import datetime
import time
import uuid

# Configure the page
st.set_page_config(
    page_title="Medical AI Assistant - Dify",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = "app-nBkI63qeFoHR4urOdmX3ej5S"
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = str(uuid.uuid4())
if 'patient_context' not in st.session_state:
    st.session_state.patient_context = {}
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

class DifyMedicalBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.dify.ai/v1"  # Dify API base URL
        
    def chat_with_dify_bot(self, message, conversation_id=None, user_id="streamlit_user"):
        """
        Send message to Dify medical bot using chat-messages endpoint
        """
        try:
            url = f"{self.base_url}/chat-messages"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Add medical context to the message if available
            enhanced_message = self.enhance_message_with_context(message)
            
            payload = {
                "inputs": {},
                "query": enhanced_message,
                "response_mode": "blocking",
                "conversation_id": conversation_id or st.session_state.conversation_id,
                "user": user_id
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Update conversation ID for continuity
                if 'conversation_id' in data:
                    st.session_state.conversation_id = data['conversation_id']
                
                # Extract the answer from Dify response
                bot_response = data.get('answer', 'Sorry, I could not process your medical query.')
                
                # Add medical disclaimer if not already present
                if "medical advice" not in bot_response.lower() and "disclaimer" not in bot_response.lower():
                    bot_response += "\n\n⚠️ *This information is for educational purposes only and is not a substitute for professional medical advice. Please consult with a healthcare provider for personalized medical guidance.*"
                
                return bot_response
                
            elif response.status_code == 401:
                return "❌ Authentication failed. Please check your Dify API key."
            elif response.status_code == 400:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error_msg = error_data.get('message', 'Bad request to Dify API')
                return f"❌ Request error: {error_msg}"
            else:
                return f"❌ Dify API Error: {response.status_code}. Please try again."
                
        except requests.exceptions.Timeout:
            return "⏱️ Request timed out. The medical bot may be processing a complex query. Please try again."
        except requests.exceptions.RequestException as e:
            return f"🔌 Connection error: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
    
    def get_conversation_messages(self, conversation_id=None, limit=20):
        """
        Get conversation history from Dify
        """
        try:
            url = f"{self.base_url}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "conversation_id": conversation_id or st.session_state.conversation_id,
                "limit": limit
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                return []
                
        except Exception as e:
            st.error(f"Error fetching conversation history: {str(e)}")
            return []
    
    def enhance_message_with_context(self, message):
        """
        Enhance user message with patient context for better medical assistance
        """
        context = st.session_state.patient_context
        
        if not any(context.values()):
            return message
        
        context_parts = []
        
        if context.get('age_range'):
            context_parts.append(f"Patient age range: {context['age_range']}")
        
        if context.get('medical_history'):
            context_parts.append(f"Relevant medical history: {context['medical_history']}")
        
        if context.get('urgency_level') and context['urgency_level'] != "General inquiry":
            context_parts.append(f"Urgency level: {context['urgency_level']}")
        
        if context_parts:
            context_string = " | ".join(context_parts)
            enhanced_message = f"[Medical Context: {context_string}]\n\nUser Query: {message}"
            return enhanced_message
        
        return message

# Initialize the Dify medical bot
@st.cache_resource
def initialize_dify_medical_bot():
    return DifyMedicalBot(st.session_state.api_key)

def main():
    # Header with medical styling
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: #1565c0; margin: 0;'>🏥 Medical AI Assistant</h1>
        <p style='color: #666; margin: 0.5rem 0 0 0;'>Powered by Dify AI - Your healthcare information companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Medical disclaimer banner
    st.warning("""
    ⚠️ **Important Medical Disclaimer**: This AI assistant provides general health information for educational purposes only. 
    It is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of your physician 
    or other qualified health provider with any questions you may have regarding a medical condition.
    """)
    
    # Sidebar for medical context and settings
    with st.sidebar:
        st.header("🔧 Medical Assistant Settings")
        
        # API Configuration
        with st.expander("Dify API Configuration", expanded=False):
            api_key = st.text_input(
                "Dify API Key", 
                value=st.session_state.api_key,
                type="password",
                help="Your Dify medical bot API key (app-xxxxx format)"
            )
            
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                st.rerun()
            
            # Display API status
            if st.session_state.api_key.startswith("app-"):
                st.success("✅ Dify API key format recognized")
            else:
                st.warning("⚠️ Please enter a valid Dify API key (starts with 'app-')")
        
        st.divider()
        
        # Patient Context (Optional)
        st.subheader("👤 Patient Context")
        st.caption("Optional information for better medical assistance")
        
        age_range = st.selectbox(
            "Age Range",
            ["Not specified", "0-18", "19-35", "36-50", "51-65", "65+"],
            help="General age range for age-appropriate information"
        )
        
        medical_history = st.text_area(
            "Relevant Medical History",
            placeholder="Any relevant medical conditions, allergies, or medications (optional)",
            height=100,
            help="This context helps provide more relevant medical information"
        )
        
        urgency_level = st.selectbox(
            "Urgency Level",
            ["General inquiry", "Mild concern", "Moderate concern", "Urgent (seek immediate care)"],
            help="Helps prioritize the type of response"
        )
        
        # Update patient context
        st.session_state.patient_context = {
            "age_range": age_range if age_range != "Not specified" else None,
            "medical_history": medical_history if medical_history else None,
            "urgency_level": urgency_level,
            "session_id": st.session_state.session_id
        }
        
        st.divider()
        
        # Quick Medical Actions
        st.subheader("⚡ Quick Medical Actions")
        
        quick_questions = [
            ("🆘 Emergency Info", "What should I do in a medical emergency and when should I call 911?"),
            ("💊 Medication Help", "I need help understanding my medication, side effects, or drug interactions."),
            ("🩺 Symptom Checker", "I'd like to discuss some symptoms I'm experiencing and understand when to seek care."),
            ("🏥 Find Healthcare", "Help me understand what type of healthcare provider I should see for my condition."),
            ("🧬 Lab Results", "I need help understanding my medical test results or lab values."),
            ("🍎 Health & Wellness", "I want advice on maintaining good health, diet, and lifestyle choices.")
        ]
        
        for icon_text, question in quick_questions:
            if st.button(icon_text, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
        
        # Clear conversation
        st.divider()
        if st.button("🗑️ Clear Conversation", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.session_state.conversation_id = str(uuid.uuid4())
            st.rerun()
        
        # Session Statistics
        st.divider()
        st.subheader("📊 Session Info")
        st.text(f"Session: {st.session_state.session_id[:8]}...")
        st.text(f"Conversation: {st.session_state.conversation_id[:8]}...")
        st.metric("Questions Asked", len([msg for msg in st.session_state.messages if msg["role"] == "user"]))
        st.metric("Responses Given", len([msg for msg in st.session_state.messages if msg["role"] == "assistant"]))
    
    # Main chat interface
    dify_bot = initialize_dify_medical_bot()
    
    # Display chat messages with medical styling
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🏥"):
                    st.markdown(message["content"])
    
    # Chat input with medical context
    if prompt := st.chat_input("Ask me about health, symptoms, medications, or medical concerns..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get Dify medical bot response
        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner("🔄 Medical AI is analyzing your query via Dify..."):
                try:
                    response = dify_bot.chat_with_dify_bot(
                        prompt,
                        st.session_state.conversation_id
                    )
                    
                    st.markdown(response)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = "I apologize, but I encountered a technical issue connecting to the medical AI. Please check your internet connection and try again."
                    st.error(f"Technical Error: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Emergency contact information
    with st.expander("🚨 Emergency Contacts & When to Seek Immediate Care", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Emergency Services:**
            - **US Emergency**: 911
            - **UK Emergency**: 999
            - **EU Emergency**: 112
            - **Poison Control (US)**: 1-800-222-1222
            - **Crisis Text Line**: Text HOME to 741741
            - **Suicide Prevention (US)**: 988
            """)
        
        with col2:
            st.markdown("""
            **Seek Immediate Care For:**
            - Chest pain or difficulty breathing
            - Signs of stroke (F.A.S.T.)
            - Severe bleeding or trauma
            - Loss of consciousness
            - Severe allergic reactions
            - High fever with severe symptoms
            """)
    
    # Dify Integration Info
    with st.expander("ℹ️ About This Medical Assistant", expanded=False):
        st.markdown("""
        **Powered by Dify AI Platform:**
        - This medical assistant uses advanced AI through the Dify platform
        - Conversations are processed securely through Dify's infrastructure
        - The bot maintains conversation context for better medical assistance
        - All responses include appropriate medical disclaimers
        
        **Features:**
        - Patient context awareness
        - Medical history consideration  
        - Urgency level assessment
        - Conversation continuity
        - Emergency guidance
        
        **Your API Key:** `{}`
        """.format(st.session_state.api_key[:15] + "..." if len(st.session_state.api_key) > 15 else st.session_state.api_key))
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            <p>🏥 Medical AI Assistant | Powered by Dify AI | Session: {}</p>
            <p><em>Always consult healthcare professionals for medical decisions</em></p>
        </div>
        """.format(st.session_state.session_id[:8]), 
        unsafe_allow_html=True
    )

# Export conversation for medical records
def export_dify_conversation():
    """Export Dify conversation with medical context for records"""
    if st.session_state.messages:
        conversation_data = {
            "platform": "Dify AI",
            "session_id": st.session_state.session_id,
            "conversation_id": st.session_state.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "patient_context": st.session_state.patient_context,
            "messages": st.session_state.messages,
            "api_key_used": st.session_state.api_key[:15] + "...",
            "disclaimer": "This is an AI-generated conversation via Dify platform for informational purposes only. Not a substitute for professional medical advice."
        }
        return json.dumps(conversation_data, indent=2)
    return None

if __name__ == "__main__":
    main()
