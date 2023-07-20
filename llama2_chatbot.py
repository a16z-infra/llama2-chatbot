"""
LLaMA 2 Chatbot app
======================

This is an Streamlit chatbot app with LLaMA2 that includes session chat history and option to select multiple LLM
API enpoints on Replicate. Each model (7B, 13B & 70B) runs on Replicate on one A100 (40Gb). The weights have been tensorized.

Author: Marco Mascorro (@mascobot.com)
Created: July 2023
Version: 0.9.0 (Experimental)
Status: Development
Python version: 3.9.15
a16z-infra
"""
#External libraries:
import streamlit as st
import replicate
from dotenv import load_dotenv
load_dotenv()
import os
from utils import debounce_replicate_run

# feel free to replace with your own logo
logo1 = 'https://storage.googleapis.com/llama2_release/a16z_logo.png'
logo2 = 'https://storage.googleapis.com/llama2_release/replicate_logo_white.png'

###Initial UI configuration:###
st.set_page_config(page_title="LLaMA2 Chatbot by a16z-infra", page_icon=logo1, layout="wide")

# reduce font sizes for input text boxes
custom_css = """
    <style>
        .stTextArea textarea {font-size: 13px;}
        div[data-baseweb="select"] > div {font-size: 13px !important;}
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


st.sidebar.header("LLaMA2 Chatbot")#Left sidebar menu
st.sidebar.markdown('**by a16z Infra**')
st.sidebar.markdown('**(Chatbot UI not associated with Meta Platforms, Inc)**')

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
REPLICATE_MODEL_ENDPOINT70B = os.environ.get('REPLICATE_MODEL_ENDPOINT70B', default='')
PRE_PROMPT = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as Assistant."

if not (REPLICATE_API_TOKEN and REPLICATE_MODEL_ENDPOINT13B and REPLICATE_MODEL_ENDPOINT7B):
    st.warning("Add a `.env` file to your app directory with the keys specified in `.env_template` to continue.")
    st.stop()

#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()
#Set up/Initialize Session State variables:
if 'chat_dialogue' not in st.session_state:
    st.session_state['chat_dialogue'] = []
if 'llm' not in st.session_state:
    #st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT13B
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT70B
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
selected_option = st.sidebar.selectbox('Choose a LLaMA2 model:', ['LLaMA2-70B', 'LLaMA2-13B', 'LLaMA2-7B'], key='model')
if selected_option == 'LLaMA2-7B':
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT7B
elif selected_option == 'LLaMA2-13B':
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT13B
else:
    st.session_state['llm'] = REPLICATE_MODEL_ENDPOINT70B
#Model hyper parameters:
st.session_state['temperature'] = st.sidebar.slider('Temperature:', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
st.session_state['top_p'] = st.sidebar.slider('Top P:', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
st.session_state['max_seq_len'] = st.sidebar.slider('Max Sequence Length:', min_value=64, max_value=4096, value=2048, step=8)

NEW_P = st.sidebar.text_area('Prompt before the chat starts. Edit here if desired:', PRE_PROMPT, height=60)
if NEW_P != PRE_PROMPT and NEW_P != "" and NEW_P != None:
    st.session_state['pre_prompt'] = NEW_P + "\n\n"
else:
    st.session_state['pre_prompt'] = PRE_PROMPT


# Add the "Clear Chat History" button to the sidebar
clear_chat_history_button = st.sidebar.button("Clear Chat History")

# Check if the button is clicked
if clear_chat_history_button:
    # Reset the chat history stored in the session state
    st.session_state['chat_dialogue'] = []
    
    
# add links to relevant resources for users to select
text1 = 'Chatbot Demo Code' 
text2 = 'Model on Replicate' 
text3 = 'LLaMa2 Cog Template'

logo1_link = "https://github.com/a16z-infra/llama2-chatbot"
logo2_link = "https://replicate.com/a16z-infra/llama13b-v2-chat"
text3_link = "https://github.com/a16z-infra/cog-llama-template"

st.sidebar.markdown(f"""
<div class='resources-section'>
    <h3>Resources:</h3>
    <div style="display: flex; justify-content: space-between;">
        <div style="display: flex; flex-direction: column; padding-left: 15px;">
            <div style="align-self: flex-start; padding-bottom: 5px;"> <!-- Change to flex-start here -->
                <a href="{logo1_link}">
                    <img src="{logo1}" alt="Logo 1" style="width: 30px;"/>
                </a>
            </div>
            <div style="align-self: flex-start;">
                <p style="font-size:11px; margin-bottom: -5px;"><a href="{logo1_link}">{text1}</a></p>
                <p style="font-size:11px;"><a href="{text3_link}">{text3}</a></p>  <!-- second line of text -->
            </div>
        </div>
        <div style="display: flex; flex-direction: column; padding-right: 25px;">
            <div style="align-self: flex-start; padding-bottom: 5px;">
                <a href="{logo2_link}">
                    <img src="{logo2}" alt="Logo 2" style="width: 120px;"/>
                </a>
            </div>
            <div style="align-self: flex-start;">
                <p style="font-size:11px;"><a href="{logo2_link}">{text2}</a></p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


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
        output = debounce_replicate_run(st.session_state['llm'], string_dialogue + "Assistant: ",  st.session_state['max_seq_len'], st.session_state['temperature'], st.session_state['top_p'], REPLICATE_API_TOKEN)
        for item in output:
            full_response += item
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.chat_dialogue.append({"role": "assistant", "content": full_response})



