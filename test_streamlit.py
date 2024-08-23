import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from deep_translator import GoogleTranslator

api_key = "AIzaSyC57vVDUCQ94eRDFO8ntW67yyrxZXMLrgw"
genai.configure(api_key=api_key)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

st.title('Disease Analysis Chatbot')

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

uploaded_file = st.file_uploader("Choose an image...", type="jpg")
user_query = st.text_input("Enter your question about the image")

language = st.selectbox("Select Language", ["English", "Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", "Urdu"])

if st.button('Submit'):
    if uploaded_file is not None and user_query:
        image_data = uploaded_file.read()

        analysis_request = {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "text": user_query,
                    
                }
            ]
        }

        response = model.generate_content(analysis_request)

        if hasattr(response, 'text'):
            decoded_response = response.text.encode('utf-8').decode('unicode_escape')
            
            if language != "English":
                try:
                    language_codes = {
                        "Hindi": "hi",
                        "Bengali": "bn",
                        "Telugu": "te",
                        "Marathi": "mr",
                        "Tamil": "ta",
                        "Gujarati": "gu",
                        "Urdu": "ur"
                    }
                    translator = GoogleTranslator(source='en', target=language_codes[language])
                    decoded_response = translator.translate(decoded_response)
                except Exception as e:
                    st.write(f"Translation error: {e}")
            
            st.session_state.conversation.append({
                'user': user_query,
                'response': decoded_response
            })
            
            st.write("Conversation History:")
            for i, conv in enumerate(st.session_state.conversation):
                st.write(f"**User {i+1}**: {conv['user']}")
                st.write(f"**Response {i+1}**: {conv['response']}")
        else:
            st.write("Unable to get a valid response from the model.")
    else:
        st.write("Please upload an image and enter a query.")