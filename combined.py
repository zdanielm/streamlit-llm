import streamlit as st
from openai import OpenAI
import PyPDF2
from hugchat import hugchat
from hugchat.login import Login

# Set up Streamlit app configuration
st.set_page_config(
    page_title="PDF Tanuló Chatbot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar for model selection
with st.sidebar:
    st.title('Chatbot kiválasztása')
    chatbot_option = st.radio(
        "Válassz egy chatbotot:",
        ('OpenAI (alapértelmezett)', 'HugChat'),
        index=0  # OpenAI is selected by default
    )

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", ""))

# Fetch Hugging Face credentials from secrets.toml
hf_email = st.secrets.get("EMAIL", "")
hf_pass = st.secrets.get("PASS", "")

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

    # Show success message when PDF content is extracted
    st.success(f"A PDF első {num_pages} oldala sikeresen feldolgozva.")

    # Save extracted PDF content
    if "pdf_text" not in st.session_state:
        st.session_state["pdf_text"] = extracted_text

else:
    st.error("Kérlek, tölts fel egy PDF fájlt a folytatáshoz!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to generate OpenAI response
def generate_openai_response(prompt):
    messages = [
        {"role": "system", "content": f"A felhasználó feltöltött egy PDF-et. Itt van az első 10 oldalból kinyert szöveg:\n\n{st.session_state['pdf_text']}"},
        *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    ]

    # Collect response in a buffer
    response_buffer = ""
    stream = client.chat.completions.create(
        model="gpt-4o-mini",  # Use your desired OpenAI model
        messages=messages,
        stream=True,
    )

    # Iterate through chunks and collect the content
    for chunk in stream:
        # Access delta content directly, checking for its existence
        if hasattr(chunk.choices[0].delta, 'content'):
            content = chunk.choices[0].delta.content
            if content:  # Ensure content is not None
                response_buffer += content

    return response_buffer


# Function to generate HugChat response with PDF context
def generate_hugchat_response(prompt_input, email, passwd):
    sign = Login(email, passwd)
    cookies = sign.login()
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())

    # Include extracted PDF text in the prompt for context
    pdf_context = f"A PDF első 10 oldalból kinyert szöveg:\n\n{st.session_state['pdf_text']}\n\n"
    full_prompt = pdf_context + prompt_input

    # Send the prompt including the PDF content to HugChat
    return chatbot.chat(full_prompt)

# Main chat interaction
if uploaded_pdf is not None:
    # User input and chat for OpenAI
    if chatbot_option == 'OpenAI (alapértelmezett)':
        if prompt := st.chat_input("Kérdezz valamit a PDF tartalma alapján..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # OpenAI assistant response
            with st.chat_message("assistant"):
                with st.spinner("Gondolkodom..."):
                    response = generate_openai_response(prompt)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # User input and chat for HugChat
    elif chatbot_option == 'HugChat':
        # Only ask for credentials if not available in secrets.toml
        if not hf_email or not hf_pass:
            with st.sidebar:
                st.header('HuggingFace bejelentkezés')
                hf_email = st.text_input('Add meg a Hugging Face e-mail címed:', type='password')
                hf_pass = st.text_input('Add meg a Hugging Face jelszavad:', type='password')

        if hf_email and hf_pass:
            if prompt := st.chat_input("Kérdezz valamit..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                # HugChat assistant response with PDF content as context
                if st.session_state.messages[-1]["role"] != "assistant":
                    with st.chat_message("assistant"):
                        with st.spinner("Gondolkodom..."):
                            response = generate_hugchat_response(prompt, hf_email, hf_pass)
                            st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.warning("Kérlek, add meg a HuggingFace bejelentkezési adataid!", icon="⚠️")
