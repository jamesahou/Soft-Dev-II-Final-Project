"""
    Description: This is an app that keeps track of the user's tests, compile study resources from sources like YouTube,
                 reminds the user of upcoming tests and tracks the user's progress. It has multiple pages: Home Page,
                 Study Page, General Page. In the Home Page, the app displays a table of tests ranked in urgency and gives
                 the user the option to add additional tests. In the Study Page, the user can select a test to study for
                 and the app will search with the APIs for study resources related to the topic of the test. Finally for
                 the general page, the app displays statistics of the user.
    Author: James Hou
    Date: 5/1/2020
"""
import os
from datetime import datetime
import time
import json
import graphics
import requests
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import threading
from PIL import ImageTk, Image
import requests
from io import BytesIO


class API:
    def __init__(self, api_name):
        self.api_name = api_name
        self.api_key = self.readAPIKey()

    def readAPIKey(self):
        file = open("../api_key.txt", 'r')
        for line in file:
            if self.api_name in line:
                file.close()
                self.api_key = line.strip().split(',')[1]
                return self.api_key


class YouTubeAPI(API):
    def __init__(self):
        super().__init__('yt')
        self.search_url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&sortBy=views&key=%s' % self.api_key

    def searchVideo(self, query, numResults):
        search_url = self.search_url + ("&q=%s" % query) + ("&maxResults=%d" % numResults)
        data = requests.get(search_url)
        data = data.json()
        videos = []
        for video in data["items"]:
            videos.append(Video(video))
        return videos


class Video:
    def __init__(self, video_data):
        self.video_data = video_data
        self.video_id = self.video_data["id"]["videoId"]
        self.video_thumbnailurl = self.video_data["snippet"]["thumbnails"]["default"]['url']
        self.video_title = self.video_data["snippet"]["title"]
        self.video_description = self.video_data["snippet"]["description"]
        self.channel = self.video_data["snippet"]["channelTitle"]
        self.video_thumbnail = self.getThumbnail()
        self.api_key = self.getAPIKey()
        self.base_url = "https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s" % (self.video_id, self.api_key)
        self.link = "https://www.youtube.com/watch?v=%s&feature=youtu.be" % self.video_id
        self.video_duration = self.getVideoDuration()

    def getAPIKey(self):
        yt = YouTubeAPI()
        return yt.readAPIKey()

    def getThumbnail(self):
        response = requests.get(self.video_thumbnailurl)
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        return image

    def resizeThumbnail(self, height, width, method=Image.ANTIALIAS):
        self.video_thumbnail = self.video_thumbnail.resize((height, width), method)
        return self.video_thumbnail

    def getFullDescription(self):
        information_url = self.base_url + "&part=snippet"
        response = requests.get(information_url)
        response = response.json()
        return response["items"][0]["snippet"]["description"]

    def getVideoDuration(self):
        detail_url = self.base_url + "&part=contentDetails"
        response = requests.get(detail_url)
        response = response.json()
        length = response["items"][0]["contentDetails"]["duration"][2:]
        length = length.lower()
        return length


class Test:
    def __init__(self, name, date, description):
        self.name = name
        self.date = date
        self.date_string = self.date.strftime("%b %d %Y %I:%M%p")
        self.description = description

    def summarize(self):
        summary = "Test name: %s Test date: %s Test Description: %s" %(self.name, self.date_string, self.description)
        print(summary)
        return summary


class TestCatalog:
    def __init__(self, doThread=True, root="database.txt"):
        self.root = root
        self.tests = self.readDatabase()
        self.length = len(self.tests)
        self.rankTests()
        self.updateDatabase()

        if doThread:
            thread = threading.Thread(target=self.threadedChecker)
            thread.daemon = True
            thread.start()

    def __getitem__(self, key):
        return self.tests[key]

    def __len__(self):
        return len(self.tests)

    def readDatabase(self,):
        """
        Purpose: This function reads all the upcoming tests of the user.
        Parameters: This function takes the path of the database file as a string.
        Returns: Returns a list of lists with each list containing the test name (string), test date (datetime.datetime)
                 and topic (string).
        """
        file = open(self.root, 'r')
        tests = []
        for line in file:
            line = line.strip().split(',')
            line[1] = datetime.strptime(line[1], '%b %d %Y %I:%M%p')  # cast the string into a datetime value
            tests.append(Test(line[0], line[1], line[2]))

        file.close()
        return tests

    def updateDatabase(self):
        """
        Purpose: This function updates the database file with the new set of tests.
        Parameters: This function takes the path to the databse file, a string, and the list of tests which is a list of lists.
        Returns: N/A
        """
        file = open(self.root, 'w')
        for test in self.tests:
            file.write(test.name)
            file.write(',')
            file.write(test.date_string)
            file.write(',')
            file.write(test.description)
            file.write("\n")

        file.close()

    def rankTests(self):
        """
        Purpose: This function sorts the list of tests by the date of the test.
        Parameters: It takes the lists of lists where each sublist contains the test name (string), test date (datetime.datetime)
                    and the topic of the test (string).
        Returns: Returns a sorted list of tests where each sublist contains the test name (string), test date (datetime.datetime)
                    and the topic of the test (string).
        """
        for i in range(self.length):
            indexOfEarliest = i
            for j in range(i + 1, self.length):
                if self.tests[j].date < self.tests[indexOfEarliest].date:  # finding the test with the earliest test date
                    indexOfEarliest = j

            self.tests[i], self.tests[indexOfEarliest] = self.tests[indexOfEarliest], self.tests[i]  # swap

        return self.tests

    def summarizeTests(self):
        for test in self.tests:
            test.summarize()

    def threadedChecker(self):
        while True:
            valid = []
            for test in self.tests:
                if test.date > datetime.now():
                    valid.append(test)
            self.tests = valid
            self.length = len(self.tests)
            self.updateDatabase()
            self.summarizeTests()
            time.sleep(600)

    def addTest(self, test):
        self.tests.append(test)
        self.updateDatabase()
        return self.tests


