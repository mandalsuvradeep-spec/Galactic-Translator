import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import speech_recognition as sr
import base64
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Translator",
    page_icon="🟣",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- HELPER: LOAD LOCAL IMAGE ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- CUSTOM CSS SETUP ---
def set_background(png_file):
    try:
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""<style>.stApp {background-color: #0E1117;}</style>""", unsafe_allow_html=True)

# Load the background image
set_background('background.jpg')

# --- MAIN STYLING ---
st.markdown("""
<style>
    /* DEEP VIOLET COLOR VARIABLES */
    :root {
        --neon-purple: #4E16F2; 
        --dark-purple: #3a0fb3;
    }

    /* === WATERMARK STYLING === */
    .watermark {
        position: fixed;
        bottom: 20px;
        right: 25px;
        color: rgba(255, 255, 255, 0.6);
        font-size: 13px;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 400;
        z-index: 9999;
        letter-spacing: 1px;
        pointer-events: none;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8); /* Dark shadow for visibility */
    }

    /* === 1. VISIBILITY FIX FOR TITLE === */
    h1 { 
        text-align: center; 
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 900; 
        font-size: 3.5rem;
        margin-bottom: 20px;
        /* Strong black shadow to separate text from background */
        text-shadow: 0 4px 15px rgba(0, 0, 0, 0.9); 
    }
    
    /* === 2. REMOVE PINK BORDER (BRUTE FORCE FIX) === */
    .stTextArea div[data-baseweb="base-input"] {
        background-color: rgba(0,0,0,0.6) !important;
        border: 1px solid rgba(78, 22, 242, 0.3) !important;
        border-radius: 10px !important;
    }

    /* FORCE VIOLET ON FOCUS */
    .stTextArea div[data-baseweb="base-input"]:focus-within {
        border: 2px solid var(--neon-purple) !important;
        box-shadow: 0 0 15px rgba(78, 22, 242, 0.6) !important;
    }

    /* TEXT COLOR INSIDE BOX */
    .stTextArea textarea {
        color: white !important;
        caret-color: var(--neon-purple) !important;
    }

    /* === 3. TAB UNDERLINE FIX === */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: var(--neon-purple) !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--neon-purple) !important;
    }
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: var(--neon-purple) !important;
    }

    /* === 4. GLOBAL INTERACTION OVERRIDES === */
    ::selection {
        background-color: var(--neon-purple) !important;
        color: white !important;
    }

    /* Center the app vertically */
    .block-container {
        padding-top: 10vh !important;
        max_width: 700px;
    }

    /* Glassmorphism Tab Container */
    .stTabs {
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(20px);
        padding: 40px;
        border-radius: 25px;
        border: 1px solid rgba(78, 22, 242, 0.3); 
        box-shadow: 0 10px 40px rgba(0,0,0,0.8);
    }
    
    /* Result Card */
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid var(--neon-purple);
        margin-top: 25px;
    }
    
    p, label, .stMarkdown { color: #e0e0e0 !important; }
    
    /* Neon Buttons */
    .stButton>button {
        background: linear-gradient(90deg, var(--neon-purple) 0%, var(--dark-purple) 100%);
        color: white;
        border: none;
        height: 60px;
        border-radius: 12px;
        font-weight: 900;
        font-size: 20px;
        letter-spacing: 1px;
        box-shadow: 0 0 25px rgba(78, 22, 242, 0.5); 
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 40px rgba(78, 22, 242, 0.8);
    }
    .stButton>button:active, .stButton>button:focus {
        background: var(--neon-purple) !important;
        border-color: white !important;
        color: white !important;
    }
    
    /* Dropdown Focus */
    div[data-baseweb="select"] > div {
        background-color: rgba(0,0,0,0.6) !important;
        border-color: rgba(78, 22, 242, 0.3) !important;
    }
    div[data-baseweb="select"]:hover > div {
        border-color: var(--neon-purple) !important;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
def main():
    # INJECT WATERMARK
    st.markdown("<div class='watermark'>Made by Suvradeep</div>", unsafe_allow_html=True)

    # TITLE
    st.markdown("<h1>TRANS<span style='color:#4E16F2'>LATOR</span></h1>", unsafe_allow_html=True)
    
    with st.container():
        languages = {
            "Spanish": "es", "French": "fr", "German": "de", "Hindi": "hi",
            "Japanese": "ja", "Korean": "ko", "Russian": "ru", "Tamil": "ta",
            "Italian": "it", "Chinese": "zh-CN", "Arabic": "ar"
        }
        
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            target_lang_name = st.selectbox("", list(languages.keys()), label_visibility="collapsed")
            target_code = languages[target_lang_name]

        st.write("") 
        tab1, tab2 = st.tabs(["🎤  VOICE INPUT", "⌨️  TEXT INPUT"])

        # --- VOICE TAB ---
        with tab1:
            st.write("")
            st.markdown("<p style='text-align:center; opacity:0.7; font-family:monospace;'>INITIALIZE RECORDING SEQUENCE</p>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1,2,1])
            with c2:
                audio = mic_recorder(
                    start_prompt="▶ START",
                    stop_prompt="⬛ STOP & PROCESS",
                    key='recorder',
                    format="wav"
                )

            if audio:
                with st.spinner("PROCESSING AUDIO STREAM..."):
                    r = sr.Recognizer()
                    audio_data = io.BytesIO(audio['bytes'])
                    try:
                        with sr.AudioFile(audio_data) as source:
                            audio_listened = r.record(source)
                            text_in = r.recognize_google(audio_listened)
                        process_translation(text_in, target_code)
                    except Exception:
                        st.error("AUDIO DATA CORRUPTED. RETRY.")

        # --- TEXT TAB ---
        with tab2:
            text_input = st.text_area("", height=120, placeholder="> ENTER DATA HERE...")
            if st.button("EXECUTE TRANSLATION"):
                if text_input:
                    process_translation(text_input, target_code)

def process_translation(text, target_code):
    try:
        translated = GoogleTranslator(source='auto', target=target_code).translate(text)
        
        st.markdown(f"""
        <div class='result-card'>
            <p style='color:#aaa; font-size:12px; margin-bottom:10px; font-family:monospace; text-transform:uppercase;'>[ Input Data ]</p>
            <p style='font-size:20px; color:white; margin-bottom:25px; line-height:1.4; font-family:monospace;'>{text}</p>
            <div style='height:1px; background:rgba(78, 22, 242, 0.3); margin-bottom:25px;'></div>
            <p style='color:#4E16F2; font-size:12px; margin-bottom:10px; font-family:monospace; text-transform:uppercase;'>[ Translated Output ]</p>
            <p style='font-size:30px; font-weight:700; color:#4E16F2; line-height:1.3; font-family:monospace; text-shadow: 0 0 15px rgba(78, 22, 242, 0.5);'>{translated}</p>
        </div>
        """, unsafe_allow_html=True)

        tts = gTTS(text=translated, lang=target_code)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        st.audio(audio_fp, format='audio/mp3', start_time=0)
        
    except Exception as e:
        st.error(f"SYSTEM ERROR: {e}")

if __name__ == "__main__":
    main()