import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
from deep_translator import GoogleTranslator
from groq import Groq

llama_client = Groq(api_key="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")

genai.configure(api_key="AIzaSyC57vVDUCQ94eRDFO8ntW67yyrxZXMLrgw")
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

st.title('Disease Analysis Chatbot')

if 'conversation' not in st.session_state:
    st.session_state.conversation = []

uploaded_file = st.file_uploader("Choose an image...", type="jpg")
user_query = st.text_input("Enter your question about the image")

language = st.selectbox("Select Language", ["English", "Hindi", "Punjabi", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", "Urdu"])

if st.button('Submit'):
    if uploaded_file is not None and user_query:
        image_data = uploaded_file.read()

        classification_request = {
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_data
                    }
                },
                {
                    "text": "Classify the image as either an animal, a plant, or something else."
                }
            ]
        }
        classification_response = model.generate_content(classification_request)

        if ("animal" in classification_response.text or 
            "plant" in classification_response.text or 
            "pet" in classification_response.text or 
            "flower" in classification_response.text or 
            "tree" in classification_response.text or 
            "bird" in classification_response.text or 
            "insect" in classification_response.text):
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
            try:
                response = model.generate_content(analysis_request)
                chat_completion = llama_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": response.text + " How can we help farmers prevent or eliminate this issue? Keep it concise for easy understanding.",
                        }
                    ],
                    model="llama-3.1-70b-versatile",
                )
                value = chat_completion.choices[0].message.content

                if hasattr(response, 'text'):
                    decoded_response = response.text.encode('utf-8').decode('unicode_escape')
                    value = value.encode('utf-8').decode('unicode_escape')
                    if language != "English":
                        try:
                            language_codes = {
                                "Hindi": "hi",
                                "Bengali": "bn",
                                "Telugu": "te",
                                "Marathi": "mr",
                                "Tamil": "ta",
                                "Gujarati": "gu",
                                "Urdu": "ur",
                                "Punjabi": "pa"
                            }
                            translator = GoogleTranslator(source='en', target=language_codes[language])
                            decoded_response = translator.translate(decoded_response)
                            value = translator.translate(value)
                        except Exception as e:
                            st.write(f"Translation error: {e}")

                    st.session_state.conversation.append({
                        'user': user_query,
                        'response': decoded_response + "\n  \n \n" + value
                    })

                    st.write("Conversation History:")
                    for i, conv in enumerate(st.session_state.conversation[-5:]):
                        st.write(f"**User {i+1}**: {conv['user']}")
                        st.write(f"**Response {i+1}**: {conv['response']}")
                else:
                    st.write("Unable to get a valid response from the model.")
            except Exception as e:
                st.write(f"Error: {e}")
        else:
            st.write("Please upload an image of an animal or plant.")
    else:
        st.write("Please upload an image and enter a query.")
