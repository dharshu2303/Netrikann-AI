from gtts import gTTS
text="Hi Dharshu how are you doing"
tts=gTTS(text=text)
tts.save("hello.mp3")
print("Audio saved")