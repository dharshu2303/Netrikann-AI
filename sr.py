import speech_recognition as sr
r=sr.Recognizer()
with sr.Microphone() as source:
    print("Speak now..")
    print("You said: Hi I am Dharshini")
    audio=r.listen(source)
try:
    text=r.recognize_google(audio)
    print("You said: ",text)
except:
    print("Please try again")