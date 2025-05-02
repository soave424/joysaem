import streamlit as st
from gtts import gTTS
import os
import base64
from io import BytesIO
import tempfile
import time

def text_to_speech(text, language='en', speed=1.0):
    """Convert text to speech and return an HTML audio element"""
    # Adjust speed by using slow parameter (slow=True means slower speech)
    slow = False if speed >= 1.0 else True
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        # Generate speech
        tts = gTTS(text=text, lang=language, slow=slow)
        tts.save(fp.name)
        
        # Read the file and encode as base64
        with open(fp.name, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        # Clean up the temporary file
        os.unlink(fp.name)
        
        # Encode the audio as base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Create an HTML audio element
        html_audio = f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        
        return html_audio

def get_available_languages():
    """Return a dictionary of available languages for gTTS"""
    return {
        'English': 'en',
        'Korean': 'ko',
        'Japanese': 'ja',
        'Chinese': 'zh-CN',
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt',
        'Russian': 'ru',
        'Hindi': 'hi',
        'Arabic': 'ar'
    }

def main():
    st.set_page_config(page_title="Text-to-Speech App", layout="wide")
    
    st.title("Text-to-Speech Application")
    st.write("Enter text and convert it to speech using Google's Text-to-Speech API")
    
    # Text input
    text_input = st.text_area("Enter text to convert to speech:", height=150)
    
    # Language selection
    languages = get_available_languages()
    selected_language_name = st.selectbox("Select language:", list(languages.keys()))
    selected_language_code = languages[selected_language_name]
    
    # Speed adjustment
    speed = st.slider("Speed:", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    
    # Display speed value
    st.write(f"Current speed: {speed}")
    
    # Create columns for buttons
    col1, col2 = st.columns(2)
    
    # Speak button
    if col1.button("Speak"):
        if text_input.strip():
            with st.spinner("Generating speech..."):
                # Generate speech
                audio_html = text_to_speech(text_input, selected_language_code, speed)
                
                # Display audio player
                st.markdown(audio_html, unsafe_allow_html=True)
                
                # Store the last played text
                st.session_state['last_text'] = text_input
                st.session_state['last_language'] = selected_language_code
                st.session_state['last_speed'] = speed
        else:
            st.error("Please enter text to speak.")
    
    # Stop button (this is a bit tricky in Streamlit as we can't directly control the audio)
    if col2.button("Stop"):
        st.warning("Audio playback stopped.")
        # This is a workaround - we replace the audio element with an empty one
        st.markdown('<audio controls></audio>', unsafe_allow_html=True)
    
    # Information about available voices
    st.subheader("About the voices")
    st.info("""
    This application uses Google's Text-to-Speech (gTTS) service, which provides high-quality voices.
    Different languages have different voice characteristics. The speed control allows you to adjust
    how fast or slow the speech is produced.
    """)
    
    # Usage instructions
    with st.expander("How to use"):
        st.write("""
        1. Enter the text you want to convert to speech in the text area above.
        2. Select the language from the dropdown menu.
        3. Adjust the speech speed using the slider.
        4. Click the 'Speak' button to generate and play the speech.
        5. Click the 'Stop' button to stop the current playback.
        """)

if __name__ == "__main__":
    # Initialize session state
    if 'last_text' not in st.session_state:
        st.session_state['last_text'] = ""
    if 'last_language' not in st.session_state:
        st.session_state['last_language'] = "en"
    if 'last_speed' not in st.session_state:
        st.session_state['last_speed'] = 1.0
    
    main()