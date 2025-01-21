# Install os, asyncio, googletrans, customtkinter, json, and random before running the program

# Import all the modules that are necessary for the program
import os
import asyncio
from googletrans import Translator
import customtkinter as ctk
import json
import random

# Make an instance of the Translator class from the googletrans module
translator = Translator()

# Load the words.json and store the values in four lists - languageKeys, easyWords, mediumWords, and hardWords 
# - using a procedure, so that it can be called when needed
def loadWords():
    # Make variables global so that they can be accessed and modified from anywhere in the code
    global languageKeys
    global easyWords
    global mediumWords
    global hardWords

    # Load the words.json file
    words = json.load(open("words.json"))

    # Store the values in the global variables
    languageKeys = words["languageKeys"]
    easyWords = words["easy"]
    mediumWords = words["medium"]
    hardWords = words["hard"]

# Load the user's data using the name of the user as the parameter and store the values in global variables 
# - languageLearning, difficulty, score, position, seenWords, learnedWords, and masteredWords - using a procedure,
# so that it can be called when needed
def loadData(name):
    # Make variables global so that they can be accessed and modified from anywhere in the code
    global languageLearning
    global difficulty
    global score
    global position
    global seenWords
    global learnedWords
    global masteredWords

    # Open the user's data file
    data = json.load(open(f"data/{name.lower().replace(" ", "_")}.json"))

    # Store the data in the global variables
    languageLearning = data["languageLearning"]
    difficulty = data["difficulty"]
    score = data["score"]
    position = data["position"]
    seenWords = data["seenWords"]
    learnedWords = data["learnedWords"]
    masteredWords = data["masteredWords"]

# Save or create the user's data depending on the parameters that are passed to the procedure and 
# store the values in the user's data file and global variables
def saveData(
        name, 
        newLanguage="", 
        newDifficulty="", 
        newScore=0, 
        newPosition=0, 
        newSeenWords={}, 
        newLearnedWords={}, 
        newMasteredWords={}, 
        create=False):
    # Make variables global so that they can be accessed and modified from anywhere in the code
    global username
    global languageLearning
    global difficulty
    global score
    global position
    global seenWords
    global learnedWords
    global masteredWords
    
    # If the user's file needs to be created, store default values in the newData variable
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

    # If the user's file doesn't need to be created, load the user's data from the file and store it in the newData variable
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

    # If the parameters - newLanguage, newDifficulty, newScore, newPosition, newSeenWords, newLearnedWords, or newMasteredWords 
    # - are passed to the procedure without the default values, update the newData variable with the new values
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

    # If the name of the user that is passed through the parameter is the same as the global variable username (the current user), 
    # update the global variables with the new values
    if name == username:
        languageLearning = newData["languageLearning"]
        difficulty = newData["difficulty"]
        score = newData["score"]
        position = newData["position"]
        seenWords = newData["seenWords"]
        learnedWords = newData["learnedWords"]
        masteredWords = newData["masteredWords"]

    # Open the user's new file or already existing file and dump the newData into it
    with open(f"data/{name.lower().replace(" ", "_")}.json", "w") as file:
        json.dump(newData, file)

# Check if the user's position in the leaderboard has changed and if it has, update the values in all the files
def checkPosition(username):
    # Make variables global so that they can be accessed and modified from anywhere in the code
    global position
    global score

    # Get a list of all the files in the data folder
    files = os.listdir("data")

    # If the user's score is 0 (newly created file with the default value), set the position to the length of the files
    if score == 0:
        position = len(files)
        saveData(name=username, newPosition=position)

    # Get a dictionary of all the scores of the files list with the filename as the key
    scores = {}
    for filename in files:
        scores[filename] = json.load(open(f"data/{filename}"))["score"]

    # Sort the scores dictionary by the values in descending order by first converting it to a list to actually sort the values 
    # and then reconverting it into a dictionary to know the filenames for each value in sortedScoresList
    sortedScoresList = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    sortedScores = {}
    for sortedScore in sortedScoresList:
        sortedScores[sortedScore[0]] = sortedScore[1]
    sortedScoresKeyList = list(sortedScores.keys())

    # For every filename in the sortedScores dictionary, check if the position in the file is the same as the position 
    # in the sortedScoresKeyList and if it isn't, update the position in the file
    for filename, score in sortedScores.items():
        positionInFile = json.load(open(f"data/{filename}"))["position"]
        if positionInFile != (sortedScoresKeyList.index(filename)+1):
            saveData(name=(filename.replace(".json", "")), newPosition=(sortedScoresKeyList.index(filename)+1))

