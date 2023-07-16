"""
LLaMA 2 Chatbot app
======================

This is an Streamlit chatbot app with LLaMA2 that includes session chat history and option to select multiple LLM
API enpoints on Replicate. Each model (7B & 13B) runs on Replicate on one A100 (80Gb). The weights have been tensorized.

Author: Marco Mascorro (@mascobot.com)
Created: July 2023
Version: 0.9.0
Status: Development
Python version: 3.9.15
a16z-infra
"""
#External libraries:
import streamlit as st
from streamlit_chat import message
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
PRE_PROMPT = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as Assistant.\n\n"
MODEL = ''

#Dropdown menu to select the model edpoint:
selected_option = st.sidebar.selectbox('Choose a model:', ['LLaMA2_7B', 'LLaMA2_13B'], key='model')
if selected_option == 'LLaMA2_7B':
    MODEL = REPLICATE_MODEL_ENDPOINT7B
else:
    MODEL = REPLICATE_MODEL_ENDPOINT13B
#Model hyper parameters:
temperature = st.sidebar.slider('Temperature:', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
top_p = st.sidebar.slider('Top P:', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
max_seq_len = st.sidebar.slider('Max Sequence Length:', min_value=50, max_value=4096, value=2048, step=10)

PRE_PROMPT_INPUT = st.sidebar.text_area('Prompt before the chat starts. Edit here if desired:', PRE_PROMPT, height=130)
if len(PRE_PROMPT_INPUT) > 0:
    PRE_PROMPT = PRE_PROMPT_INPUT

#Set up/Initialize Session State variables:
if 'user_messages' not in st.session_state:
    st.session_state['user_messages'] = []
if 'model_response' not in st.session_state:
    st.session_state['model_response'] = []
if 'chat_dialogue' not in st.session_state:
    st.session_state['chat_dialogue'] = ''

def replicate_client(prompt='', max_length=300, temperature=0.1, top_p=0.9, repetition_penalty=1, model=MODEL) -> str:
    output = replicate.run(
        model,
        input={"prompt": prompt, "max_length": max_length, "temperature": temperature, "top_p": top_p, "repetition_penalty": repetition_penalty},
    )
    # The predict method returns an iterator, and you can iterate over that output.
    response_tmp = ''
    for item in output:
        # https://replicate.com/a16z-infra/llama13b-v2-chat/versions/56acad22679f6b95d6e45c78309a2b50a670d5ed29a37dd73d182e89772c02f1/api#output-schema
        #print(item)
        response_tmp = response_tmp + item
    return response_tmp

#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = str(st.text_input("Question:", placeholder="Type your question here to talk to LLaMA2", key='input'))
        submit_button = st.form_submit_button(label='Send')
    if submit_button and user_input:
        if len(user_input) > 0:
            st.session_state['user_messages'].append(user_input)
            #Chat memory implementation:
            # Check if user_messages is longer
            if len(st.session_state['user_messages']) > len(st.session_state['model_response']):
                # Append an empty string to model_responses
                st.session_state['model_response'].append('')
            dialogue = ""
            for user, model in zip(st.session_state['user_messages'], st.session_state['model_response']):
                dialogue += f"User: {user}\n\nAssistant: {model}\n\n"
            if PRE_PROMPT not in dialogue:
                dialogue = PRE_PROMPT + "\n" + dialogue
            print (dialogue)
            st.session_state['model_response'].append(replicate_client(prompt=dialogue, max_length=max_seq_len, temperature=temperature, top_p=top_p))
        st.session_state['model_response'] = list(filter(None, st.session_state['model_response']))#remove empty strings
    #Allow Users to reset the memory
    if st.button("Clear Chat"):
        st.session_state['user_messages'] = []
        st.session_state['model_response'] = []
        st.session_state['chat_dialogue'] = ''
        st.info("Chat memory cleared")

#Populate the chat history:
with response_container:
    if len(st.session_state['user_messages']) > len(st.session_state['model_response']):
        for i in range(len(st.session_state['model_response'])):
            message(st.session_state['user_messages'][i], key=str(i) + '_user', is_user=True, avatar_style="icons", seed=5)
            message(st.session_state['model_response'][i], key=str(i) + '_model', avatar_style="icons", seed=2)
    else:
        for i in range(len(st.session_state['user_messages'])):
            message(st.session_state['user_messages'][i], key=str(i) + '_user', is_user=True, avatar_style="icons", seed=5)
            message(st.session_state['model_response'][i], key=str(i) + '_model', avatar_style="icons", seed=2)

##Add a sidebar with Resources:
st.sidebar.header('**Resources:**')
st.sidebar.markdown("<a style='text-decoration:none;' href='https://github.com/a16z-infra/llama2-chatbot'><font size=4>GitHub to clone this chat web app</font></a>", unsafe_allow_html=True)
st.sidebar.markdown("<a style='text-decoration:none;' href='https://github.com/a16z-infra/cog-llama-template'><font size=4>GitHub to deploy LLaMA2 on Replicate</font></a>", unsafe_allow_html=True)
st.sidebar.markdown('---') # Add a horizontal rule

