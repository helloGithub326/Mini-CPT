import asyncio
from googletrans import Translator
import customtkinter as ctk

translator = Translator()

seenWords = {} #CHANGE TO JSON

async def translateText(text):
    result = await translator.translate(text, dest="es", src="en")
    #translatedWord = result.extra_data["translation"][0][0]
    translatedWord = result.extra_data["all-translations"][0][1][0]
    wordDefinition = result.extra_data["definitions"][0][1][0][0]
    similarWords = result.extra_data["all-translations"][0][1][1:]
        
    return translatedWord, wordDefinition, similarWords

text = input()
translatedWord, wordDefinition, similarWords = asyncio.run(translateText(text))

seenWords[translatedWord] = {"word": translatedWord, "def": wordDefinition, "similar": similarWords}
print(seenWords[translatedWord])

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#000000")
        self.title("Lingo Vocabulary") #CHANGE NAME
        self.geometry("600x400")
        self.after(0, lambda:self.state("zoomed"))

        self.mainloop()

if __name__ == "__main__":   
    App()