# Translate a list of words using the googletrans's Translator class that was stored as the translator variable 
# and return a dictionary with the original word as the key and the translated word, definition, and similar words as the values
async def translateList(list):
    translatedWords = {}
    translations = await translator.translate([word for word in list], dest=languageLearning, src="en")
    
    # For each translation that is gotten from the googletrans API, store the translated word, definition, 
    # and similar words in the translatedWords dictionary with the original word as the key
    for index, translation in enumerate(translations):
        translatedWord = translation.extra_data["translation"][0][0]
        wordDefinition = translation.extra_data["definitions"][0][1][0][0]
        try:
            similarWords = translation.extra_data["all-translations"][0][1][1:]
        except:
            similarWords = []
        
        translatedWords[list[index]] = {"translated": translatedWord, "definition": wordDefinition, "similar": similarWords}
    
    # Return the dictionary with the translated words
    return translatedWords

# Make the App class, using customtkinter, that acts as the window for the entire program
class App(ctk.CTk):
    # Initialzie the ctk.CTk herited class and set the window's title, color, and zoom state
    def __init__(self):
        super().__init__(fg_color="#0B192C")
        self.title("V-Lang: Unlock the Power of a Language, One Word at a Time!")
        self.geometry("1200x600")
        self.minsize(1000, 500)
        self.after(0, lambda:self.state("zoomed"))

        # Set up a grid system for the App class
        self.columnconfigure(0, weight=1, uniform="a")
        self.rowconfigure(0, weight=1, uniform="a")
        self.rowconfigure(1, weight=5, uniform="a")

        # Make the username variable global so that it can be accessed and modified from anywhere in the code
        global username

        # Load the words frm the words.json file using the loadWords procedure
        loadWords()

        # Create an instance of the details frame
        self.detailsFrame = detailsFrame(self)

        # Create an instance of the login frame
        self.loginFrame = loginFrame(self)
        self.loginFrame.submitButton.configure(command=self.getUser)

        # Run the mainloop of the App class
        self.mainloop()

    # Get the user's data from the input from the loginFrame
    def getUser(self, name="", *args):
        # Make the username variable global so that it can be accessed and modified from anywhere in the code
        global username

        # Check if the user has a file or not and see if the user inputted a name or not. If they did, set self.username to that
        hasFile = False
        if name == "":
            if self.loginFrame.nameEntry.get():
                self.username = self.loginFrame.nameEntry.get()
        else:
            self.username = name

        username = self.username

        # If the user has a file, get the filename of the file and set hasFile to True
        for filename in os.listdir("data"):
            if filename == self.username.lower().replace(" ", "_") + ".json":
                hasFile = True

        # If the user has a file, load the user's data and update the UI with the new values
        if hasFile:
            loadData(self.username)
            self.updateUI()
            
            # Destory the loginFrame
            self.loginFrame.destroy()

            # Translate all the words using the translateList procedure
            allWords = easyWords + mediumWords + hardWords
            allWordsTranslated = asyncio.run(translateList(allWords))
            
            self.easyWordsTranslated = {}
            self.mediumWordsTranslated = {}
            self.hardWordsTranslated = {}

            # Store the words in the allWordsTranslated dictionary into the easyWordsTranslated, mediumWordsTranslated, 
            # and hardWordsTranslated dictionaries based on the difficulty of the word
            index = 0
            for word in allWordsTranslated:
                if index <= (len(easyWords) - 1):
                    self.easyWordsTranslated[word] = {
                        "translated": allWordsTranslated[word]["translated"], 
                        "definition": allWordsTranslated[word]["definition"], 
                        "similar": allWordsTranslated[word]["similar"]
                    }
                elif index <= (((len(easyWords) + len(mediumWords))) - 1):
                    self.mediumWordsTranslated[word] = {
                        "translated": allWordsTranslated[word]["translated"], 
                        "definition": allWordsTranslated[word]["definition"], 
                        "similar": allWordsTranslated[word]["similar"]
                    }
                elif index <= (((len(easyWords) + len(mediumWords) + len(hardWords))) - 1):
                    self.hardWordsTranslated[word] = {
                        "translated": allWordsTranslated[word]["translated"], 
                        "definition": allWordsTranslated[word]["definition"], 
                        "similar": allWordsTranslated[word]["similar"]
                    }
                index += 1

            # Create a vocabularyWordFrame instance
            self.vocabularyWordFrame = vocabularyWordFrame(self)
        # If the user doesn't have a file, ask the user what language they want to learn and give the user a dropdown to input that
        else:
            self.loginFrame.nameLabel.configure(text="Choose The Language You Want to Learn:")
            self.loginFrame.nameEntry.destroy()
            self.loginFrame.languageDropdown.grid(row=2, column=0, sticky="nsew", padx=350, pady=10)
            self.loginFrame.submitButton.configure(command=self.setLanguage)

    # Set the language that was given by the user from the loginFrame to the language code using the languageKeys dictionary 
    # and save it in the user's file
    def setLanguage(self, *args):
        languageInput = self.loginFrame.languageDropdown.get().lower()

        for key, language in languageKeys.items():
                if language == languageInput:
                    languageCode = key

        saveData(name=self.username, newLanguage=languageCode, create=True)
        self.getUser(name=self.username)

    # Update the UI with new values
    def updateUI(self):
        checkPosition(self.username)

        # Format the languageLearning variable to be in full form instead of the language code and capitalize it
        languageLearningFormatted = ""
        for key, language in languageKeys.items():
            if languageLearning == key:
                languageLearningFormatted = language.capitalize()

        # Format the socre based on if the score is equal to one or not
        scoreFormatted = str(score)
        if score == 1:
            scoreFormatted += " Word Mastered"
        else:
            scoreFormatted += " Words Mastered"

        # Position the format based on the ending digit of the position or the position itself
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

        # Set the labels to the new values
        self.detailsFrame.languageLabel.configure(text=languageLearningFormatted)
        self.detailsFrame.difficultyLabel.configure(text=difficulty.capitalize())
        self.detailsFrame.usernameLabel.configure(text=self.username.capitalize())
        self.detailsFrame.scoreLabel.configure(text=scoreFormatted)
        self.detailsFrame.positionLabel.configure(text=positionFormatted)
    
    # Open the practiceWordFrame and destroy the vocabularyWordFrame
    def openPractice(self):
        # Make the seenWords variable global so that it can be accessed and modified from anywhere in the code
        global seenWords

        # If the current word isn't in the seenWords dictionary, add it to the dictionary
        if not (self.vocabularyWordFrame.currentWord in list(seenWords.keys())):
            seenWords[self.vocabularyWordFrame.currentWord] = {
                "translated": self.vocabularyWordFrame.translatedWord, 
                "definition": self.vocabularyWordFrame.wordDefinition, 
                "similar": self.vocabularyWordFrame.similarWords
            }
        
        # Create the practiceWordFrame instance and destroy the vocabularyWordFrame instance
        self.practiceWordFrame = practiceWordFrame(self, self.updateUI)
        self.vocabularyWordFrame.destroy()
    
    # Create the vocabularyWordFrame instance and destroy the practiceWordFrame
    def openLearn(self):
        self.vocabularyWordFrame = vocabularyWordFrame(self)
        self.practiceWordFrame.destroy()

