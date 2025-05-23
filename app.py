import requests
import streamlit as st
import json
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "patient_context" not in st.session_state:
    st.session_state.patient_context = {}

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# Configuration
DIFY_API_KEY = "app-LqxTQOfPzxKyYIR22Ys5V39A"
DIFY_URL = "https://api.dify.ai/v1/chat-messages"

def send_message_to_dify(prompt, conversation_id=""):
    """Send message to Dify API and return response"""
    headers = {
        'Authorization': f'Bearer {DIFY_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Enhance prompt with patient context if available
    enhanced_prompt = enhance_prompt_with_context(prompt)
    
    payload = {
        "inputs": {},
        "query": enhanced_prompt,
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": f"medical_patient_{st.session_state.session_id}",
        "files": []
    }
    
    try:
        with st.spinner("🔄 Medical AI is analyzing your query..."):
            response = requests.post(DIFY_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()
            
            if 'answer' not in response_data:
                return "I apologize, but I couldn't process your medical query. Please try again.", conversation_id
            
            answer = response_data.get('answer', '')
            new_conversation_id = response_data.get('conversation_id', conversation_id)
            
            # Add medical disclaimer if discussing health topics
            if is_medical_query(prompt):
                answer = add_medical_disclaimer(answer)
            
            return answer, new_conversation_id
            
    except requests.exceptions.Timeout:
        return "⏱️ The request timed out. The medical AI may be processing a complex query. Please try again.", conversation_id
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {e}")
        return "🔌 I'm having trouble connecting to the medical AI service. Please check your connection and try again.", conversation_id
    except Exception as e:
        st.error(f"Unexpected Error: {e}")
        return "❌ An unexpected error occurred. Please try again or contact support.", conversation_id

def enhance_prompt_with_context(prompt):
    """Add patient context to prompt for better medical responses"""
    context = st.session_state.patient_context
    
    if not any(context.values()):
        return prompt
    
    context_parts = []
    
    if context.get('age_range'):
        context_parts.append(f"Age: {context['age_range']}")
    
    if context.get('gender'):
        context_parts.append(f"Gender: {context['gender']}")
    
    if context.get('symptoms'):
        context_parts.append(f"Current symptoms: {context['symptoms']}")
    
    if context.get('medical_history'):
        context_parts.append(f"Medical history: {context['medical_history']}")
    
    if context.get('medications'):
        context_parts.append(f"Current medications: {context['medications']}")
    
    if context.get('urgency'):
        context_parts.append(f"Urgency level: {context['urgency']}")
    
    if context_parts:
        context_string = " | ".join(context_parts)
        return f"[Patient Context: {context_string}]\n\nPatient Question: {prompt}"
    
    return prompt

def is_medical_query(prompt):
    """Check if the query is medical-related"""
    medical_keywords = [
        'symptom', 'pain', 'ache', 'sick', 'ill', 'disease', 'condition', 'treatment',
        'medication', 'medicine', 'doctor', 'hospital', 'health', 'medical', 'diagnosis',
        'fever', 'headache', 'nausea', 'cough', 'infection', 'allergy', 'blood', 'heart'
    ]
    return any(keyword in prompt.lower() for keyword in medical_keywords)

def add_medical_disclaimer(response):
    """Add medical disclaimer to health-related responses"""
    if "disclaimer" not in response.lower() and "medical advice" not in response.lower():
        disclaimer = "\n\n⚠️ **Medical Disclaimer**: This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns."
        response += disclaimer
    return response

def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; margin-bottom: 2rem; color: white;'>
        <h1 style='margin: 0; font-size: 2.5rem;'>🏥 Medical AI Assistant</h1>
        <p style='margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;'>Powered by Dify AI Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Medical disclaimer banner
    st.error("""
    🚨 **IMPORTANT MEDICAL DISCLAIMER**: This AI provides general health information for educational purposes only. 
    It is NOT a substitute for professional medical advice. For medical emergencies, call emergency services immediately.
    Always consult healthcare professionals for medical decisions.
    """)
    
    # Sidebar for patient context and settings
    with st.sidebar:
        st.header("👤 Patient Information")
        
        # Patient context form
        with st.form("patient_context_form"):
            st.subheader("📋 Medical Context (Optional)")
            st.caption("Providing context helps get more relevant medical information")
            
            age_range = st.selectbox(
                "Age Range",
                ["Select age", "0-12 (Child)", "13-17 (Teen)", "18-30 (Young Adult)", 
                 "31-50 (Adult)", "51-65 (Middle Age)", "65+ (Senior)"]
            )
            
            gender = st.selectbox(
                "Gender",
                ["Prefer not to say", "Male", "Female", "Other"]
            )
            
            symptoms = st.text_area(
                "Current Symptoms",
                placeholder="Describe any symptoms you're experiencing...",
                height=80
            )
            
            medical_history = st.text_area(
                "Relevant Medical History",
                placeholder="Any chronic conditions, past surgeries, family history...",
                height=80
            )
            
            medications = st.text_area(
                "Current Medications",
                placeholder="List any medications, supplements, or treatments...",
                height=60
            )
            
            urgency = st.selectbox(
                "How urgent is your concern?",
                ["General question", "Minor concern", "Moderate concern", "Serious concern", "Emergency"]
            )
            
            submitted = st.form_submit_button("💾 Update Medical Context", use_container_width=True)
            
            if submitted:
                st.session_state.patient_context = {
                    "age_range": age_range if age_range != "Select age" else None,
                    "gender": gender if gender != "Prefer not to say" else None,
                    "symptoms": symptoms if symptoms else None,
                    "medical_history": medical_history if medical_history else None,
                    "medications": medications if medications else None,
                    "urgency": urgency if urgency != "General question" else None
                }
                st.success("✅ Medical context updated!")
        
        st.divider()
        
        # Quick medical questions
        st.subheader("⚡ Quick Medical Questions")
        
        quick_questions = [
            ("🆘 Emergency Guide", "What should I do in a medical emergency and when should I call 911?"),
            ("💊 Medication Info", "I need information about a medication, its uses, and potential side effects."),
            ("🩺 Symptom Checker", "I have some symptoms and want to understand what they might indicate."),
            ("🏥 Healthcare Navigation", "Help me understand what type of healthcare provider I should see."),
            ("🧪 Test Results", "I need help understanding my medical test results or lab values."),
            ("💪 Health & Wellness", "I want advice on maintaining good health and preventing illness."),
            ("🤰 Women's Health", "I have questions about women's health, pregnancy, or reproductive health."),
            ("👶 Child Health", "I need information about child health, pediatric care, or development.")
        ]
        
        for button_text, question in quick_questions:
            if st.button(button_text, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.rerun()
        
        st.divider()
        
        # Session management
        st.subheader("🔧 Session Management")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_id = ""
                st.rerun()
        
        with col2:
            if st.button("🔄 New Session", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_id = ""
                st.session_state.patient_context = {}
                st.session_state.session_id = str(uuid.uuid4())[:8]
                st.rerun()
        
        # Session info
        st.divider()
        st.subheader("📊 Session Information")
        st.text(f"Session ID: {st.session_state.session_id}")
        st.text(f"Conversation ID: {st.session_state.conversation_id[:8]}..." if st.session_state.conversation_id else "New conversation")
        st.metric("Questions Asked", len([m for m in st.session_state.messages if m["role"] == "user"]))
        st.metric("AI Responses", len([m for m in st.session_state.messages if m["role"] == "assistant"]))
        
        # Context status
        context_count = sum(1 for v in st.session_state.patient_context.values() if v)
        if context_count > 0:
            st.success(f"✅ {context_count} context field(s) provided")
        else:
            st.info("ℹ️ No medical context provided")
    
    # Main chat interface
    st.subheader("💬 Chat with Medical AI")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🏥"):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about health, symptoms, medications, or medical concerns...", key="main_chat_input"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🏥"):
            message_placeholder = st.empty()
            
            # Send to Dify API
            full_response, new_conversation_id = send_message_to_dify(prompt, st.session_state.conversation_id)
            
            # Update conversation ID
            st.session_state.conversation_id = new_conversation_id
            
            # Display response
            message_placeholder.markdown(full_response)
            
            # Add to session state
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Emergency information footer
    with st.expander("🚨 Emergency Information & When to Seek Immediate Care"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🚨 Emergency Numbers:**
            - **Emergency Services**: 911 (US), 999 (UK), 112 (EU)
            - **Poison Control**: 1-800-222-1222 (US)
            - **Crisis Text Line**: Text HOME to 741741
            - **Suicide Prevention**: 988 (US)
            """)
        
        with col2:
            st.markdown("""
            **⚠️ Seek Immediate Care For:**
            - Chest pain or trouble breathing
            - Signs of stroke (F.A.S.T. test)
            - Severe bleeding or injuries
            - Loss of consciousness
            - Severe allergic reactions
            - Thoughts of self-harm
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
            <p>🏥 Medical AI Assistant powered by Dify AI | Session: {st.session_state.session_id}</p>
            <p><em>Always consult healthcare professionals for medical decisions and emergencies</em></p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
