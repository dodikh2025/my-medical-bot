import requests
import streamlit as st 

dify_api_key ="app-LqxTQOfPzxKyYIR22Ys5V39A"

url="https://api.dify.ai/v1/chat-messages"
st.title( "Dify streamlit App")

if "conversation_id" not in st.session_state:
     st.session_state.conversation_id=""

if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:
   with st.chat_message(message["role"]):
      st.markdown(message["content"])

prompt= st.chat_input("Enter your question")

if prompt:
     with st.chat_messages("user"):
        st.markdown(prompt)
     st.session_state.essages.append({"role": "user", "content": prompt})

with st.chat_message("assistant"):
     message_placeholder= st.empt()
     
       headers={
               'Authorization':  f'Bearer {dify_api_key}',
               'content-Type': 'application/json'

      }
      
      playload ={
             "inputs":{}
             "query": prompt,
             "response_mode": "blocking",
             "conversation_id: st.session_state.conversation_id,
             "user": "aianytime",
             "files":[]
}

try:
   response=request.post(url, heasers=headers, json=paload)
   response.raise_for_status()
   response_data = response.json()

  full_response = response_data.get('answer','')
  new_conversation_id = response_data.get('conversation_id', st.session_state.conversation
  st.session_state.conversation_id = new_conversaion_id
except requests.exceptions.RequestsException as e:
  st.error(f"An error occurred: {e}")
  full_response = "An error occurred while fetching the response."
message_placeholder.markdown(full_response)
st.session_state.messages.append({"role":"assistant", "content": full_response})

