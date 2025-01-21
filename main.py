import os
import asyncio
from googletrans import Translator
import customtkinter as ctk
import json
import random

translator = Translator()

def loadWords():
    global languageKeys
    global easyWords
    global mediumWords
    global hardWords

    words = json.load(open("words.json"))

    languageKeys = words["languageKeys"]
    easyWords = words["easy"]
    mediumWords = words["medium"]
    hardWords = words["hard"]

def loadData(name):
    global languageLearning
    global difficulty
    global score
    global position
    global seenWords
    global learnedWords
    global masteredWords

    data = json.load(open(f"data/{name.lower().replace(" ", "_")}.json"))

    languageLearning = data["languageLearning"]
    difficulty = data["difficulty"]
    score = data["score"]
    position = data["position"]
    seenWords = data["seenWords"]
    learnedWords = data["learnedWords"]
    masteredWords = data["masteredWords"]

def saveData(name, newLanguage="", newDifficulty="", newScore=0, newPosition=0, newSeenWords={}, newLearnedWords={}, newMasteredWords={}, create=False):
    global username
    global languageLearning
    global difficulty
    global score
    global position
    global seenWords
    global learnedWords
    global masteredWords
    
    if create:
        newData = {
            "name": name,
            "languageLearning": newLanguage,
            "difficulty": "easy",
            "score": 0,
            "position": 0,
            "seenWords": {},
            "learnedWords": {},
            "masteredWords": {}
        }

    if not create:
        data = json.load(open(f"data/{name.lower().replace(" ", "_")}.json"))        

        newData = {
            "name": name,
            "languageLearning": data["languageLearning"],
            "difficulty": data["difficulty"],
            "score": data["score"],
            "position": data["position"],
            "seenWords": data["seenWords"],
            "learnedWords": data["learnedWords"],
            "masteredWords": data["masteredWords"]
        }

    if newDifficulty != "":
        newData["difficulty"] = newDifficulty
    if newScore != 0:
        newData["score"] = newScore
    if newPosition != 0:
        newData["position"] = newPosition
    if newSeenWords != {}:
        newData["seenWords"] = newSeenWords
    if newLearnedWords != {}:
        newData["learnedWords"] = newLearnedWords
    if newMasteredWords != {}:
        newData["masteredWords"] = newMasteredWords

    if name == username:
        languageLearning = newData["languageLearning"]
        difficulty = newData["difficulty"]
        score = newData["score"]
        position = newData["position"]
        seenWords = newData["seenWords"]
        learnedWords = newData["learnedWords"]
        masteredWords = newData["masteredWords"]

    with open(f"data/{name.lower().replace(" ", "_")}.json", "w") as file:
        json.dump(newData, file)

def checkPosition(username):
    global position
    global score
    files = os.listdir("data")

    if score == 0:
        position = len(files)
        saveData(name=username, newPosition=position)

    scores = {}
    for filename in files:
        scores[filename] = json.load(open(f"data/{filename}"))["score"]

    sortedScoresList = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    sortedScores = {}
    for sortedScore in sortedScoresList:
        sortedScores[sortedScore[0]] = sortedScore[1]
    sortedScoresKeyList = list(sortedScores.keys())

    for filename, score in sortedScores.items():
        positionInFile = json.load(open(f"data/{filename}"))["position"]
        if positionInFile != (sortedScoresKeyList.index(filename)+1):
            saveData(name=(filename.replace(".json", "")), newPosition=(sortedScoresKeyList.index(filename)+1))

