import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

st.set_page_config(
    page_title="XETA AI Workspace",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #1E1E1E;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

def init_client():
    if "GEMINI_API_KEY" in st.secrets:
        try:
            return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        except Exception as e:
            st.error(f"Configuration Error: {e}")
            return None
    return None

client = init_client()

def home_page():
    st.title("XETA AI Workspace")
    st.markdown("### XETA AI Studio integrates multiple AI capabilities into a single intelligent platform.")
    st.write("Use the Sidebar on the left to navigate.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("Chat Assistant\n\nConversational AI with memory.")
    with col2:
        st.info("Global Translator\n\nTranslate text into 9+ languages.")
    with col3:
        st.info("Vision Analyst\n\nAnalyze images and extract text.")

def chatbot_interface():
    st.title("Intelligent Chat Assistant")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        history = [
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])]
            )
            for msg in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=history
                )
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                message_placeholder.error(f"System Error: {str(e)}")

def translator_interface():
    st.title("Global Translator")
    
    c1, c2 = st.columns([3, 1], gap="medium")
    
    with c1:
        target_lang = st.selectbox("Target Language", 
            ["Spanish", "French", "German", "Hindi", "Telugu", "Tamil", "Japanese", "Chinese", "Korean"])
    
    with c2:
        st.write("")
        st.write("") 
        translate_btn = st.button("Translate Content")

    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.subheader("Input")
        source_text = st.text_area("Input Text", height=300, label_visibility="collapsed", placeholder="Type or paste text here...")
    
    translation_result = ""
    if translate_btn and source_text:
        with st.spinner("Processing..."):
            try:
                prompt = f"Translate into {target_lang}. Provide the translation as plain text only without any markdown formatting:\n\n{source_text}"
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
                translation_result = response.text
            except Exception as e:
                st.error(f"Failed: {e}")
    elif translate_btn and not source_text:
        st.warning("Please enter text to translate.")

    with col2:
        st.subheader("Output")
        st.text_area("Output Text", value=translation_result, height=300, label_visibility="collapsed", placeholder="Translation will appear here...")

def vision_interface():
    st.title("Vision Analyst")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1], gap="medium")
        
        with col1:
            st.image(image, caption="Source", width="stretch")
            
        with col2:
            st.subheader("Options")
            action_type = st.radio("Mode", ["Detailed Description", "Text Extraction (OCR)", "Visual QA"])
            run_btn = st.button("Run Analysis")

        if run_btn:
            with st.spinner("Analyzing..."):
                prompt_map = {
                    "Detailed Description": "Describe this image in detail.",
                    "Text Extraction (OCR)": "Extract all visible text exactly as it appears.",
                    "Visual QA": "Identify key objects."
                }
                
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[prompt_map[action_type], image]
                    )
                    st.markdown("---")
                    st.subheader("Results")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Failed: {e}")

def main():
    if not client:
        st.error("API Key missing. Please check secrets.toml")
        st.stop()

    with st.sidebar:
        st.header("Navigation")
        options = ["Home", "Chat Assistant", "Translator", "Vision Analyst"]
        selection = st.radio("Go to:", options)
        

    if selection == "Home":
        home_page()
    elif selection == "Chat Assistant":
        chatbot_interface()
    elif selection == "Translator":
        translator_interface()
    elif selection == "Vision Analyst":
        vision_interface()

if __name__ == "__main__":
    main()