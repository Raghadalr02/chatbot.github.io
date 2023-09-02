import os
import streamlit as st

from langchain.chains import ConversationChain

from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI

# Define the personality dataset
personality_dataset = {
    'ENFP': ['Yes', 'yes', 'Yes', 'No', 'Yes', 'No', 'Yes', 'No'],
    'ISTJ': ['No', 'Yes', 'No', 'Yes', 'No', 'Yes', 'No', 'Yes'],
    # Add more personality types and their associated responses here
}


# Define a function to assess personality based on responses
def assess_personality(responses):
    if responses.count('Yes') > 4:
        return 'ENFP'
    else:
        return 'ISTJ'


# Define a function to suggest places based on personality and city using ChatGPT
def suggest_places_from_chatgpt(personality, city):
    # Define a prompt to ask ChatGPT for place suggestions
    chatgpt_prompt = f"Suggest places in {city} for {personality} personality"

    # Use ChatGPT to generate suggestions
    response = Conversation.run(input=chatgpt_prompt)

    # Process and extract suggestions from the response
    suggestions = response.split('\n')
    return suggestions


# Set Streamlit page configuration
st.set_page_config(page_title='✈️ Personalized Trip', layout='wide')

# Initialize session states
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "past" not in st.session_state:
    st.session_state["past"] = []
if "input" not in st.session_state:
    st.session_state["input"] = ""
if "stored_session" not in st.session_state:
    st.session_state["stored_session"] = []


# Define function to get user input
def get_text(key="input"):
    input_text = st.text_input("You: ", st.session_state[key], key=key,
                               placeholder="Your AI assistant here! Ask me anything ...",
                               label_visibility='hidden')
    return input_text


# Define function to start a new chat
def new_chat():
    save = []
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        save.append("User:" + st.session_state["past"][i])
        save.append("Bot:" + st.session_state["generated"][i])
    st.session_state["stored_session"].append(save)
    st.session_state["generated"] = []
    st.session_state["past"] = []
    st.session_state["input"] = ""
    st.session_state.entity_memory.entity_store = {}
    st.session_state.entity_memory.buffer.clear()


# Set up the Streamlit app layout
st.title("✈️ Personalized Trip")

# Ask the user to enter their OpenAI API key
os.environ['OPENAI_API_KEY'] = st.secrets['key']

llm = OpenAI(temperature=0,
             openai_api_key=st.secrets['key'],
             model_name='gpt-3.5-turbo',
             verbose=False)
    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=st.number_input(
            ' (#)Summary of prompts to consider', min_value=3, max_value=1000))

    Conversation = ConversationChain(
        llm=llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state.entity_memory
    )
else:
    st.sidebar.warning('API key required to try this app. The API key is not stored in any form.')

# Collect 8 questions from the user to assess personality
responses = []
for i in range(8):
    response = st.radio(f"Question {i + 1}: Are you (Yes/No)?", options=['Yes', 'No'])
    responses.append(response)

# Assess personality based on responses
personality = assess_personality(responses)

# Ask the user about the city they want to visit
chosen_city = st.text_input("Enter the city you want to visit:")

# Generate place suggestions using ChatGPT
if chosen_city:
    suggested_places = suggest_places_from_chatgpt(personality, chosen_city)
    if suggested_places:
        st.subheader(f"Suggested Places in {chosen_city} for {personality} personality:")
        for place in suggested_places:
            st.write(f"- {place}")
    else:
        st.warning("Sorry, no suggestions available for this combination of personality and city.")

# ...

# Display the conversation history using an expander, and allow the user to download it
with st.expander("Conversation", expanded=True):
    download_str = []
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.info(st.session_state["past"][i], icon="🧐")
        st.success(st.session_state["generated"][i], icon="🤖")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])

    download_str = '\n'.join(download_str)
    if download_str:
        st.download_button('Download', download_str)

# Display stored conversation sessions in the sidebar
for i, sublist in enumerate(st.session_state.stored_session):
    with st.sidebar.expander(label=f"Conversation-Session:{i}"):
        st.write(sublist)

# Allow the user to clear all stored conversation sessions
if st.session_state.stored_session:
    if st.sidebar.checkbox("Clear-all"):
        del st.session_state.stored_session
