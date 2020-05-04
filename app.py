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

def readDatabase(root):
    """
    Purpose: This function reads all the upcoming tests of the user.
    Parameters: This function takes the path of the database file as a string.
    Returns: Returns a list of lists with each list containing the test name (string), test date (datetime.datetime)
             and topic (string).
    """
    file = open(root, 'r')
    tests = []
    for line in file:
        line = line.strip().split(',')
        line[1] = datetime.strptime(line[1], '%b %d %Y %I:%M%p')        # cast the string into a datetime value
        tests.append(line)

    file.close()
    return tests

def updateDatabase(root, tests):
    """
    Purpose: This function updates the database file with the new set of tests.
    Parameters: This function takes the path to the databse file, a string, and the list of tests which is a list of lists.
    Returns: N/A
    """
    file = open(root, 'w')
    for i in range(len(tests)):
        file.write(tests[i][0])
        file.write(',')
        file.write(tests[i][1].strftime("%b %d %Y %I:%M%p"))        # formats the datetime into a string.
        file.write(',')
        file.write(tests[i][2])
        file.write("\n")

    file.close()

def rankTests(tests):
    """
    Purpose: This function sorts the list of tests by the date of the test.
    Parameters: It takes the lists of lists where each sublist contains the test name (string), test date (datetime.datetime)
                and the topic of the test (string).
    Returns: Returns a sorted list of tests where each sublist contains the test name (string), test date (datetime.datetime)
                and the topic of the test (string).
    """
    for i in range(len(tests)):
        indexOfEarliest = i
        for j in range(i+1, len(tests)):
            if tests[j][1] < tests[indexOfEarliest][1]:              # finding the test with the earliest test date
                indexOfEarliest = j

        tests[i], tests[indexOfEarliest] = test[indexOfEarliest], tests[i] # swap

    return tests


def displayWelcome(FIRSTTIME, tests):
    """
    Purpose: Displays the welcome message to the user.
    Parameters: Takes a boolean which tells the app whether the user is new or not and a list of tests.
    Returns: N/A
    """
    if FIRSTTIME:
        print("Welcome to the Study App.")
        print("This app will help you study for any test.")
        print("This app compiles all the resources online and displays them to you in an organized way.")


if __name__ == "__main__":
    APPISACTIVE = True
    FIRSTTIME = False

    database_root = "database.txt"
    # Checks if the user is a first-time user by looking for the database file.
    # If the user is, it creates a new database file and changes the first time user flag.
    if os.path.exists(database_root) == False:
        file = open(database_root, 'w')
        file.close()
        FIRSTTIME = True

    tests = readDatabase(database_root)
    tests = rankTests(tests)
    updateDatabase(database_root, tests)

    displayWelcome(FIRSTTIME, tests)

    currentPage = -1
    pages = {0:"home", 1:"study", 2:"general"}
    while APPISACTIVE:
        page = input("Type for page:")
        currentPage = page

        if currentPage == "home":
            print("This is the home page")
            print("These are your tests (ranked in urgency)")
