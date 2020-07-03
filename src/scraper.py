#!/usr/bin/env python3

import requests, argparse, sys, re
from halo import Halo # extremely important
from bs4 import BeautifulSoup

from detailedSearchFunctions import findTalents, findBaseSkills, findStats, findSkills
from inputReader import readLinesIntoDict, readLineFromFile

# created 06/06/2020
# last edited: 02/07/2020
# version: 1.4.0
# author: Joseph Wang (EmeraldEntities)

### FUNCTIONS ########################
def initializeArguments():
  # Using the argparse library, initializes cmd arguments
  parser = argparse.ArgumentParser(description="Find information about any operator in Arknights!")
  parser.add_argument("operator", help="The operator you want information for. For spaces, use a '-' in place of the space. No special characters.")
  parser.add_argument("-t", "--talent", help="Displays the specified operator's talent.", action="store_true")
  parser.add_argument("-s", "--skills", help="Displays the specified operator's skills.", action="store_true")
  parser.add_argument("-u", "--upgrades", help="Displays the specified operator's upgrade stages and what this operator needs. In-dev", action="store_true")
  parser.add_argument("-b", "--base", help="Displays the specified operator's base skills.", action="store_true")
  parser.add_argument("-i", "--info", help="Displays the specified operator's stats.", action="store_true")
  parser.add_argument("-a", "--all", help="Displays all the information about this specified operator.", action="store_true")
  args = parser.parse_args()

  return args
######################################

def main():
  spinner = Halo(text="Fetching...", spinner="dots", color="magenta")
  # Initialize the arguments for cmd purposes 
  args = initializeArguments()
  spinner.start()

  imagesDict = readLinesIntoDict("./info/imageToText.txt")
  jsonReplacementNames = readLinesIntoDict("./info/jsonOperatorReplacements.txt")
  urlReplacementNames = readLinesIntoDict("./info/urlOperatorReplacements.txt")

  url = readLineFromFile("./info/url.txt")  # We're always assuming readFromFile returns a valid string tes
  url = (url + "operator/" + args.operator 
        if args.operator not in urlReplacementNames.keys()
        else url + "operator/" + urlReplacementNames[args.operator])

  result = requests.get(url) #remember to uncommemt
  # if (True): # debugging
  if (result.status_code == 200):
    # 200 for if the page exists
    spinner.text = "Parsing..."
    spinner.colour = "yellow"

    src = result.content
    soup = BeautifulSoup(src, "lxml")
    # soup = BeautifulSoup(open("debug.html", "r", encoding="utf-8"), "lxml") # debugging
    
    # Finding the default information that should be displayed for every operator
    # (eg. tags, description, etc.)
    tags = soup.find_all("div", "tag-title")

    # TODO: I could probably make this neater and cooler and probably in its own function
    tagString = ""
    for tag in tags:
      tagString = tagString + tag.a.string.strip() + "     "

    rarityCell = soup.find("div", "rarity-cell")
    rarity = len(rarityCell.find_all("img"))

    professionCell = soup.find("div", "profession-title")
    professionText = professionCell.text.strip()

    desc = soup.find_all("div", "description-box")

    descText = (["No proper description."] 
                if (len(desc) < 3) 
                else ["".join(desc[item].text).strip() + "\n" for item in range(3)])

    # Any optional messages are stored in a list to make printing them at the end easy and so that
    # printing optional messages don't take 50 lines of code.
    optionalMessages = []
    formattedName = args.operator.replace("-", " ").title()
    properName = (formattedName
                  if formattedName not in jsonReplacementNames.keys()
                  else jsonReplacementNames[formattedName])

    # Checking and calling the appropriate functions for optional flags
    # Taking advantage of python's functional programming paradigms to adhere to DRY principles
    #TODO: is this even good practice??? I'm trying to adhere to DRY principles but this makes me start to sweat
    conditionals = [
      [args.info  , findStats     , [soup, properName]],
      [args.skills, findSkills,     [soup]]           ,
      [args.talent, findTalents   , [soup, imagesDict]],
      [args.base  , findBaseSkills, [soup, imagesDict]],
    ]

    for flag, findInfoFunction, arguments in conditionals:
      if flag or args.all:
        optionalMessages += findInfoFunction(*arguments)


    spinner.succeed("Success!")

    # Print out the results
    sys.stdout.write("\n\n" + properName + "   ")
    sys.stdout.write("*" * rarity + "   ") # Star rarity
    sys.stdout.write(professionText + "\n")

    sys.stdout.write(tagString + "\n\n")
    for text in descText: 
      sys.stdout.write(text)

    for text in optionalMessages:
      sys.stdout.write(text + "\n")

  else:
    # Page returns anything other than a 200
    spinner.fail("Failed.")
    sys.stdout.write("\n\n" + args.operator.replace("-", " ").title() + "\n")
    sys.stdout.write("\n" + "Could not find operator! Either the server is down, or your spelling is! \n")

  sys.stdout.write("\n\n")

if __name__ == "__main__":
  main()