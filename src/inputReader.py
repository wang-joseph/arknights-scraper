import re, sys

# created 01/07/2020
# last edited: 01/07/2020
# version: 1.0.1
# author: Joseph Wang (EmeraldEntities)

def readLineFromFile(file):
  with open(file, "r") as f:
    result = f.readline()

  return result

def readLinesIntoDict(file):
  newDict = {}

  with open(file, "r") as f:
    currentLine = f.readline()

    while currentLine != "\n":
      lineInfo = re.split(r'\s+',currentLine.rstrip())

      lineInfo[0] = lineInfo[0].replace('+', ' ')
      lineInfo[1] = lineInfo[1].replace('+', ' ')

      newDict[lineInfo[0]] = lineInfo[1]

      currentLine = f.readline()
  return newDict

if __name__ == "__main__":
  sys.stdout.write("Wrong python file to run! The main file to run is `scraper.py`.\n\n")