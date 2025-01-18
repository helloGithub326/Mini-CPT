#CHECK WHETHER LIST EXPLAINATION IS GOOD (USE SAMPLE A AS GUIDE)
#ADD INPUT FOR GETTING THE LANGUAGE THE USER IS GOING TO LEARN WHEN USER FILE IS CREATED

import os
import asyncio
from googletrans import Translator
import customtkinter as ctk
import json

translator = Translator()

username = "" #CHANGE TO JSON
languageLearning = "en"
difficulty = ""
score = 0
position = 0
seenWords = {}
learnedWords = {}
masteredWords = {}

easyWords = []
mediumWords = []
hardWords = []

def loadWords():
    pass

def loadData(username):
    data = json.load(open(f"data/{username.lower()}.json"))

    languageLearning = data["languageLearning"]
    difficulty = data["difficulty"]
    score = data["score"]
    position = data["position"]
    seenWords = data["seenWords"]
    learnedWords = data["learnedWords"]
    masteredWords = data["masteredWords"]

    print(languageLearning, difficulty, score, position, seenWords, learnedWords, masteredWords)

    return data

def createData(username):
    pass

async def translateText(text):
    result = await translator.translate(text, dest=languageLearning, src="en")
    #translatedWord = result.extra_data["translation"][0][0]
    translatedWord = result.extra_data["all-translations"][0][1][0]
    wordDefinition = result.extra_data["definitions"][0][1][0][0]
    similarWords = result.extra_data["all-translations"][0][1][1:]
    
    return translatedWord, wordDefinition, similarWords

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#0B192C")
        self.title("Vocabulary") #CHANGE NAME
        self.geometry("1200x600")
        self.minsize(800, 400)
        self.after(0, lambda:self.state("zoomed"))

        self.columnconfigure(0, weight=1, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")
        self.rowconfigure(1, weight=5, uniform="a")

        self.detailsFrame = detailsFrame(self)

        self.loginFrame = loginFrame(self)
        self.loginFrame.nameSubmitButton.configure(command=self.getUser)

        self.mainloop()

    def getUser(self, *args):
        username = self.loginFrame.nameEntry.get()
        hasFile = False

        for filename in os.listdir("data"):
            if filename.rstrip(".json") == username:
                hasFile = True

        if hasFile:
            loadData(username)
        else:
            createData(username)

        positionFormatted = str(position)
        positionLastDigit = position % 10

        if position == 11 or position == 12 or position == 13:
            positionFormatted += "th"
        elif positionLastDigit == 1:
            positionFormatted += "st"
        elif positionLastDigit == 2:
            positionFormatted += "nd"
        elif positionFormatted == 3:
            positionFormatted += "rd"
        else:
            positionFormatted += "th"
        positionFormatted += " Place"

        self.detailsFrame.languageLabel.configure(text=languageLearning)
        print(difficulty)
        self.detailsFrame.difficultyLabel.configure(text=difficulty) #NOT GETTING CORRECT VALUE
        self.detailsFrame.usernameLabel.configure(text=username)
        self.detailsFrame.scoreLabel.configure(text=f"{score} Words Mastered")
        self.detailsFrame.positionLabel.configure(text=positionFormatted)

        self.loginFrame.destroy()
        self.vocabularyWordFrame = vocabularyWordFrame(self)

    def getWord(word):
        text = input()
        translatedWord, wordDefinition, similarWords = asyncio.run(translateText(text))

        seenWords[translatedWord] = {"word": translatedWord, "def": wordDefinition, "similar": similarWords}

class detailsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1, uniform="b")
        self.columnconfigure(1, weight=4, uniform="b")
        self.columnconfigure(2, weight=1, uniform="b")
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform="b")

        self.languageLabel = ctk.CTkLabel(self, text="Vocabulary", font=ctk.CTkFont(family="Calibri", size=52), anchor="s")
        self.languageLabel.grid(row=0, column=1, rowspan=3, sticky="nsew", pady=5)

        self.difficultyLabel = ctk.CTkLabel(self, text="Difficulty", font=ctk.CTkFont(family="Calibri", size=18), anchor="n")
        self.difficultyLabel.grid(row=3, column=1, sticky="nsew", pady=5)

        self.usernameLabel = ctk.CTkLabel(self, text="Username", font=ctk.CTkFont(family="Calibri", size=18), anchor="se")
        self.usernameLabel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.scoreLabel = ctk.CTkLabel(self, text="0 Words Mastered", font=ctk.CTkFont(family="Calibri", size=18), anchor="sw")
        self.scoreLabel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

        self.positionLabel = ctk.CTkLabel(self, text="0th Place", font=ctk.CTkFont(family="Calibri", size=18), anchor="nw")
        self.positionLabel.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)

class loginFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        self.columnconfigure(0, weight=1, uniform="c")
        self.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="c")

        nameLabel = ctk.CTkLabel(self, text="Enter Your Username:\n(a new one will be created if one does not exist)", font=ctk.CTkFont(family="Calibri", size=20))
        nameLabel.grid(row=1, column=0, sticky="nsew", padx=350, pady=10)

        self.nameEntry = ctk.CTkEntry(self, corner_radius=10, font=ctk.CTkFont(family="Calibri", size=20))
        self.nameEntry.grid(row=2, column=0, sticky="nsew", padx=350, pady=10)

        self.nameSubmitButton = ctk.CTkButton(self, text="Submit", corner_radius=10)
        self.nameSubmitButton.grid(row=3, column=0, sticky="nsew", padx=350, pady=10)

class vocabularyWordFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

class practiceWordFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

App()