import speech_recognition as sr
from gtts import gTTS
import streamlit as st
import os
import google.generativeai as genai

# Mapping for language display
LANGUAGE_OPTIONS = {
    "Hindi": "hi",
    "Kannada": "kn",
    "Telugu": "te",
    "Tamil": "ta",
    "Malayalam": "ml",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Russian": "ru"
}

# Configure Gemini API
genai.configure(api_key='')


# Speech Recognition Function
def recognize_speech(language_code):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak something.")
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio, language=language_code)
            st.success(f"Recognized Speech: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")

    return None


# Translation Function using Gemini
def translate_text(input_text, source_language, target_language):
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Translate the following text from {source_language} to {target_language}. 
        Maintain the sentiment and context of the original text.
        Provide only the translation without any additional explanation or analysis.

        Text to translate: {input_text}
        """

        # Set safety settings to be more permissive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]

        response = model.generate_content(prompt, safety_settings=safety_settings)

        if response.text:
            return response.text.strip()
        else:
            return "Translation could not be generated. Please try rephrasing your input."

    except Exception as e:
        st.error(f"An error occurred during translation: {str(e)}")
        return "Error in translation. Please try again or rephrase your input."


# Text-to-Speech Function using gTTS
def text_to_speech(text, language_code='en'):
    try:
        tts = gTTS(text=text, lang=language_code)
        tts.save("translated_audio.mp3")
        return "translated_audio.mp3"
    except Exception as e:
        st.error(f"Text-to-Speech error: {e}")
        return None


# Streamlit App UI Layout
def main():
    st.title("🌐 Multilingual Live & Text Translator")

    # Choose between Text and Live Speech Translation
    translation_mode = st.radio("Choose Translation Mode:", ('Text Translation', 'Live Speech Translation'))

    if translation_mode == 'Text Translation':
        st.subheader("Text Translator")

        # Input text for translation
        input_text = st.text_area("Enter text to translate", "")

        # Source language selection
        source_language_name = st.selectbox(
            "Select source language",
            list(LANGUAGE_OPTIONS.keys()),
            key="source_text"
        )
        source_language = source_language_name

        # Target language selection
        target_language_name = st.selectbox(
            "Select target language for translation",
            list(LANGUAGE_OPTIONS.keys()),
            key="target_text"
        )
        target_language = target_language_name

        if st.button("Translate Text"):
            if input_text:
                translated_text = translate_text(input_text, source_language, target_language)
                if translated_text:
                    st.success(f"Translated Text: {translated_text}")
                    st.write("Playing the translated text as speech...")

                    # Convert translated text to speech
                    audio_file = text_to_speech(translated_text, LANGUAGE_OPTIONS[target_language_name])
                    if audio_file:
                        # Use Streamlit's audio player to play the audio
                        audio_bytes = open(audio_file, 'rb').read()
                        st.audio(audio_bytes, format='audio/mp3')

    elif translation_mode == 'Live Speech Translation':
        st.subheader("Live Speech Translator")

        # Select source language for speech recognition
        source_language_name = st.selectbox(
            "Select your language for speech recognition",
            list(LANGUAGE_OPTIONS.keys()),
            key="source_speech"
        )
        source_language_code = LANGUAGE_OPTIONS[source_language_name]

        # Target language selection
        target_language_name = st.selectbox(
            "Select target language for translation",
            list(LANGUAGE_OPTIONS.keys()),
            key="target_speech"
        )
        target_language = target_language_name

        if st.button("Start Listening"):
            input_text = recognize_speech(source_language_code)
            if input_text:
                translated_text = translate_text(input_text, source_language_name, target_language)
                if translated_text:
                    st.success(f"Translated Speech: {translated_text}")
                    st.write("Playing the translated text as speech...")

                    # Convert translated text to speech
                    audio_file = text_to_speech(translated_text, LANGUAGE_OPTIONS[target_language_name])
                    if audio_file:
                        # Use Streamlit's audio player to play the audio
                        audio_bytes = open(audio_file, 'rb').read()
                        st.audio(audio_bytes, format='audio/mp3')


if __name__ == "__main__":
    main()