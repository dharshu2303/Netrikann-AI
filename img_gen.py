import requests
import streamlit as st
import google.generativeai as g
st.title("Image Generation")
prompt=st.text_input("Enter a prompt:")
if st.button("Generate Image"):
    url="https://image.pollinations.ai/prompt/"+requests.utils.quote(prompt)
    img=requests.get(url).content
    with open("o.png","wb") as f:
        f.write(img)
    st.image("o.png", caption="Generated Image")