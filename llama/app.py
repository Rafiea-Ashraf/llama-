import logging
import sys
import time
from typing import Optional
import requests
import streamlit as st
from streamlit_chat import message

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)

BASE_API_URL = "https://musaqlain-langflow-hackathon-clearout.hf.space/api/v1/run"
FLOW_ID = "0b93e3c9-b7d0-4769-bd56-e603ec03cc69"

uploaded_doc_url = None

def upload_document_to_service(document_file):
    # Here, implement your logic to upload the document to a storage service
    # and return the URL of the uploaded document.
    pass

def main():
    st.set_page_config(page_title="DocuGenie", page_icon="📚")

    st.markdown("##### Welcome to DocuGenie")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])
    
    # Ensure uploaded document URL is initialized in session state
    if "uploaded_doc_url" not in st.session_state:
        st.session_state.uploaded_doc_url = None

    if prompt := st.chat_input("Ask me anything about your documents!"):
        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "avatar": "https://example.com/user-avatar.png",  # Replace with actual user avatar URL
            }
        )
        # Display user message in chat message container
        with st.chat_message(
            "user",
            avatar="https://example.com/user-avatar.png",  # Replace with actual user avatar URL
        ):
            st.write(prompt)

        # Display assistant response in chat message container
        with st.chat_message(
            "assistant",
            avatar="https://example.com/assistant-avatar.png",  # Replace with actual assistant avatar URL
        ):
            message_placeholder = st.empty()
            with st.spinner(text="Thinking..."):
                assistant_response = generate_response(prompt)
                message_placeholder.write(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_response,
                "avatar": "https://example.com/assistant-avatar.png",  # Replace with actual assistant avatar URL
            }
        )
    
    # Call the document upload component
    document_upload_component()

def document_upload_component():
    global uploaded_doc_url  # Declare the variable as global
    
    st.markdown("### Upload a Document")
    
    uploaded_file = st.file_uploader("Choose a document...", type=["pdf", "docx", "txt", "csv"])
    
    if uploaded_file is not None:
        
        if st.button("Upload"):
            with st.spinner("Uploading..."):
                doc_url = upload_document_to_service(uploaded_file)
                st.session_state.uploaded_doc_url = doc_url

def run_flow(inputs: dict, flow_id: str, tweaks: Optional[dict] = None) -> dict:
    api_url = f"{BASE_API_URL}/{flow_id}"

    payload = {"inputs": inputs}

    if tweaks:
        payload["tweaks"] = tweaks

    response = requests.post(api_url, json=payload)
    
    return response.json()

def generate_response(prompt):
    logging.info(f"question: {prompt}")
    inputs = {"question": prompt}
    
    # Dynamically create TWEAKS dictionary
    tweaks = {
        "ChatInput-PKbEo": {
            "input_value": prompt,
            "sender": "User",
            "sender_name": "User",
            "session_id": "",
            "store_message": True
        },
    }

    if st.session_state.uploaded_doc_url:
        tweaks["FileUploadComponent-DYGG2"] = {
            "AIMLApiKey": "8759623ce0574e56b454933d4e4ee4aa",
            "MaxTokens": 300,
            "model": "gpt-4o",
            "prompt": "Analyze the document",
            "uploaded_file": st.session_state.uploaded_doc_url
        }

    response = run_flow(inputs, flow_id=FLOW_ID, tweaks=tweaks)

    try:
        logging.info(f"answer: {response['outputs'][0]['outputs'][0]['results']['message']['data']['text']}")
        return response['outputs'][0]['outputs'][0]['results']['message']['data']['text']
    except Exception as exc:
        logging.error(f"error: {response}")
        return "Sorry, there was a problem finding an answer for you."

if __name__ == "__main__":
    main()
