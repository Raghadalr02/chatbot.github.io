import streamlit as st
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationEntityMemory
from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
from langchain.llms import OpenAI

# Define a function to suggest a country and its places based on personality using ChatGPT
def suggest_country_and_places_from_chatgpt(personality):
    # Define a prompt to ask ChatGPT for a country and place suggestions
    chatgpt_prompt = f"Suggest a country and its places in Saudi Arabia for {personality} personality"

    # Use ChatGPT to generate suggestions
    response = Conversation.run(input=chatgpt_prompt)

    # Process and extract suggestions from the response
    suggestions = response.split('\n')

    # Initialize variables to store the formatted suggestions
    formatted_suggestions = []
    current_city = []  # Initialize as an empty list

    for suggestion in suggestions:
        # Check if the suggestion is a city
        if suggestion.startswith("- "):
            if current_city:
                formatted_suggestions.append("\n".join(current_city))
            current_city = [f"{suggestion[2:]}:"]
        elif suggestion:
            # Add places under the current city
            current_city.append(f"- {suggestion}")

    # Add the last city
    if current_city:
        formatted_suggestions.append("\n".join(current_city))

    return formatted_suggestions

# Define a function to determine personality type based on user responses
def determine_personality_type(answers):
    personality_type = ""

    # Question 1: Extroversion (E) or Introversion (I)
    if answers[0].lower() == "yes":
        personality_type += "E"
    elif answers[0].lower() == "no":
        personality_type += "I"
    else:
        return "Invalid Answer for Question 1"

    # Question 2: Sensing (S) or Intuition (N)
    if answers[1].lower() == "yes":
        personality_type += "S"
    elif answers[1].lower() == "no":
        personality_type += "N"
    else:
        return "Invalid Answer for Question 2"

    # Question 3: Thinking (T) or Feeling (F)
    if answers[2].lower() == "yes":
        personality_type += "T"
    elif answers[2].lower() == "no":
        personality_type += "F"
    else:
        return "Invalid Answer for Question 3"

    # Question 4: Judging (J) or Perceiving (P)
    if answers[3].lower() == "yes":
        personality_type += "J"
    elif answers[3].lower() == "no":
        personality_type += "P"
    else:
        return "Invalid Answer for Question 4"

    return personality_type

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

# Set up sidebar with various options
with st.sidebar.expander("🛠️ ", expanded=False):
    # Option to preview memory store
    if st.checkbox("Preview memory store"):
        with st.expander("Memory-Store", expanded=False):
            st.session_state.entity_memory.store
    # Option to preview memory buffer
    if st.checkbox("Preview memory buffer"):
        with st.expander("Bufffer-Store", expanded=False):
            st.session_state.entity_memory.buffer
    MODEL = st.selectbox(label='Model', options=['gpt-3.5-turbo', 'text-davinci-003', 'text-davinci-002', 'code-davinci-002'])
    K = st.number_input(' (#)Summary of prompts to consider', min_value=3, max_value=1000)

# Initialize Conversation as None
Conversation = None

# Set up the Streamlit app layout
st.title("✈️ Personalized Trip")

# Ask the user to enter their OpenAI API key
API_O = st.sidebar.text_input("API-KEY", type="password")

# Session state storage would be ideal
if API_O:
    # Create an OpenAI instance
    llm = OpenAI(temperature=0,
                 openai_api_key=API_O,
                 model_name=MODEL,
                 verbose=False)

    # Initialize entity memory
    if 'entity_memory' not in st.session_state:
        st.session_state.entity_memory = ConversationEntityMemory(llm=llm, k=3)  # Removed the input from the web interface

    # Initialize the Conversation object
    Conversation = ConversationChain(
        llm=llm,
        prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
        memory=st.session_state.entity_memory
    )

# Initialize responses list and current question index
responses = []
current_question = 0

# Define the new set of 4 questions
questions = [
    "Do you prefer socializing with others? ",
    "Are you detail-oriented and focused on the present? ",
    "Do you make decisions based on logic and analysis? ",
    "Are you organized and like to plan ahead? "
]

# Loop through questions and get user responses iteratively
for i in range(4):
    if i == current_question:
        st.write(f"Question {i + 1}:")
        response = st.text_input(f"{questions[i]} (Yes/No) ", key=f"question_{i}")
        response = response.strip().lower()  # Convert to lowercase and remove leading/trailing spaces
        if response == 'yes' or response == 'no':
            responses.append(response)
            current_question += 1
        elif response:
            st.warning("Re-enter answer please")  # Display error message for invalid response

# Generate country and places suggestions based on personality
if len(responses) == 4:
    personality = determine_personality_type(responses)
    st.write(f"Personality Type: {personality}")
    st.write("Suggestions:")
    suggestions = suggest_country_and_places_from_chatgpt(personality)
    for suggestion in suggestions:
        st.write(suggestion)
