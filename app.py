def readDatabase(root):
    """
    Purpose: This function reads all the
    Parameters:
    Returns:
    """
    file = open(root, 'r')
    tests = []
    FIRSTTIME = False
    for line in file:
        if "first-time" in line:
              FIRSTTIME = True
        else:
            line = line.strip().split(',')
            tests.append(line)

    file.close()
    return tests, FIRSTTIME

def updateDatabase(root, tests):
    file = open(root, 'w')
    for i in range(len(tests)):
        file.write(','.join(tests[i]) + "\n")

    file.close()

def displayWelcome(FIRSTTIME, tests):
    if FIRSTTIME:
        print("Welcome to the Study App.")
        print("This app will help you study for any test.")
        print("This app compiles all the resources online and displays them to you in an organized way.")
        print("Here are your ")

if __name__ == "__main__":
    APPISACTIVE = True
    database = "database.txt"
    tests, FIRSTTIME = readDatabase(database)
    displayWelcome(FIRSTTIME, tests)
    if FIRSTTIME:
        updateDatabase(database, tests)
        FIRSTTIME = False

    CHANGEISMADE = False
