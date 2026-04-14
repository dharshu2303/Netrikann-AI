import streamlit as st
import google.generativeai as g
from PIL import Image
st.title("Road Damage Analyzer")
a=st.file_uploader("Upload an image")
g.configure(api_key="AIzaSyA2E8zi6nQcUnRJ3pmDwfrlNHSyd9j7Cd8")
model=g.GenerativeModel("gemini-2.5-flash")
b=st.text_input("Enter your question")
if st.button("Submit"):
    a=Image.open(a)
    instruction = "You are a road damage analyzer. You must only answer queries related to road damage analysis. " \
    "If the question is not related to road damage, reply exactly with: '" \
    "I will be answering only questions related to road damage'."
    res=model.generate_content([a, instruction, b])
    st.write(res.text)