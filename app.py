import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from google.cloud import firestore
db = firestore.Client.from_service_account_json("serviceAccountKey.json")

load_dotenv()

# Set the title of the webpage
st.set_page_config(page_title="Interactive Assistant", page_icon="https://icons.iconarchive.com/icons/microsoft/fluentui-emoji-flat/256/Robot-Flat-icon.png")
st.title("Interactive Assistant")
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages=[
        {
            "role":"assistant",
            "content":"Ask me Anything Under the Sky"
        }
    ]
    chat_history = []
    # Get messages from Firestore
    chat_ref = db.collection("chatdb").order_by('timestamp')
    docs = chat_ref.get()
    for doc in docs:
        message = doc.to_dict()
        chat_history.append(message)
    st.session_state.messages += chat_history

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Process and store Query and Response
def llm_function(query):
    # Display status message
    with st.spinner("Wait for me to process the query"):
        # Generate response
        response = model.generate_content(query)
        st.toast('Here is your answer!', icon='🎉')

    # Displaying the Assistant Message
    with st.chat_message("assistant"):
        st.markdown(response.text)

    # Storing the User Message
    user_message = {
        "role": "user",
        "content": query,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    st.session_state.messages.append(user_message)

    # Storing the Assistant Response
    assistant_message = {
        "role": "assistant",
        "content": response.text,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    st.session_state.messages.append(assistant_message)

    # Store the messages in Firestore
    chat_ref = db.collection("chatdb")
    chat_ref.add(user_message)
    chat_ref.add(assistant_message)

# Accept user input
query = st.chat_input("Ask Something ?")

# Calling the Function when Input is Provided
if query:
    # Displaying the User Message
    with st.chat_message("user"):
        st.markdown(query)

    llm_function(query)
