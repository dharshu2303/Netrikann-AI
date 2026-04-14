from googletrans import Translator
translator=Translator()
translated=translator.translate("hi Dharshini How are you",src='en',dest='ta')
print(translated.text)