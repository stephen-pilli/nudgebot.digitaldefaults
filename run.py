import openai
import streamlit as st
import time
import re


messages_counter = 0
# assistant_id = "asst_rmysPCSULTOx88mnUgNBoY0b"
# assistant_id = "asst_usc60S31hykpgk1GZVo9II1f"
# assistant_id = "asst_U6dd7edl2xsk5BrUY4BDzDt5"
assistant_id = "asst_zHWEbYUhSaJoZTcLSCDAKp2f"


client = openai

if "chat_pilli" not in st.session_state:
    st.session_state['chat_pilli'] = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "messages_counter" not in st.session_state:
    st.session_state.messages_counter = 0
if "instructions" not in st.session_state:
    st.session_state['instructions'] = ""
if "checkbox" not in st.session_state:
    st.session_state.checkbox = None

st.set_page_config(page_title="Supermarket Chatbot", page_icon=":speech_balloon:")

openai.api_key = st.secrets["API_KEY"]

st.title("Supermarket")

if st.button("Start Shopping"):

    st.session_state['instructions'] = ""
    f = open("instructions.txt", "r")
    st.session_state.instructions = f.read()

    st.session_state.chat_pilli = True
    thread = client.beta.threads.create()

    st.session_state.thread_id = thread.id
    st.session_state.messages_counter = 0

if st.sidebar.button("Finish"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.chat_pilli = False  # Reset the chat state
    st.session_state.thread_id = None
    st.session_state.messages_counter = 0
    st.session_state['instructions'] = ""
    st.session_state.checkbox = None
    #TODO save messages here.

if st.session_state.chat_pilli:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]): 
            if message["role"] == "user":
                st.markdown(message["content"])
            elif re.search("#CODE-03#", message["content"]) != None:
                if st.session_state.checkbox == False:
                    st.markdown("Thanks for donating!!")
                else:
                    nudge = "A donation of €1 will be made on your behalf to the charity organization DRI.\
                    Please let me know if you would like to change it. The total grocery bill is €14."
                    def changed():
                        st.session_state.checkbox = False
                    # st.write(nudge)
                    st.session_state.checkbox = st.checkbox(nudge, value= True, on_change=changed)
            elif re.search("#CODE-09#", message["content"]) != None:
                    st.write("Submit the following code:", st.session_state.thread_id)
                    st.write("Thanks for participating, you may click the finish button")
            else:
                st.markdown(message["content"])

        
    if prompt := st.chat_input("Show me what you got."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)


        client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions=st.session_state.instructions
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        st.session_state.messages_counter += len(assistant_messages_for_run)
    

        if st.session_state.messages_counter > 20:
            st.session_state.messages = []  # Clear the chat history
            st.session_state.chat_pilli = False  # Reset the chat state
            st.session_state.thread_id = None
            st.session_state.messages_counter = 0
            st.session_state['instructions'] = ""
            st.session_state.checkbox = None
    

        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                if re.search("#CODE-03#", message.content[0].text.value) != None:
                    nudge = "A donation of €1 will be made on your behalf to the charity organization DRI.\
                    Please let me know if you would like to change it. The total grocery bill is €14."
                    def changed():
                        st.session_state.checkbox = False
                    # st.write(nudge)
                    st.session_state.checkbox = st.checkbox(nudge, value= True, on_change=changed)
                elif re.search("#CODE-09#", message.content[0].text.value) != None:
                    st.write("Submit the following code:", st.session_state.thread_id)
                    st.write("Thanks for participating, you may click the finish button")
                else: 
                    st.markdown(message.content[0].text.value)
                    
                    

        # f = open("data/"+str(st.session_state.thread_id)+".json", "w")
        # f.write(str(st.session_state['messages']))
        # f.close()
