def readDatabase(root):
    file = open(root, 'r')
    tests = []
    for line in file:
        if "example test" in line == False:
            line = line.strip().split(',')
            tests.append(line)
    file.close()
    return tests


if __name__ == "__main__":
    l = readDatabase('database.txt')
    print(l)