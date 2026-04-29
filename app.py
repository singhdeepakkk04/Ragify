import streamlit as st
import requests
import json
import os

# --- Configuration ---
st.set_page_config(page_title="RAGify Chatbot", page_icon="🤖")
st.title("🤖 RAGify Chatbot")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    api_url = st.text_input("RAGify API URL", value="http://localhost:8000/api/v1/rag/query")
    api_key = st.text_input("Project API Key", type="password", help="Get this from your RAGify Project Dashboard")
    project_id = st.number_input("Project ID", min_value=1, value=1)
    
    st.markdown("---")
    st.markdown("Powered by **RAGify**")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("Sources"):
                for idx, citation in enumerate(message["citations"]):
                    st.markdown(f"**[{idx+1}] {citation.get('filename', 'Unknown')}**")
                    st.caption(f"\"{citation.get('snippet', '')}\"")

# React to user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    if not api_key:
        st.error("Please provide an API Key in the sidebar.")
        st.stop()

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        citations_placeholder = st.empty()
        
        full_response = ""
        citations = []
        
        try:
            # Send streaming request to RAGify backend
            headers = {
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "project_id": project_id,
                "query": prompt
            }
            
            with requests.post(api_url, json=payload, headers=headers, stream=True) as response:
                if response.status_code != 200:
                    st.error(f"Error {response.status_code}: {response.text}")
                    st.stop()
                    
                # Process the NDJSON stream
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            
                            # Handle citations
                            if "citations" in data:
                                citations = data["citations"]
                                
                            # Handle tokens
                            if "token" in data:
                                full_response += data["token"]
                                message_placeholder.markdown(full_response + "▌")
                                
                        except json.JSONDecodeError:
                            continue
                            
            # Final update without the cursor
            message_placeholder.markdown(full_response)
            
            # Display citations if any
            if citations:
                with citations_placeholder.expander("Sources"):
                    for idx, citation in enumerate(citations):
                        st.markdown(f"**[{idx+1}] {citation.get('filename', 'Unknown')}**")
                        st.caption(f"\"{citation.get('snippet', '')}\"")
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            full_response = "Sorry, I encountered an error while processing your request."
            
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "citations": citations
        })
