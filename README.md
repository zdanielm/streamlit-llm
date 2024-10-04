# A Streamlit PDF Learner Chatbot using OpenAI API
## (Cloud Technologies Project)

- A chatbot, that wants a PDF uploaded and it extracts the first maximum 10 pages and answers based on the content

## Requirements:
- Python 3 (used 3.12.2 for development) with pip
- OpenAI API with GPT-4o Access (Can be set to other model in the code)

## Setup (using pip):

### 1.: Create Python venv

```bash
python -m venv venv  # or python3 -m venv venv
```

### 2.: Activate the venv

#### Windows
```bash
venv\Scripts\activate
```
#### Linux & Unix

```bash
source venv/bin/activate
```

### 3.: Install required packages with pip (Streamlit, OpenAI, PyPDF2)
```bash
pip install -r requirements.txt
```
### &nbsp;&nbsp;&nbsp;&nbsp;Or just use:
```bash
pip install streamlit openai PyPDF2
```

### 4.: Configure OpenAI API key

#### You need to create a `.streamlit` folder with a `secrets.toml` file! </br>Linux example:
```bash
mkdir -p .streamlit && touch .streamlit/secrets.toml`
```

#### Then write your API key inside like this:
```toml
OPENAI_API_KEY = "YOUR_API_KEY"
```
> [!WARNING]
> Make sure to replace YOUR_API_KEY to your actual key (while keeping the double quotes)!

### 5. Run app

> [!WARNING]
> Make sure the venv you created has been activated (above)!

```bash
streamlit run main.py
```

🥳🥳🥳
***Now the chatbot should open up in your default browser.
Have fun!***
🥳🥳🥳
