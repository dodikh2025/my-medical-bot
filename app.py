import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure the page
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = "app-nBkI63qeFoHR4urOdmX3ej5S"
if 'patient_context' not in st.session_state:
    st.session_state.patient_context = {}
if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

class MedicalBot:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def chat_with_medical_bot(self, message, conversation_history=None, patient_context=None):
        """
        Send message to medical bot and get response
        """
        try:
            # Method 1: OpenAI API for medical assistance
            return self.openai_medical_call(message, conversation_history, patient_context)
            
        except Exception as e:
            # Method 2: Custom medical API endpoint
            return self.custom_medical_api_call(message, conversation_history, patient_context)
    
    def openai_medical_call(self, message, conversation_history=None, patient_context=None):
        """
        OpenAI API call configured for medical assistance
        """
        try:
            url = "https://api.openai.com/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Medical-specific system prompt
            system_prompt = """You are a professional medical AI assistant. You provide helpful medical information and support healthcare professionals and patients. 

IMPORTANT DISCLAIMERS:
- Always remind users that this is not a substitute for professional medical advice
- Encourage users to consult healthcare professionals for serious concerns
- Do not provide specific diagnoses or treatment recommendations
- Focus on educational information and general guidance
- Be empathetic and supportive while maintaining professional boundaries

Your responses should be:
- Evidence-based and medically accurate
- Clear and easy to understand
- Appropriately cautious about medical recommendations
- Supportive and empathetic"""

            messages = [{"role": "system", "content": system_prompt}]
            
            # Add patient context if available
            if patient_context:
                context_msg = f"Patient context: {json.dumps(patient_context, indent=2)}"
                messages.append({"role": "system", "content": context_msg})
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    messages.append(msg)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 1200,
                "temperature": 0.3,  # Lower temperature for medical accuracy
                "presence_penalty": 0.1
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data['choices'][0]['message']['content']
                
                # Add medical disclaimer if not already present
                if "medical advice" not in bot_response.lower():
                    bot_response += "\n\n⚠️ *This information is for educational purposes only and is not a substitute for professional medical advice. Please consult with a healthcare provider for personalized medical guidance.*"
                
                return bot_response
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_msg = error_data.get('error', {}).get('message', f"API Error: {response.status_code}")
                return f"Medical Bot API Error: {error_msg}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def custom_medical_api_call(self, message, conversation_history=None, patient_context=None):
        """
        Custom medical API endpoint call
        Replace with your specific medical bot API details
        """
        try:
            # Replace with your actual medical bot API endpoint
            api_url = "https://your-medical-bot-api.com/chat"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-Medical-Bot": "true"
            }
            
            payload = {
                "message": message,
                "conversation_id": st.session_state.session_id,
                "patient_context": patient_context or {},
                "history": conversation_history or [],
                "mode": "medical_assistance",
                "safety_level": "high"
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'Sorry, I could not process your medical query.')
            else:
                return f"Medical API Error: {response.status_code} - Please try again or contact support."
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize the medical bot
@st.cache_resource
def initialize_medical_bot():
    return MedicalBot(st.session_state.api_key)

def main():
    # Header with medical styling
    st.markdown("""
    <div style='text-align: center; padding: 1rem; background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: #1565c0; margin: 0;'>🏥 Medical AI Assistant</h1>
        <p style='color: #666; margin: 0.5rem 0 0 0;'>Your AI-powered healthcare information companion</p>
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
        with st.expander("API Configuration", expanded=False):
            api_key = st.text_input(
                "Medical Bot API Key", 
                value=st.session_state.api_key,
                type="password",
                help="Your medical bot API key"
            )
            
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                st.rerun()
        
        st.divider()
        
        # Patient Context (Optional)
        st.subheader("👤 Patient Context")
        st.caption("Optional information to provide better assistance")
        
        age_range = st.selectbox(
            "Age Range",
            ["Not specified", "0-18", "19-35", "36-50", "51-65", "65+"],
            help="General age range for age-appropriate information"
        )
        
        medical_history = st.text_area(
            "Relevant Medical History",
            placeholder="Any relevant medical conditions, allergies, or medications (optional)",
            height=100
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
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆘 Emergency Info", use_container_width=True):
                emergency_msg = "What should I do in a medical emergency?"
                st.session_state.messages.append({"role": "user", "content": emergency_msg})
                st.rerun()
        
        with col2:
            if st.button("💊 Medication Help", use_container_width=True):
                med_msg = "I need help understanding my medication"
                st.session_state.messages.append({"role": "user", "content": med_msg})
                st.rerun()
        
        if st.button("🩺 Symptom Checker", use_container_width=True):
            symptom_msg = "I'd like to discuss some symptoms I'm experiencing"
            st.session_state.messages.append({"role": "user", "content": symptom_msg})
            st.rerun()
        
        if st.button("🏥 Find Healthcare", use_container_width=True):
            healthcare_msg = "Help me find appropriate healthcare services"
            st.session_state.messages.append({"role": "user", "content": healthcare_msg})
            st.rerun()
        
        # Clear conversation
        st.divider()
        if st.button("🗑️ Clear Conversation", use_container_width=True, type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        # Session Statistics
        st.divider()
        st.subheader("📊 Session Info")
        st.text(f"Session ID: {st.session_state.session_id[:8]}...")
        st.metric("Questions Asked", len([msg for msg in st.session_state.messages if msg["role"] == "user"]))
        st.metric("Responses Given", len([msg for msg in st.session_state.messages if msg["role"] == "assistant"]))
    
    # Main chat interface
    medical_bot = initialize_medical_bot()
    
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
        
        # Get medical bot response
        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner("Medical AI is analyzing your query..."):
                try:
                    # Prepare conversation history for context
                    conversation_history = [
                        {"role": msg["role"], "content": msg["content"]} 
                        for msg in st.session_state.messages[:-1]
                    ]
                    
                    response = medical_bot.chat_with_medical_bot(
                        prompt, 
                        conversation_history, 
                        st.session_state.patient_context
                    )
                    
                    st.markdown(response)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"I apologize, but I encountered a technical issue. Please try again or contact support if the problem persists."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Emergency contact information
    with st.expander("🚨 Emergency Contacts", expanded=False):
        st.markdown("""
        **In case of medical emergency:**
        - **Emergency Services**: 911 (US) / 999 (UK) / 112 (EU)
        - **Poison Control**: 1-800-222-1222 (US)
        - **Crisis Text Line**: Text HOME to 741741
        - **National Suicide Prevention Lifeline**: 988 (US)
        
        **When to seek immediate care:**
        - Chest pain or difficulty breathing
        - Signs of stroke (sudden numbness, confusion, trouble speaking)
        - Severe bleeding or trauma
        - Loss of consciousness
        - Severe allergic reactions
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8em;'>
            <p>🏥 Medical AI Assistant | Built with Streamlit | Session: {}</p>
            <p><em>Always consult healthcare professionals for medical decisions</em></p>
        </div>
        """.format(st.session_state.session_id[:8]), 
        unsafe_allow_html=True
    )

# Export conversation for medical records
def export_medical_conversation():
    """Export conversation with medical context for records"""
    if st.session_state.messages:
        conversation_data = {
            "session_id": st.session_state.session_id,
            "timestamp": datetime.now().isoformat(),
            "patient_context": st.session_state.patient_context,
            "messages": st.session_state.messages,
            "disclaimer": "This is an AI-generated conversation for informational purposes only. Not a substitute for professional medical advice."
        }
        return json.dumps(conversation_data, indent=2)
    return None

if __name__ == "__main__":
    main()
