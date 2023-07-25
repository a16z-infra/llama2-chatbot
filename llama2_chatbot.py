"""
LLaMA 2 Chatbot app
======================

This is a Streamlit chatbot app with LLaMA2 that includes session chat history and an option to select multiple LLM
API endpoints on Replicate. The 7B and 13B models run on Replicate on one A100 40Gb. The 70B runs in one A100 80Gb. The weights have been tensorized.

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
from auth0_component import login_button

###Global variables:###
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN', default='')
#Your your (Replicate) models' endpoints:
REPLICATE_MODEL_ENDPOINT7B = os.environ.get('REPLICATE_MODEL_ENDPOINT7B', default='')
REPLICATE_MODEL_ENDPOINT13B = os.environ.get('REPLICATE_MODEL_ENDPOINT13B', default='')
REPLICATE_MODEL_ENDPOINT70B = os.environ.get('REPLICATE_MODEL_ENDPOINT70B', default='')
PRE_PROMPT = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as Assistant."
#Auth0 for auth
AUTH0_CLIENTID = os.environ.get('AUTH0_CLIENTID', default='')
AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', default='')

if not (REPLICATE_API_TOKEN and REPLICATE_MODEL_ENDPOINT13B and REPLICATE_MODEL_ENDPOINT7B and 
        AUTH0_CLIENTID and AUTH0_DOMAIN):
    st.warning("Add a `.env` file to your app directory with the keys specified in `.env_template` to continue.")
    st.stop()

###Initial UI configuration:###
st.set_page_config(page_title="LLaMA2 Chatbot by a16z-infra", page_icon="🦙", layout="wide")

def render_app():

    # reduce font sizes for input text boxes
    custom_css = """
        <style>
            .stTextArea textarea {font-size: 13px;}
            div[data-baseweb="select"] > div {font-size: 13px !important;}
        </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    #Left sidebar menu
    st.sidebar.header("LLaMA2 Chatbot")

    #Set config for a cleaner menu, footer & background:
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

    btn_col1, btn_col2 = st.sidebar.columns(2)

    # Add the "Clear Chat History" button to the sidebar
    def clear_history():
        st.session_state['chat_dialogue'] = []
    clear_chat_history_button = btn_col1.button("Clear History",
                                            use_container_width=True,
                                            on_click=clear_history)

    # add logout button
    def logout():
        del st.session_state['user_info']
    logout_button = btn_col2.button("Logout",
                                use_container_width=True,
                                on_click=logout)
        
    # add links to relevant resources for users to select
    st.sidebar.write(" ")

    text1 = 'Chatbot Demo Code' 
    text2 = 'LLaMA2 70B Model on Replicate' 
    text3 = 'LLaMa2 Cog Template'

    text1_link = "https://github.com/a16z-infra/llama2-chatbot"
    text2_link = "https://replicate.com/replicate/llama70b-v2-chat"
    text3_link = "https://github.com/a16z-infra/cog-llama-template"

    logo1 = 'https://storage.googleapis.com/llama2_release/a16z_logo.png'
    logo2 = 'https://storage.googleapis.com/llama2_release/Screen%20Shot%202023-07-21%20at%2012.34.05%20PM.png'

    st.sidebar.markdown(
        "**Resources**  \n"
        f"<img src='{logo2}' style='height: 1em'> [{text2}]({text2_link})  \n"
        f"<img src='{logo1}' style='height: 1em'> [{text1}]({text1_link})  \n"
        f"<img src='{logo1}' style='height: 1em'> [{text3}]({text3_link})",
        unsafe_allow_html=True)

    st.sidebar.write(" ")
    st.sidebar.markdown("*Made with ❤️ by a16z Infra and Replicate. Not associated with Meta Platforms, Inc.*")

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


if 'user_info' in st.session_state:
# if user_info:
    render_app()
else:
    st.write("Please login to use the app. This is just to prevent abuse, we're not charging for usage.")
    st.session_state['user_info'] = login_button(AUTH0_CLIENTID, domain = AUTH0_DOMAIN)
