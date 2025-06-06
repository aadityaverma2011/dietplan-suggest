import streamlit as st
from PIL import Image
import base64
import requests
from io import BytesIO
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.badges import badge

# ---------------------- GEMINI SETUP ----------------------

API_KEY = st.secrets["GEMINI_API_KEY"]
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def image_to_base64(img: Image.Image):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def call_gemini_with_image(image_data_b64, prompt_text):
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_data_b64
                        }
                    },
                    {
                        "text": prompt_text
                    }
                ]
            }
        ]
    }
    response = requests.post(f"{GEMINI_API_URL}?key={API_KEY}", headers=headers, json=body)
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Gemini API Error."

# ---------------------- UI SETUP ----------------------

st.set_page_config(page_title="Visual Diet Coach", layout="centered", page_icon="🥗")

st.markdown("""
    <style>
    h1 { text-align: center; font-size: 3rem; margin-top: 1rem; color: #1F4E79; }
    .sub { text-align: center; font-size: 1.2rem; color: #333; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>Visual Diet Coach</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Upload a food photo and get nutrition advice directly from Gemini 1.5 Flash </div>", unsafe_allow_html=True)
badge(type="github", name="https://github.com/aadityaverma2011/dietplan-suggest", url="https://github.com/aadityaverma2011")

# ---------------------- FILE UPLOAD ----------------------

uploaded_file = st.file_uploader("Upload your meal photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Your Meal", use_container_width=True)

    if st.button("Get Nutrition Advice"):
        with st.spinner("Gemini is analyzing the image..."):
            b64_image = image_to_base64(image)
            prompt = (
    "You are a nutrition expert. Analyze this food image and provide a response in the following exact structure:\n\n"
    "1. **Identified Food Item:** (What food is shown?)\n"
    "2. **Estimated Calories:** (Approximate number of calories)\n"
    "3. **Health Assessment:** (Is it healthy or not? Why?)\n"
    "4. **Suggested Healthier Alternative:** (Recommend 1 better option, or say 'None needed')\n\n"
    "Keep it concise, informative, and human-friendly. Follow this format strictly."
)

            result = call_gemini_with_image(b64_image, prompt)

        with stylable_container("response", css_styles="padding: 1rem; background: #ffffff; border-radius: 12px; border: 1px solid #ddd; margin-top: 1rem;"):
            st.markdown(f"### Gemini's Take:\n{result}")
else:
    st.info("Upload a food image to get started!")

st.markdown("---")