async def translateList(list):
    translatedWords = {}
    translations = await translator.translate([word for word in list], dest=languageLearning, src="en")
    for index, translation in enumerate(translations):
        translatedWord = translation.extra_data["translation"][0][0]
        wordDefinition = translation.extra_data["definitions"][0][1][0][0]
        try:
            similarWords = translation.extra_data["all-translations"][0][1][1:]
        except:
            similarWords = []
        
        translatedWords[list[index]] = {"translated": translatedWord, "definition": wordDefinition, "similar": similarWords}
    return translatedWords

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#0B192C")
        self.title("V-Lang: Unlock the Power of a Language, One Word at a Time!")
        self.geometry("1200x600")
        self.minsize(800, 400)
        self.after(0, lambda:self.state("zoomed"))

        self.columnconfigure(0, weight=1, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")
        self.rowconfigure(1, weight=5, uniform="a")

        global username

        loadWords()

        self.detailsFrame = detailsFrame(self)

        self.loginFrame = loginFrame(self)
        self.loginFrame.submitButton.configure(command=self.getUser)

        self.mainloop()

    def getUser(self, name="", *args):
        global username

        hasFile = False
        if name == "":
            if self.loginFrame.nameEntry.get():
                self.username = self.loginFrame.nameEntry.get()
        else:
            self.username = name

        username = self.username

        for filename in os.listdir("data"):
            if filename == self.username.lower().replace(" ", "_") + ".json":
                hasFile = True

        if hasFile:
            loadData(self.username)
            self.updateUI()
            
            self.loginFrame.destroy()

            allWords = easyWords + mediumWords + hardWords
            allWordsTranslated = asyncio.run(translateList(allWords))
            
            self.easyWordsTranslated = {}
            self.mediumWordsTranslated = {}
            self.hardWordsTranslated = {}

            index = 0
            for word in allWordsTranslated:
                if index <= (len(easyWords) - 1):
                    self.easyWordsTranslated[word] = {"translated": allWordsTranslated[word]["translated"], "definition": allWordsTranslated[word]["definition"], "similar": allWordsTranslated[word]["similar"]}
                elif index <= (((len(easyWords) + len(mediumWords))) - 1):
                    self.mediumWordsTranslated[word] = {"translated": allWordsTranslated[word]["translated"], "definition": allWordsTranslated[word]["definition"], "similar": allWordsTranslated[word]["similar"]}
                elif index <= (((len(easyWords) + len(mediumWords) + len(hardWords))) - 1):
                    self.hardWordsTranslated[word] = {"translated": allWordsTranslated[word]["translated"], "definition": allWordsTranslated[word]["definition"], "similar": allWordsTranslated[word]["similar"]}
                index += 1

            self.vocabularyWordFrame = vocabularyWordFrame(self)
        else:
            self.loginFrame.nameLabel.configure(text="Choose The Language You Want to Learn:")
            self.loginFrame.nameEntry.destroy()
            self.loginFrame.languageDropdown.grid(row=2, column=0, sticky="nsew", padx=350, pady=10)
            self.loginFrame.submitButton.configure(command=self.setLanguage)

    def setLanguage(self, *args):
        languageInput = self.loginFrame.languageDropdown.get().lower()

        for key, language in languageKeys.items():
                if language == languageInput:
                    languageCode = key

        saveData(name=self.username, newLanguage=languageCode, create=True)
        self.getUser(name=self.username)

    def updateUI(self):
        checkPosition(self.username)

        languageLearningFormatted = ""
        for key, language in languageKeys.items():
            if languageLearning == key:
                languageLearningFormatted = language.capitalize()

        
        scoreFormatted = str(score)
        if score == 1:
            scoreFormatted += " Word Mastered"
        else:
            scoreFormatted += " Words Mastered"

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

        self.detailsFrame.languageLabel.configure(text=languageLearningFormatted)
        self.detailsFrame.difficultyLabel.configure(text=difficulty.capitalize())
        self.detailsFrame.usernameLabel.configure(text=self.username.capitalize())
        self.detailsFrame.scoreLabel.configure(text=scoreFormatted)
        self.detailsFrame.positionLabel.configure(text=positionFormatted)
    
    def openPractice(self):
        global seenWords

        if not (self.vocabularyWordFrame.currentWord in list(seenWords.keys())):
            seenWords[self.vocabularyWordFrame.currentWord] = {"translated": self.vocabularyWordFrame.translatedWord, "definition": self.vocabularyWordFrame.wordDefinition, "similar": self.vocabularyWordFrame.similarWords}
        
        self.practiceWordFrame = practiceWordFrame(self, self.updateUI)
        self.vocabularyWordFrame.destroy()
    
    def openLearn(self):
        self.vocabularyWordFrame = vocabularyWordFrame(self)
        self.practiceWordFrame.destroy()

class detailsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid(row=0, column=0, sticky="nsew")

        self.columnconfigure(0, weight=1, uniform="b")
        self.columnconfigure(1, weight=4, uniform="b")
        self.columnconfigure(2, weight=1, uniform="b")
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform="b")

        self.languageLabel = ctk.CTkLabel(self, text="V-Lang", font=ctk.CTkFont(family="Futura", size=52), anchor="s")
        self.languageLabel.grid(row=0, column=1, rowspan=3, sticky="nsew", pady=5)

        self.difficultyLabel = ctk.CTkLabel(self, text="Unlock the Power of a Language, One Word at a Time!", font=ctk.CTkFont(family="Futura", size=18), anchor="n")
        self.difficultyLabel.grid(row=3, column=1, sticky="nsew", pady=5)

        self.usernameLabel = ctk.CTkLabel(self, text="Username", font=ctk.CTkFont(family="Futura", size=18), anchor="se")
        self.usernameLabel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=20, pady=10)

        self.scoreLabel = ctk.CTkLabel(self, text="0 Words Mastered", font=ctk.CTkFont(family="Futura", size=18), anchor="sw")
        self.scoreLabel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=20, pady=10)

        self.positionLabel = ctk.CTkLabel(self, text="0th Place", font=ctk.CTkFont(family="Futura", size=18), anchor="nw")
        self.positionLabel.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=20, pady=10)

class loginFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        self.columnconfigure(0, weight=1, uniform="c")
        self.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="c")

        self.nameLabel = ctk.CTkLabel(self, text="Enter Your Username:\n(new data will be created if data does not already exist)", font=ctk.CTkFont(family="Futura", size=20))
        self.nameLabel.grid(row=1, column=0, sticky="nsew", padx=350, pady=10)

        self.nameEntry = ctk.CTkEntry(self, corner_radius=10, fg_color="#333333", border_width=0, font=ctk.CTkFont(family="Futura", size=20))
        self.nameEntry.grid(row=2, column=0, sticky="nsew", padx=350, pady=10)

        languageKeysList = list(languageKeys.values())
        for index, languageKey in enumerate(languageKeysList):
            languageKeysList[index] = languageKey.capitalize()
        
        self.languageDropdown = ctk.CTkOptionMenu(self, values=languageKeysList, corner_radius=10, fg_color="#333333", button_color="#333333", button_hover_color="#333333", font=ctk.CTkFont(family="Futura", size=20))
        self.languageDropdown

        self.submitButton = ctk.CTkButton(self, text="Submit", corner_radius=10, font=ctk.CTkFont(family="Futura", size=20))
        self.submitButton.grid(row=3, column=0, sticky="nsew", padx=350, pady=10)

class vocabularyWordFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        self.columnconfigure(0, weight=1, uniform="d")
        self.columnconfigure(1, weight=8, uniform="d")
        self.columnconfigure(2, weight=1, uniform="d")
        self.rowconfigure(0, weight=2, uniform="d")
        self.rowconfigure(1, weight=3, uniform="d")
        self.rowconfigure(2, weight=1, uniform="d")
        self.rowconfigure(3, weight=3, uniform="d")
        self.rowconfigure(4, weight=2, uniform="d")

        global difficulty
        global seenWords

        self.easyWordsTranslated = parent.easyWordsTranslated
        self.mediumWordsTranslated = parent.mediumWordsTranslated
        self.hardWordsTranslated = parent.hardWordsTranslated

        if difficulty == "easy":
            self.wordList = easyWords
            self.wordDict = self.easyWordsTranslated
        elif difficulty == "medium":
            self.wordList = mediumWords
            self.wordDict = self.mediumWordsTranslated
        elif difficulty == "hard":
            self.wordList = hardWords
            self.wordDict = self.hardWordsTranslated

        self.currentWords = []
        self.translatedWord = ""
        self.currentWord = ""
        self.wordDefinition = ""
        self.similarWords = ""
        
        if difficulty != "viewed":
            self.newWord()

        self.wordLabel = ctk.CTkLabel(self, text=self.translatedWord, font=ctk.CTkFont(family="Futura", size=42), anchor="s")
        self.wordLabel.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        self.originalWordLabel = ctk.CTkLabel(self, text=f"({self.currentWord})", font=ctk.CTkFont(family="Futura", size=16), anchor="n")
        self.originalWordLabel.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)

        self.defLabel = ctk.CTkLabel(self, text=self.wordDefinition, font=ctk.CTkFont(family="Futura", size=20), anchor="n")
        self.defLabel.grid(row=3, column=1, sticky="nsew", pady=5)

        self.similarWordsLabel = ctk.CTkLabel(self, text=self.similarWords, font=ctk.CTkFont(family="Futura", size=18))
        self.similarWordsLabel.grid(row=4, column=1, sticky="nsew", pady=5)

        self.nextButton = ctk.CTkButton(self, text=">", corner_radius=50, command=self.nextWord, font=ctk.CTkFont(family="Futura", size=20))
        self.nextButton.grid(row=0, column=2, sticky="nes", padx=25, pady=25)
        
        self.previousButton = ctk.CTkButton(self, text="<", corner_radius=50, command=self.previousWord, font=ctk.CTkFont(family="Futura", size=20))
        self.previousButton.grid(row=0, column=0, sticky="nsw", padx=25, pady=25)

        self.practiceButton = ctk.CTkButton(self, text="Practice", corner_radius=50, command=parent.openPractice, font=ctk.CTkFont(family="Futura", size=20))
        self.practiceButton.grid(row=0, column=1, sticky="nsew", padx=425, pady=25)

        if difficulty == "viewed":
            self.wordLabel.configure(text="YOU HAVE SEEN ALL THE WORDS!\nPRACTICE THEM TO REMEMBER THEM!")
            self.originalWordLabel.configure(text="")
            self.defLabel.configure(text="")
            self.similarWordsLabel.configure(text="")
    
    def newWord(self):
        global seenWords
        global difficulty

        try:
            repeat = True
            iterations = 0
            while repeat:
                if iterations == (len(self.wordList) - 1):
                    self.changeDifficulty()
                    if difficulty == "viewed":
                        repeat = False
                self.currentWord = random.choice(self.wordList)
                repeat = False
                if self.currentWord in list(seenWords.keys()):
                    repeat = True
                iterations += 1
            
            if difficulty == "viewed":
                self.wordLabel.configure(text="YOU HAVE SEEN ALL THE WORDS!\nPRACTICE THEM TO REMEMBER THEM!")
                self.originalWordLabel.configure(text="")
                self.defLabel.configure(text="")
                self.similarWordsLabel.configure(text="")
            elif difficulty != "viewed":
                self.translatedWord = self.wordDict[self.currentWord]["translated"]
                self.wordDefinition = self.wordDict[self.currentWord]["definition"]
                self.similarWords = self.wordDict[self.currentWord]["similar"]

                defList = self.wordDefinition.replace(" ", " -")
                defList = defList.split("-")

                length = 0
                for index, word in enumerate(defList):
                    length += len(word)
                    if length >= 50:
                        defList.insert(index, "\n")
                        length -= 50
                
                defStr = ""
                for word in defList:
                    defStr += word
                
                defStr = defStr.rstrip(".")
                self.wordDefinition = defStr

                similarWordsList = self.similarWords
                length = 0
                for index, word in enumerate(similarWordsList):
                    length += len(word)
                    if length >= 75:
                        similarWordsList.insert(index, "\n")
                        length -= 75

                similarWordsStr = "Similar Words:\n"
                previousWord = ""
                for index, word in enumerate(similarWordsList):
                    if index == 0 or previousWord == "\n":
                        similarWordsStr += word
                    else:
                        similarWordsStr += f", {word}"
                    previousWord = word
                self.similarWords = similarWordsStr
        except Exception as e:
            self.newWord()

    def updateWord(self, word=""):
        global username
        global seenWords

        if word != "":
            wordData = seenWords[word]

            self.translatedWord = wordData["translated"]
            self.currentWord = self.currentWords[self.currentWords.index(word)]
            self.wordDefinition = wordData["definition"]
            self.similarWords = wordData["similar"]
        
        self.wordLabel.configure(text=self.translatedWord)
        self.originalWordLabel.configure(text=f"({self.currentWord})")
        self.defLabel.configure(text=self.wordDefinition)
        self.similarWordsLabel.configure(text=self.similarWords)

        saveData(name=username, newSeenWords=seenWords)

    def nextWord(self):
        global seenWords
        global difficulty

        if not(self.currentWord in self.currentWords):
            self.currentWords.append(self.currentWord)
        currentWordIndex = self.currentWords.index(self.currentWord)
        if currentWordIndex == (len(self.currentWords)-1):
            seenWords[self.currentWord] = {"translated": self.translatedWord, "definition": self.wordDefinition, "similar": self.similarWords}
            self.newWord()
            if difficulty != "viewed":
                self.updateWord()
        else:
            self.updateWord(self.currentWords[currentWordIndex+1])

    def previousWord(self):
        global seenWords

        self.currentWords.append(self.currentWord)
        currentWordIndex = self.currentWords.index(self.currentWord)
        if currentWordIndex == (len(self.currentWords)-1):
            seenWords[self.currentWord] = {"translated": self.translatedWord, "definition": self.wordDefinition, "similar": self.similarWords}
            self.updateWord(self.currentWords[currentWordIndex-1])
        elif currentWordIndex != 0:
            self.currentWords.pop()
            self.updateWord(self.currentWords[currentWordIndex-1])
        else:
            self.currentWords.pop()

    def changeDifficulty(self):
        global username
        global difficulty

        if difficulty == "easy":
            difficulty = "medium"
            self.wordList = mediumWords
            self.wordDict = self.mediumWordsTranslated
        elif difficulty == "medium":
            difficulty = "hard"
            self.wordList = hardWords
            self.wordDict = self.hardWordsTranslated
        elif difficulty == "hard":
            difficulty = "viewed"
            self.wordLabel.configure(text="YOU HAVE SEEN ALL THE WORDS!\nPRACTICE THEM TO REMEMBER THEM!")
            self.originalWordLabel.configure(text="")
            self.defLabel.configure(text="")
            self.similarWordsLabel.configure(text="")
        else:
            self.wordLabel.configure(text="YOU HAVE SEEN ALL THE WORDS!\nPRACTICE THEM TO REMEMBER THEM!")
            self.originalWordLabel.configure(text="")
            self.defLabel.configure(text="")
            self.similarWordsLabel.configure(text="")   

        saveData(name=username, newDifficulty=difficulty)