class App:
    def __init__(self,):
        self.root = tk.Tk()
        self.root.title("Study App")
        self.appHeight = self.root.winfo_screenheight() * 3 // 5
        self.appWidth = self.root.winfo_screenwidth() * 3 // 5
        self.root.geometry("%dx%d" %(self.appWidth, self.appHeight))

        self.catalog = TestCatalog()

        self.navigator = self.createNavigator()
        self.root.mainloop()


    def createNavigator(self):
        navigator = ttk.Notebook(self.root)
        navigator.add(HomePage(navigator, self.catalog), text="Home", )
        navigator.add(StudyPage(navigator, self.catalog), text="Study")
        navigator.add(SettingsPage(navigator, self.catalog), text="Settings")
        navigator.pack(side="top", fill="both", expand=True)
        navigator.grid_rowconfigure(0, weight=1)
        navigator.grid_columnconfigure(0, weight=1)
        return navigator


class HomePage(tk.Frame):
    def __init__(self, parent, catalog):
        tk.Frame.__init__(self, master=parent, relief=tk.SUNKEN)

        self.pageTitle = tk.Label(self, text="HOME PAGE", font=("Verdana", 24, "bold"))
        self.pageTitle.pack()

        self.table = self.createTable()
        self.catalog = catalog

        self.updateButton = ttk.Button(self, text='UPDATE TABLE', command=self.updateTable())
        self.updateButton.pack()

        self.nameLabel = None
        self.nameEntry = None
        self.dateLabel = None
        self.dateEntry = None
        self.descriptionLabel = None
        self.descriptionEntry = None
        self.createEntries()

        self.addButton = tk.Button(self, text="ADD TEST", command=lambda: self.addTest())
        self.addButton.pack()

    def createTable(self):
        title = tk.Label(self, text="Test List (Ranked In Urgency)", font=("Verdana", 18))
        title.pack()
        columns = ('Rank', 'Test', 'Date', 'Description')
        table = ttk.Treeview(self, columns=('Rank', 'Test', 'Date', 'Description'), show='headings')

        verscrlbar = ttk.Scrollbar(self, orient="vertical", command=table.yview)
        verscrlbar.pack(side='right', fill='x')
        table.configure(xscrollcommand=verscrlbar.set)

        for label in columns:
            table.heading(label, text=label)

        table.pack()
        return table

    def populateTable(self,):
        for i in range(1, len(self.catalog) + 1):
            test = self.catalog[i-1]
            self.table.insert("", "end", values=(i, test.name, test.date_string, test.description))

        self.table.pack()

    def eraseTable(self):
        self.table.delete(*self.table.get_children())

    def updateTable(self):
        self.eraseTable()
        self.populateTable()

    def createEntries(self):
        self.nameLabel = tk.Label(self, text="Name", font=("Verdana", 16))
        self.nameEntry = tk.Entry(self)
        self.dateLabel = tk.Label(self, text="Date (Month Date Year Hour MinuteAM/PM)", font=("Verdana", 16))
        self.dateEntry = tk.Entry(self)
        self.descriptionLabel = tk.Label(self, text="Description", font=("Verdana", 16))
        self.descriptionEntry = tk.Entry(self)

        self.nameLabel.pack()
        self.nameEntry.pack()
        self.dateLabel.pack()
        self.dateEntry.pack()
        self.descriptionLabel.pack()
        self.descriptionEntry.pack()

    def addTest(self):
        name = self.nameEntry.get()
        date = self.dateEntry.get()
        description = self.descriptionEntry.get()
        try:
            date = datetime.strptime(date, '%b %d %Y %I:%M%p')
            if date < datetime.now():
                messagebox.showwarning("Warning", "Please enter a date in the future")
            else:
                self.catalog.addTest(Test(name, date, description))
                self.updateTable()
                self.nameEntry.delete(0, 'end')
                self.dateEntry.delete(0, 'end')
                self.descriptionEntry.delete(0, 'end')
        except ValueError:
            messagebox.showwarning("Warning", "Your date entry did not match Month Date Year Hour MinuteAM/PM format.\nPlease try again")



class StudyPage(tk.Frame):
    def __init__(self, parent, catalog):
        tk.Frame.__init__(self, master=parent)
        label = tk.Label(master=self, text="Study", font=("Verdana", 24))
        label.pack()


class SettingsPage(tk.Frame):
    def __init__(self, parent, catalog):
        tk.Frame.__init__(self, master=parent)
        label = tk.Label(master=self, text="Settings", font=("Verdana", 24))
        label.pack()


if __name__ == "__main__":
    APPISACTIVE = True
    FIRSTTIME = False

    database_path = "database.txt"
    settings_path = "settings.txt"


    # Checks if the user is a first-time user by looking for the database file.
    # If the user is, it creates a new database file and changes the first time user flag.
    if os.path.exists(database_path) == False:
        file = open(database_path, 'w')
        file.close()
        FIRSTTIME = True

    app = App()

