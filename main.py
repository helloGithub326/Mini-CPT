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

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#0B192C")
        self.title("Lingo Vocabulary") #CHANGE NAME
        self.geometry("1200x600")
        self.minsize(800, 400)
        self.after(0, lambda:self.state("zoomed"))

        self.columnconfigure(0, weight=1, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")
        self.rowconfigure(1, weight=5, uniform="a")

        vocabularyWordFrame(self)

        self.mainloop()

    def getWord(word):
        text = input()
        translatedWord, wordDefinition, similarWords = asyncio.run(translateText(text))

        seenWords[translatedWord] = {"word": translatedWord, "def": wordDefinition, "similar": similarWords}

class vocabularyWordFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

App()