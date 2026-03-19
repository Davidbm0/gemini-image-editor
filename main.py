import streamlit as st
import os
from io import BytesIO
from PIL import Image
from google import genai
from google.genai import types

GEMINI_API_KEY = ""


avatar = {
    "assistant": "🤖",
    "user": "👤"
}


def clear_chat_():
    st.session_state.messages = [
        {"role": "assistant",
         "content": "Salut! Sunt asistentul tău de editare foto. Încarcă o poză și spune-mi ce modificări să fac.",
         "image": None}
    ]


def generateResponse(input_text):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)


        contents = [input_text]


        if "image" in st.session_state and st.session_state.image:
            contents.append(st.session_state.image)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="Ești un editor de imagini expert. Generează o imagine nouă bazată pe cerințele utilizatorului și explică scurt ce ai modificat.",
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        return response
    except Exception as ex:
        st.error(f"Eroare API: {ex}")
        return None


def main():
    st.set_page_config(page_title='Gemini Image Editor', layout="centered")
    st.title("🎨 Gemini Image Editor")

    if "messages" not in st.session_state:
        clear_chat_()


    with st.sidebar:
        st.header("Setări")
        st.button("Șterge Conversația", on_click=clear_chat_)
        uploaded_file = st.file_uploader("Încarcă o imagine", type=["jpg", "png", "jpeg"])

        if uploaded_file:
            img = Image.open(uploaded_file)
            st.session_state.image = img
            st.image(img, caption="Imagine activă", use_container_width=True)


    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=avatar.get(message["role"])):
            st.write(message["content"])
            if message.get("image"):
                st.image(message["image"])


    if prompt := st.chat_input("Ex: 'Pune-i o pălărie roșie' sau 'Schimbă fundalul în albastru'"):
        st.session_state.messages.append({"role": "user", "content": prompt, "image": None})

        with st.chat_message("user", avatar=avatar["user"]):
            st.write(prompt)

        with st.chat_message("assistant", avatar=avatar["assistant"]):
            with st.spinner("Generez imaginea..."):
                response = generateResponse(prompt)

                if response:
                    full_text = ""
                    generated_img = None


                    for part in response.candidates[0].content.parts:
                        if part.text:
                            full_text += part.text
                        elif part.inline_data:
                            generated_img = Image.open(BytesIO(part.inline_data.data))

                    st.write(full_text)
                    if generated_img:
                        st.image(generated_img)


                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_text,
                        "image": generated_img
                    })


if __name__ == "__main__":
    main()