# Show the basic information of the user, such as the language they are learning, the difficulty they are on, 
# their username, the score they have, and the position they are in the leaderboard
class detailsFrame(ctk.CTkFrame):
    # Initialize the ctk.CTkFrame class, set the frame's color to transparent, and grid it to the App class
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid(row=0, column=0, sticky="nsew")

        # Create the grid system for the detailsFrame
        self.columnconfigure(0, weight=1, uniform="b")
        self.columnconfigure(1, weight=4, uniform="b")
        self.columnconfigure(2, weight=1, uniform="b")
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform="b")

        # Create the languageLabel, difficultyLabel, usernameLabel, scoreLabel, and positionLabel labels 
        # and grid them to the detailsFrame grid system
        self.languageLabel = ctk.CTkLabel(self, text="V-Lang", font=ctk.CTkFont(family="Futura", size=52), anchor="s")
        self.languageLabel.grid(row=0, column=1, rowspan=3, sticky="nsew", pady=5)

        self.difficultyLabel = ctk.CTkLabel(
            self, 
            text="Unlock the Power of a Language, One Word at a Time!", 
            font=ctk.CTkFont(family="Futura", size=18), anchor="n")
        self.difficultyLabel.grid(row=3, column=1, sticky="nsew", pady=5)

        self.usernameLabel = ctk.CTkLabel(self, text="Username", font=ctk.CTkFont(family="Futura", size=18), anchor="se")
        self.usernameLabel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=20, pady=10)

        self.scoreLabel = ctk.CTkLabel(self, text="0 Words Mastered", font=ctk.CTkFont(family="Futura", size=18), anchor="sw")
        self.scoreLabel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=20, pady=10)

        self.positionLabel = ctk.CTkLabel(self, text="0th Place", font=ctk.CTkFont(family="Futura", size=18), anchor="nw")
        self.positionLabel.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=20, pady=10)