class practiceWordFrame(ctk.CTkFrame):
    def __init__(self, parent, updateUI):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        self.columnconfigure(0, weight=1, uniform="e")
        self.columnconfigure(1, weight=2, uniform="e")
        self.columnconfigure(2, weight=2, uniform="e")
        self.columnconfigure(3, weight=2, uniform="e")
        self.columnconfigure(4, weight=2, uniform="e")
        self.columnconfigure(5, weight=1, uniform="e")
        self.rowconfigure(0, weight=2, uniform="e")
        self.rowconfigure(1, weight=3, uniform="e")
        self.rowconfigure(2, weight=1, uniform="e")
        self.rowconfigure(3, weight=3, uniform="e")
        self.rowconfigure(4, weight=2, uniform="e")

        self.updateUI = updateUI

        self.wordDefinition = ""
        self.option1Word = ""
        self.option2Word = ""
        self.option3Word = ""
        self.option4Word = ""
        self.correctAnswer = ""
        self.correctAnswerTranslated = ""

        self.defLabel = ctk.CTkLabel(self, text=self.wordDefinition, font=ctk.CTkFont(family="Futura", size=32), anchor="s")
        self.defLabel.grid(row=1, column=1, columnspan=4, sticky="nsew", padx=10, pady=5)

        self.option1Button = ctk.CTkButton(self, text=self.option1Word, corner_radius=50, command=self.chooseOption1, font=ctk.CTkFont(family="Futura", size=20))
        self.option1Button.grid(row=3, column=1, sticky="nsew", padx=25, pady=25)

        self.option2Button = ctk.CTkButton(self, text=self.option2Word, corner_radius=50, command=self.chooseOption2, font=ctk.CTkFont(family="Futura", size=20))
        self.option2Button.grid(row=3, column=2, sticky="nsew", padx=25, pady=25)

        self.option3Button = ctk.CTkButton(self, text=self.option3Word, corner_radius=50, command=self.chooseOption3, font=ctk.CTkFont(family="Futura", size=20))
        self.option3Button.grid(row=3, column=3, sticky="nsew", padx=25, pady=25)

        self.option4Button = ctk.CTkButton(self, text=self.option4Word, corner_radius=50, command=self.chooseOption4, font=ctk.CTkFont(family="Futura", size=20))
        self.option4Button.grid(row=3, column=4, sticky="nsew", padx=25, pady=25)

        self.backButton = ctk.CTkButton(self, text="Learn", corner_radius=50, command=parent.openLearn, font=ctk.CTkFont(family="Futura", size=20))
        self.backButton.grid(row=0, column=1, columnspan=4, sticky="nsew", padx=450, pady=25)

        self.newQuestion()

    def newQuestion(self):
        global seenWords
        global learnedWords
        global masteredWords

        possibleWords = {}
        for word in list(seenWords.keys()):
            if (not (word in list(learnedWords.keys()))) or (not (word in list(masteredWords.keys()))):
                possibleWords[word] = seenWords[word]

        if len(possibleWords) > 0:
            randomWord = random.choice(list(possibleWords.keys()))
            self.correctAnswer = randomWord
            self.correctAnswerTranslated = (possibleWords[randomWord]["translated"]).capitalize()

            options = []

            if len(masteredWords) >= 10:
                options.append((seenWords[random.choice(list(masteredWords.keys()))]["translated"]).capitalize())
            if len(learnedWords) >= 3:
                options.append((seenWords[random.choice(list(learnedWords.keys()))]["translated"]).capitalize())
            if len(seenWords) >= 3:
                if len(options) == 0:
                    options.append((seenWords[random.choice(list(seenWords.keys()))]["translated"]).capitalize())
                    options.append((seenWords[random.choice(list(seenWords.keys()))]["translated"]).capitalize())
                    options.append((seenWords[random.choice(list(seenWords.keys()))]["translated"]).capitalize())
                elif len(options) == 1:
                    options.append((seenWords[random.choice(list(seenWords.keys()))]["translated"]).capitalize())
                    options.append((seenWords[random.choice(list(seenWords.keys()))]["translated"]).capitalize())
                elif len(options) == 2:
                    options.append((seenWords[random.choice(list(seenWords.keys()))]["translated"]).capitalize())
            else:
                options.append((possibleWords[randomWord]["translated"]).capitalize())
                options.append((possibleWords[randomWord]["translated"]).capitalize())
                options.append((possibleWords[randomWord]["translated"]).capitalize())

            options.append((possibleWords[randomWord]["translated"]).capitalize())

            self.updateQuestion(possibleWords[randomWord]["definition"], options)
        else:
            options = ["", "", "", ""]
            self.updateQuestion("YOU HAVE MASTERED ALL THE WORDS THAT YOU HAVE LEARNED!\nGO BACK AND LEARN MORE WORDS!", options)

    def updateQuestion(self, definition, options):
        self.wordDefinition = definition
        self.option1Word = random.choice(options)
        options.remove(self.option1Word)
        self.option2Word = random.choice(options)
        options.remove(self.option2Word)
        self.option3Word = random.choice(options)
        options.remove(self.option3Word)
        self.option4Word = random.choice(options)
        options.remove(self.option4Word)

        self.defLabel.configure(text=self.wordDefinition, text_color="#ffffff")
        self.option1Button.configure(text=self.option1Word)
        self.option2Button.configure(text=self.option2Word)
        self.option3Button.configure(text=self.option3Word)
        self.option4Button.configure(text=self.option4Word)
        
    def chooseOption1(self):
        if self.option1Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    def chooseOption2(self):
        if self.option2Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    def chooseOption3(self):
        if self.option3Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    def chooseOption4(self):
        if self.option4Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    def choseCorrectAnswer(self):
        global seenWords
        global learnedWords
        global masteredWords
        global score

        if self.correctAnswer in list(learnedWords.keys()):
            masteredWords[self.correctAnswer] = {"translated": learnedWords[self.correctAnswer]["translated"], "definition": learnedWords[self.correctAnswer]["definition"], "similar": learnedWords[self.correctAnswer]["similar"]}
            score += 1
        else:
            learnedWords[self.correctAnswer] = {"translated": seenWords[self.correctAnswer]["translated"], "definition": seenWords[self.correctAnswer]["definition"], "similar": seenWords[self.correctAnswer]["similar"]}

        self.defLabel.configure(text="CORRECT!", text_color="#07d400")

        saveData(name=username, newLearnedWords=learnedWords, newMasteredWords=masteredWords, newScore=score)
        checkPosition(username=username)
        self.updateUI()
        self.after(3000, self.newQuestion)

    def choseIncorrectAnswer(self):
        global learnedWords

        if self.correctAnswer in list(learnedWords.keys()):
            learnedWords.pop(self.correctAnswer)

        self.defLabel.configure(text=f"INCORRECT! Correct Answer Was {self.correctAnswerTranslated}", text_color="#d11002")

        saveData(name=username, newLearnedWords=learnedWords)
        self.after(3000, self.newQuestion)

App()