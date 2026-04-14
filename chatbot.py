import streamlit as st
import google.generativeai as genai
genai.configure(api_key="AIzaSyA2E8zi6nQcUnRJ3pmDwfrlNHSyd9j7Cd8")
model = genai.GenerativeModel("gemini-2.5-flash")

chat = model.start_chat(history=[])

print("Welcome to the Mock Interview Bot!")
role = st.text_input("What role are you preparing for? ")

system_prompt = (
    f"You are a career guide expert conducting a mock interview for the role of {role}. "
    "Ask 3 interview questions one by one. Wait for the user to answer each before asking the next. "
    "After the 3rd answer, give a final report and a score out of 10. Start with the first question now."
)
response = chat.send_message(system_prompt)
st.write("AI: " + response.text)
for i in range(3):
    user_input = input("\nYou: ")
    response = chat.send_message(user_input)
    print('\nAI:', response.text)