# Get the login input from the user
class loginFrame(ctk.CTkFrame):
    # Initialize the ctk.CTkFrame class, set the frame's color, and grid it to the App class
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        # Create the grid system for the loginFrame
        self.columnconfigure(0, weight=1, uniform="c")
        self.rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="c")

        # Create the nameLabel and nameEntry and grid them to the loginFrame grid system
        self.nameLabel = ctk.CTkLabel(
            self, 
            text="Enter Your Username:\n(new data will be created if data does not already exist)", 
            font=ctk.CTkFont(family="Futura", size=20))
        self.nameLabel.grid(row=1, column=0, sticky="nsew", padx=250, pady=10)

        self.nameEntry = ctk.CTkEntry(
            self, 
            corner_radius=10, 
            fg_color="#333333", 
            border_width=0, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.nameEntry.grid(row=2, column=0, sticky="nsew", padx=350, pady=10)

        # Convert the languageKeys dictionary values to a list and capitalize them, so they look nice in the dropdown
        languageKeysList = list(languageKeys.values())
        for index, languageKey in enumerate(languageKeysList):
            languageKeysList[index] = languageKey.capitalize()
        
        # Create the languageDropdown and the submitButton widgets and grid the submitButton to the loginFrame grid system
        self.languageDropdown = ctk.CTkOptionMenu(
            self, 
            values=languageKeysList, 
            corner_radius=10, 
            fg_color="#333333", 
            button_color="#333333", 
            button_hover_color="#333333",
            font=ctk.CTkFont(family="Futura", size=20))

        self.submitButton = ctk.CTkButton(self, text="Submit", corner_radius=10, font=ctk.CTkFont(family="Futura", size=20))
        self.submitButton.grid(row=3, column=0, sticky="nsew", padx=350, pady=10)

# Teach the user vocabulary words and their definitions using this ctk.CTkFrame 
class vocabularyWordFrame(ctk.CTkFrame):
    # Initialize the ctk.CTkFrame class, set the frame's color, and grid it to the App class
    def __init__(self, parent):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        # Create the grid system for the vocabularyWordFrame
        self.columnconfigure(0, weight=1, uniform="d")
        self.columnconfigure(1, weight=8, uniform="d")
        self.columnconfigure(2, weight=1, uniform="d")
        self.rowconfigure(0, weight=2, uniform="d")
        self.rowconfigure(1, weight=3, uniform="d")
        self.rowconfigure(2, weight=1, uniform="d")
        self.rowconfigure(3, weight=3, uniform="d")
        self.rowconfigure(4, weight=2, uniform="d")

        # Make variables global so that they can be accessed and modified from anywhere in the code
        global difficulty
        global seenWords

        # Set the self.easyWordsTranslated, self.mediumWordsTranslated, and self.hardWordsTranslated variables 
        # to the ones from the parent (App) class
        self.easyWordsTranslated = parent.easyWordsTranslated
        self.mediumWordsTranslated = parent.mediumWordsTranslated
        self.hardWordsTranslated = parent.hardWordsTranslated

        # Choose the wordList that needs to be used depending on the user's difficulty level
        if difficulty == "easy":
            self.wordList = easyWords
            self.wordDict = self.easyWordsTranslated
        elif difficulty == "medium":
            self.wordList = mediumWords
            self.wordDict = self.mediumWordsTranslated
        elif difficulty == "hard":
            self.wordList = hardWords
            self.wordDict = self.hardWordsTranslated

        # Create placeholder values for the labels to use
        self.currentWords = []
        self.translatedWord = ""
        self.currentWord = ""
        self.wordDefinition = ""
        self.similarWords = ""
        
        # If the user hasn't seen all the words yet, get a new word and set the labels to the new values
        if difficulty != "viewed":
            self.newWord()

        # Create the wordLabel, originalWordLabel, defLabel, similarWordsLabel, nextButton, previousButton, and practiceButton 
        # and grid them to the vocabularyWordFrame grid system
        self.wordLabel = ctk.CTkLabel(self, text=self.translatedWord, font=ctk.CTkFont(family="Futura", size=42), anchor="s")
        self.wordLabel.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        self.originalWordLabel = ctk.CTkLabel(
            self, 
            text=f"({self.currentWord})", 
            font=ctk.CTkFont(family="Futura", size=16), 
            anchor="n")
        self.originalWordLabel.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)

        self.defLabel = ctk.CTkLabel(self, text=self.wordDefinition, font=ctk.CTkFont(family="Futura", size=20), anchor="n")
        self.defLabel.grid(row=3, column=1, sticky="nsew", pady=5)

        self.similarWordsLabel = ctk.CTkLabel(self, text=self.similarWords, font=ctk.CTkFont(family="Futura", size=18))
        self.similarWordsLabel.grid(row=4, column=1, sticky="nsew", pady=5)

        self.nextButton = ctk.CTkButton(
            self, 
            text=">", 
            corner_radius=50, 
            command=self.nextWord, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.nextButton.grid(row=0, column=2, sticky="nes", padx=25, pady=25)
        
        self.previousButton = ctk.CTkButton(
            self, 
            text="<", 
            corner_radius=50, 
            command=self.previousWord, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.previousButton.grid(row=0, column=0, sticky="nsw", padx=25, pady=25)

        self.practiceButton = ctk.CTkButton(
            self, 
            text="Practice", 
            corner_radius=50, 
            command=parent.openPractice, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.practiceButton.grid(row=0, column=1, sticky="nsew", padx=300, pady=25)

        # If the user has already seen all the words, set the labels to the value that tells them to go practice them
        if difficulty == "viewed":
            self.wordLabel.configure(text="YOU HAVE SEEN ALL THE WORDS!\nPRACTICE THEM TO REMEMBER THEM!")
            self.originalWordLabel.configure(text="")
            self.defLabel.configure(text="")
            self.similarWordsLabel.configure(text="")
    
    # Choose a new word for the user to learn
    def newWord(self):
        # Make variables global so that they can be accessed and modified from anywhere in the code
        global seenWords
        global difficulty

        # Try to get a new word for the user to learn and set the labels to the new values
        try:
            # Keep choosing a new word until we get a word that the user hasn't seen yet or increase the 
            # difficulty level of the user if they have seen all the words from their current difficulty level
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
            
            # If the user has already seen all the words, set the labels to the value that tells them to go practice them
            if difficulty == "viewed":
                self.wordLabel.configure(text="YOU HAVE SEEN ALL THE WORDS!\nPRACTICE THEM TO REMEMBER THEM!")
                self.originalWordLabel.configure(text="")
                self.defLabel.configure(text="")
                self.similarWordsLabel.configure(text="")
            # If the user hasn't already seen all the words, set the labels to the new word's values if needed
            elif difficulty != "viewed":
                self.translatedWord = self.wordDict[self.currentWord]["translated"]
                self.wordDefinition = self.wordDict[self.currentWord]["definition"]
                self.similarWords = self.wordDict[self.currentWord]["similar"]

                # Format the defintion, so that it is on multiple lines
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

                # Format the similar words, so that they are on multiple lines if needed
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
        # If there is an error, try to get a new word again
        except Exception as e:
            self.newWord()

    # Update the values in the labels
    def updateWord(self, word=""):
        # Make variables global so that they can be accessed and modified from anywhere in the code
        global username
        global seenWords

        # If word does not equal nothing, set the values to the new word's values
        if word != "":
            wordData = seenWords[word]

            self.translatedWord = wordData["translated"]
            self.currentWord = self.currentWords[self.currentWords.index(word)]
            self.wordDefinition = wordData["definition"]
            self.similarWords = wordData["similar"]
        
        # Set the labels to the new values
        self.wordLabel.configure(text=self.translatedWord)
        self.originalWordLabel.configure(text=f"({self.currentWord})")
        self.defLabel.configure(text=self.wordDefinition)
        self.similarWordsLabel.configure(text=self.similarWords)

        # Save the new data using the saveData procedure
        saveData(name=username, newSeenWords=seenWords)

    # Go to the next word in the user's current words they are looking at
    def nextWord(self):
        # Make variables global so that they can be accessed and modified from anywhere in the code
        global seenWords
        global difficulty

        # If the current word isn't in the currentWords list, add it to the list
        if not(self.currentWord in self.currentWords):
            self.currentWords.append(self.currentWord)
        # Get the index of the current word in the currentWords list
        currentWordIndex = self.currentWords.index(self.currentWord)
        # If the current word is the last one that the user has seen, add the current word to the seenWords dictionary 
        # and get a new word
        if currentWordIndex == (len(self.currentWords)-1):
            seenWords[self.currentWord] = {
                "translated": self.translatedWord, 
                "definition": self.wordDefinition, 
                "similar": self.similarWords
            }
            self.newWord()
            # If the user hasn't seen all the words yet, update the word
            if difficulty != "viewed":
                self.updateWord()
        else:
            # If the current word isn't the last one that the user has seen, update the word to the next word 
            # in the currentWords list
            self.updateWord(self.currentWords[currentWordIndex+1])

    # Go to the previous word in the user's current words that they are looking at
    def previousWord(self):
        # Make the seenWords variable global so that it can be accessed and modified from anywhere in the code
        global seenWords

        # Add the current word to the currentWords list
        self.currentWords.append(self.currentWord)
        # Get the index of the current word in the currentWords list
        currentWordIndex = self.currentWords.index(self.currentWord)
        # If the current word is the last one the user has seen, add the current word to the seenWords dictionary 
        # and update the word to the previous word in the currentWords list
        if currentWordIndex == (len(self.currentWords)-1):
            seenWords[self.currentWord] = {
                "translated": self.translatedWord, 
                "definition": self.wordDefinition, 
                "similar": self.similarWords
            }
            self.updateWord(self.currentWords[currentWordIndex-1])
        # If the current word is not the first one, remove the current word from the current words list 
        # and update the word to the previous word
        elif currentWordIndex != 0:
            self.currentWords.pop()
            self.updateWord(self.currentWords[currentWordIndex-1])
        # If the current word is the first one, remove the current word from the current words list
        else:
            self.currentWords.pop()

    # Change the difficulty level of the user
    def changeDifficulty(self):
        # Make variables global so that they can be accessed and modified from anywhere in the code
        global username
        global difficulty

        # Change the difficulty level of the user and set the wordList and wordDict to the new values 
        # depending on the current values
        if difficulty == "easy":
            difficulty = "medium"
            self.wordList = mediumWords
            self.wordDict = self.mediumWordsTranslated
        elif difficulty == "medium":
            difficulty = "hard"
            self.wordList = hardWords
            self.wordDict = self.hardWordsTranslated
        # If the user has seen all the hardWords or the difficuly is already set to viewed, 
        # set the wordLabel to the message telling the user to go practice the words
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

        # Save the new difficulty data using the saveData procedure
        saveData(name=username, newDifficulty=difficulty)

# Allow the user to practice and master the user's seenWords and learnedWords using this ctk.CTkFrame
class practiceWordFrame(ctk.CTkFrame):
    # Initialize the ctk.CTkFrame class, set the frame's color, and grid it to the App class
    def __init__(self, parent, updateUI):
        super().__init__(parent, fg_color="#1E3E62", corner_radius=30)
        self.grid(row=1, column=0, sticky="nsew", padx=120, pady=30)

        # Create the grid system for the practiceWordFrame class
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

        # Store the updateUI procedure that was given as input to the class as self.updateUI
        self.updateUI = updateUI

        # Create placeholder values for the labels and buttons
        self.wordDefinition = ""
        self.option1Word = ""
        self.option2Word = ""
        self.option3Word = ""
        self.option4Word = ""
        self.correctAnswer = ""
        self.correctAnswerTranslated = ""

        # Create the defLabel, option1Button, option2Button, option3Button, option4Button, and learnButton 
        # and grid them to the practiceWordFrame grid system
        self.defLabel = ctk.CTkLabel(self, text=self.wordDefinition, font=ctk.CTkFont(family="Futura", size=32), anchor="s")
        self.defLabel.grid(row=1, column=1, columnspan=4, sticky="nsew", padx=10, pady=5)

        self.option1Button = ctk.CTkButton(
            self, 
            text=self.option1Word, 
            corner_radius=50, 
            command=self.chooseOption1, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.option1Button.grid(row=3, column=1, sticky="nsew", padx=25, pady=25)

        self.option2Button = ctk.CTkButton(
            self, 
            text=self.option2Word, 
            corner_radius=50, 
            command=self.chooseOption2, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.option2Button.grid(row=3, column=2, sticky="nsew", padx=25, pady=25)

        self.option3Button = ctk.CTkButton(
            self, 
            text=self.option3Word, 
            corner_radius=50, 
            command=self.chooseOption3, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.option3Button.grid(row=3, column=3, sticky="nsew", padx=25, pady=25)

        self.option4Button = ctk.CTkButton(
            self, 
            text=self.option4Word, 
            corner_radius=50, 
            command=self.chooseOption4, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.option4Button.grid(row=3, column=4, sticky="nsew", padx=25, pady=25)

        self.learnButton = ctk.CTkButton(
            self, 
            text="Learn", 
            corner_radius=50, 
            command=parent.openLearn, 
            font=ctk.CTkFont(family="Futura", size=20))
        self.learnButton.grid(row=0, column=1, columnspan=4, sticky="nsew", padx=300, pady=25)

        # Choose a new question for the user to answer using the newQuestion procedure
        self.newQuestion()

    # Choose a new question for the user to answer
    def newQuestion(self):
        # Make variables global so that they can be accessed and modified from anywhere in the code
        global seenWords
        global learnedWords
        global masteredWords

        # Create a dictionary of the words that the user hasn't learned or mastered yet by checking if they are not 
        # in the learnedWords or masteredWords
        possibleWords = {}
        for word in list(seenWords.keys()):
            if (not (word in list(learnedWords.keys()))) or (not (word in list(masteredWords.keys()))):
                possibleWords[word] = seenWords[word]

        # If there is at least one word in the possibleWords dictionary, choose a random word from the dictionary 
        # and set the correctAnswer and correctAnswerTranslated variables to the word's values
        if len(possibleWords) > 0:
            randomWord = random.choice(list(possibleWords.keys()))
            self.correctAnswer = randomWord
            self.correctAnswerTranslated = (possibleWords[randomWord]["translated"]).capitalize()

            # Create a list called options that will store the answer choices for this question
            options = []

            # Add words from either the masteredWords, learnedWords, or seenWords lists depending on how many words 
            # are in each list
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
            # If there are not enough words in either list, add random words from the possibleWords dictionary
            else:
                options.append((possibleWords[randomWord]["translated"]).capitalize())
                options.append((possibleWords[randomWord]["translated"]).capitalize())
                options.append((possibleWords[randomWord]["translated"]).capitalize())

            # Add the correct answer to the options list
            options.append((possibleWords[randomWord]["translated"]).capitalize())

            # Update the queston using the definition of the word and the options list
            self.updateQuestion(possibleWords[randomWord]["definition"], options)
        # If there are no words in the possibleWords dictionary, tell the user that they have mastered all the words 
        # they have learned and tell them to go learn more words
        else:
            options = ["", "", "", ""]
            self.updateQuestion("YOU HAVE MASTERED ALL THE WORDS THAT YOU HAVE LEARNED!\nGO BACK AND LEARN MORE WORDS!", options)

    # Update the question with the new definition and options in a random order
    def updateQuestion(self, definition, options):
        # Update the variables with the new definition and options in a random order
        self.wordDefinition = definition
        self.option1Word = random.choice(options)
        options.remove(self.option1Word)
        self.option2Word = random.choice(options)
        options.remove(self.option2Word)
        self.option3Word = random.choice(options)
        options.remove(self.option3Word)
        self.option4Word = random.choice(options)
        options.remove(self.option4Word)

        # Update the labels and buttons with the new values
        self.defLabel.configure(text=self.wordDefinition, text_color="#ffffff")
        self.option1Button.configure(text=self.option1Word)
        self.option2Button.configure(text=self.option2Word)
        self.option3Button.configure(text=self.option3Word)
        self.option4Button.configure(text=self.option4Word)
    
    # Check if the user chose the correct answer or not if they choseOption1 and run the necessary procedure based on that
    def chooseOption1(self):
        if self.option1Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    # Check if the user chose the correct answer or not if they choseOption2 and run the necessary procedure based on that
    def chooseOption2(self):
        if self.option2Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    # Check if the user chose the correct answer or not if they choseOption3 and run the necessary procedure based on that
    def chooseOption3(self):
        if self.option3Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    # Check if the user chose the correct answer or not if they choseOption4 and run the necessary procedure based on that
    def chooseOption4(self):
        if self.option4Word == self.correctAnswerTranslated:
            self.choseCorrectAnswer()
        else:
            self.choseIncorrectAnswer()

    # Add the current question word to the correct dictionary based on if they learned or mastered it, save their data, 
    # and tell the user that they got it correct
    def choseCorrectAnswer(self):
        # Make variables global so that they can be accessed and modified from anywhere in the code
        global seenWords
        global learnedWords
        global masteredWords
        global score

        # Add the current question word to the correct dictionary based on if they learned or mastered it
        if self.correctAnswer in list(learnedWords.keys()):
            masteredWords[self.correctAnswer] = {
                "translated": learnedWords[self.correctAnswer]["translated"], 
                "definition": learnedWords[self.correctAnswer]["definition"], 
                "similar": learnedWords[self.correctAnswer]["similar"]
            }
            score += 1
        else:
            learnedWords[self.correctAnswer] = {
                "translated": seenWords[self.correctAnswer]["translated"], 
                "definition": seenWords[self.correctAnswer]["definition"], 
                "similar": seenWords[self.correctAnswer]["similar"]
            }

        # Tell the user that they got it correct by changing the defLabel
        self.defLabel.configure(text="CORRECT!", text_color="#07d400")

        # Save the user's data, check their position in the leaderboard, update the UI, and choose a new question after three seconds
        saveData(name=username, newLearnedWords=learnedWords, newMasteredWords=masteredWords, newScore=score)
        checkPosition(username=username)
        self.updateUI()
        self.after(3000, self.newQuestion)

    # Remove the current question word from the learnedWords dictionary if the word is in the user's learnedWords dicitonary, 
    # save their data, and tell the user that they got it incorrect and what the correct answer was
    def choseIncorrectAnswer(self):
        # Make the learnedWords variable global so that it can be accessed and modified from anywhere in the code
        global learnedWords

        # If the current question word is in the learnedWords dictionary, remove it from the learnedWords dictionary
        if self.correctAnswer in list(learnedWords.keys()):
            learnedWords.pop(self.correctAnswer)

        # Tell the user that they got it incorrect and what the correct answer was by changing the defLabel
        self.defLabel.configure(text=f"INCORRECT! Correct Answer Was {self.correctAnswerTranslated}", text_color="#d11002")

        # Save the user's data and choose a new question after three seconds
        saveData(name=username, newLearnedWords=learnedWords)
        self.after(3000, self.newQuestion)

# Create an instance of the App class, so that the program runs
App()