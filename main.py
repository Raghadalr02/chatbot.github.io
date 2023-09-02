import os
import streamlit as st
from langchain.chains import ConversationChain
  # Import your API key from a file or set it directly here
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI
#from langchain.chat_models import ChatOpenAI

# Define a function to suggest a country and its places based on personality using ChatGPT
def suggest_country_and_places_from_chatgpt(personality):
    # Define a prompt to ask ChatGPT for a country and place suggestions
    chatgpt_prompt = f"Suggest a country and its places in Saudi Arabia for {personality} personality"

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

# Initialize Conversation as None
Conversation = None

# Set up the Streamlit app layout
st.title("✈️ Personalized Trip")

# Assign the API key directly here
os.environ['OPENAI_API_KEY'] = st.secrets['key']

# Initialize the OpenAI language model
llm = OpenAI(temperature=0,
             openai_api_key=st.secrets['key'],
             model_name='gpt-3.5-turbo',
             verbose=False)
#llm = ChatOpenAI(temperature=0,
 #           openai_api_key=st.secrets['key'],
  #           model_name='gpt-3.5-turbo',
   #          verbose=False
#)
# Initialize entity memory
if 'entity_memory' not in st.session_state:
    st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=st.number_input(
        ' (#)Summary of prompts to consider', min_value=3, max_value=1000))

# Initialize the Conversation object
Conversation = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=st.session_state.entity_memory
)

# Initialize responses list and current question index
responses = []
current_question = 0

# Define the new set of 8 questions
questions = [
    "Do you prefer to focus on concrete details rather than abstract concepts?",
    "Are you more practical and realistic than imaginative?",
    "Do you often think about the future and possibilities?",
    "Do you make decisions based on logic and analysis?",
    "Do you enjoy social interactions and meeting new people?",
    "Do you value harmony and strive to avoid conflicts?",
    "Are you often introspective and reflective?",
    "Do you trust your intuition when making decisions?"
]

# Loop through questions and get user responses iteratively
for i in range(8):
    if i == current_question:
        st.write(f"Question {i + 1}:")
        response = st.text_input(f"{questions[i]} (Yes/No)", key=f"question_{i}")
        response = response.strip().lower()  # Convert to lowercase and remove leading/trailing spaces
        if response == 'yes' or response == 'no':
            responses.append(response)
            current_question += 1
        elif response:
            st.warning("Re-enter answer please")  # Display error message for invalid response

# Assess personality based on responses
personality = "ENFP"  # You can change this to the actual assessment function based on responses

# Check if all 8 questions have been answered
if current_question == 8:
    # Suggest a country and places using ChatGPT
    suggested_country_and_places = suggest_country_and_places_from_chatgpt(personality)
    if suggested_country_and_places:
        st.subheader("Suggested Country and Places in Saudi Arabia:")
        st.write(f"Country: {suggested_country_and_places[0]}")
        st.write("Suggested Places:")
        for place in suggested_country_and_places[1:]:
            st.write(f"- {place}")
    else:
        st.warning("Sorry, no suggestions available for this personality.")

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
