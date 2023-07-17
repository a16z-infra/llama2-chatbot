"""
LLaMA 2 Chatbot app
======================

This is an Streamlit chatbot app with LLaMA2 that includes session chat history and option to select multiple LLM
API enpoints on Replicate. Each model (7B & 13B) runs on Replicate on one A100 (40Gb). The weights have been tensorized.

Author: Marco Mascorro (@mascobot.com)
Created: July 2023
Version: 0.9.0
Status: Development
Python version: 3.9.15
a16z-infra
"""
#External libraries:
import streamlit as st
import os
import replicate
###Initial UI configuration:###
st.set_page_config(page_title="LLaMA2 Chatbot by a16z-infra", page_icon="🧊", layout="wide")
st.sidebar.header("LLaMA2 Chatbot")#Left sidebar menu
st.sidebar.markdown('**by a16z Infra**')
#Set config for a cleaner menu, footer & background:
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

###Global variables:###
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN', default='')
#Your your (Replicate) models' endpoints:
REPLICATE_MODEL_ENDPOINT7B = os.environ.get('REPLICATE_MODEL_ENDPOINT7B', default='')
REPLICATE_MODEL_ENDPOINT13B = os.environ.get('REPLICATE_MODEL_ENDPOINT13B', default='')
PRE_PROMPT = "A dialog, where user interacts with an assistant. Assistant is helpful, kind, obedient, honest, and knows its own limits.\n\n"
#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()
#Set up/Initialize Session State variables:
if 'chat_dialogue' not in st.session_state:
    st.session_state['chat_dialogue'] = []
if 'llm' not in st.session_state:
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT13B
if 'temperature' not in st.session_state:
    st.session_state['temperature'] = 0.1
if 'top_p' not in st.session_state:
    st.session_state['top_p'] = 0.9
if 'max_seq_len' not in st.session_state:
    st.session_state['max_seq_len'] = 512
if 'pre_prompt' not in st.session_state:
    st.session_state['pre_prompt'] = PRE_PROMPT
if 'string_dialogue' not in st.session_state:
    st.session_state['string_dialogue'] = ''

#Dropdown menu to select the model edpoint:
selected_option = st.sidebar.selectbox('Choose a LLaMA2 model:', ['LLaMA2-13B', 'LLaMA2-7B'], key='model')
if selected_option == 'LLaMA2-7B':
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT7B
else:
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT13B
#Model hyper parameters:
st.session_state['temperature'] = st.sidebar.slider('Temperature:', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
st.session_state['top_p'] = st.sidebar.slider('Top P:', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
st.session_state['max_seq_len'] = st.sidebar.slider('Max Sequence Length:', min_value=64, max_value=4096, value=2048, step=8)

NEW_P = st.sidebar.text_area('Prompt before the chat starts. Edit here if desired:', PRE_PROMPT, height=130)
if NEW_P != PRE_PROMPT and NEW_P != "" and NEW_P != None:
    st.session_state['pre_prompt'] = NEW_P + "\n\n"
else:
    st.session_state['pre_prompt'] = PRE_PROMPT

# Display chat messages from history on app rerun
for message in st.session_state.chat_dialogue:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type your question here to talk to LLaMA2"):
    # Add user message to chat history
    st.session_state.chat_dialogue.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        string_dialogue = st.session_state['pre_prompt']
        for dict_message in st.session_state.chat_dialogue:
            if dict_message["role"] == "user":
                string_dialogue = string_dialogue + "User: " + dict_message["content"] + "\n\n"
            else:
                string_dialogue = string_dialogue + "Assistant: " + dict_message["content"] + "\n\n"
        print (string_dialogue)
        output = replicate.run(st.session_state['llm'], input={"prompt": string_dialogue + "Assistant: ", "max_length": st.session_state['max_seq_len'], "temperature": st.session_state['temperature'], "top_p": st.session_state['top_p'], "repetition_penalty": 1}, api_token=REPLICATE_API_TOKEN)
        for item in output:
            if "user:" in item.lower():
                break
            else:
                full_response += item
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.chat_dialogue.append({"role": "assistant", "content": full_response})

























