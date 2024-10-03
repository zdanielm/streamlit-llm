import streamlit as st
from openai import OpenAI
import PyPDF2


st.set_page_config(
    page_title="PDF Learner Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed")

# Set OpenAI API key from Streamlit secrets
# (Create .streamlit/secrets.toml file and write your OpenAI API key there: OPENAI_API_KEY = "YOUR_API_KEY")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# PDF upload section
uploaded_pdf = st.file_uploader("Tölts fel egy PDF-et", type="pdf")

if uploaded_pdf is not None:
    # Read the PDF file and extract text
    pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
    extracted_text = ""

    # Extract text from the first 10 pages
    num_pages = min(10, len(pdf_reader.pages))
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        extracted_text += page.extract_text()

    # Do not display extracted content, just show a success message
    st.success(f"A PDF első {num_pages} oldala sikeresen feldolgozva.")

    # Start conversation with the extracted PDF content
    if "pdf_text" not in st.session_state:
        st.session_state["pdf_text"] = extracted_text
        #st.session_state.messages.append({"role": "assistant", "content": f"A következő tartalom lett kinyerve a PDF első {num_pages} oldalából:\n\n{extracted_text}"})

else:
    st.error("Kérlek, tölts fel egy PDF fájlt a folytatáshoz!")  # Error message, if no PDF is uploaded

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input and chat
if uploaded_pdf is not None:
    if prompt := st.chat_input("Kérdezz valamit a PDF tartalma alapján..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Include PDF content as context in the assistant's response
        with st.chat_message("assistant"):
            messages = [
                {"role": "system", "content": f"A felhasználó feltöltött egy PDF-et. Itt van az első 10 oldalból kinyert szöveg:\n\n{st.session_state['pdf_text']}"},
                *[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            ]

            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=messages,
                stream=True,
            )
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})
