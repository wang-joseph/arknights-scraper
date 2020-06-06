import requests, argparse, sys
from bs4 import BeautifulSoup

# created 06/06/2020
# author: Joseph Wang (EmeraldEntities)

### FUNCTIONS ########################
def readFromFile(file):
  with open(file, "r") as f:
    result = f.readline()

  return result

def loadImagesToText():
  imagesToText = {}
  with open("./imageToText.txt", "r") as f:
    totalImages = int(f.readline())
    for _ in range(totalImages):
      imageToText = f.readline().rstrip().split(" ")
      imagesToText[imageToText[0]] = imageToText[1]

  return imagesToText


def findTalents(soup, imagesDict):
  messages = []
  messages.append("\n\nTalents\n")

  allCells = soup.find_all("div", "talent-cell")

  for cell in allCells:
    allChilds = cell.find_all("div", "talent-child")

    for child in allChilds:
      text = ""
      images = child.find_all("img")
      imageTexts = []
      for image in images:
        imageTexts.append(imagesDict[image.attrs["src"]])
      imageTexts.append("-")

      # Formatting and getting rid of the newlines and whatnot
      allText = list(filter(lambda x: x != "\n", child.find_all(text=True)))
      allText[2: 2] = imageTexts
      allText[0] = allText[0].rstrip() + " -"

      for phrase in allText:
        text = text + phrase.strip() + " " 

      messages.append(text)

  return messages
######################################

def main():
  # Initialize the arguments for cmd purposes
  parser = argparse.ArgumentParser(description="Find information about any operator in Arknights!")
  parser.add_argument("operator", help="The operator you want information for. For spaces, use a '-' in place of the space. No special characters.")
  parser.add_argument("-t", "--talent", help="Display the specified operator's talent.", action="store_true")
  parser.add_argument("-s", "--skills", help="Display the specified operator's skills. In-dev", action="store_true")
  parser.add_argument("-u", "--upgrades", help="Display the upgrade stages and what this operator needs. In-dev", action="store_true")
  parser.add_argument("-b", "--base", help="Display the specified operator's base skills. In-dev", action="store_true")
  parser.add_argument("-i", "--info", help="Display the specified operator's stats. In-dev", action="store_true")
  parser.add_argument("-a", "--all", help="Displays all the information. In-dev", action="store_true")
  args = parser.parse_args()

  url = readFromFile("url.txt")  # We're always assuming readFromFile returns a valid string
  url = url + args.operator

  # url = "https://gamepress.gg/arknights/operator/blue-poison"  # debugging URL and operator
  # operator = "blue-poison"

  imagesDict = loadImagesToText()

  result = requests.get(url)
  if (result.status_code == 200):
    # 200 for if the page exists
    src = result.content
    soup = BeautifulSoup(src, "lxml")
    
    # Finding the default information that should be displayed for every operator
    tags = soup.find_all("div", "tag-title")

    tagString = ""
    for tag in tags:
      tagString = tagString + tag.a.string.strip() + "     "

    desc = soup.find_all("div", "description-box")
    descText = ["".join(desc[item].find_all(text=True)).strip() + "\n" for item in range(3)]

    # Any optional messages are stored in a list to make printing them at the end easy and so that
    # printing optional messages don't take 50 lines of code.
    optionalMessages = []

    # Checking and calling the appropriate functions for optional flags
    if args.talent or args.all:
      optionalMessages = optionalMessages + findTalents(soup, imagesDict)
      
    # TODO: finish the rest of the flags

    # Print out the results
    sys.stdout.write("\n\n" + args.operator.replace("-", " ").title() + "\n")
    sys.stdout.write(tagString + "\n\n")
    for text in descText: 
      sys.stdout.write(text)

    for text in optionalMessages:
      sys.stdout.write(text + "\n")

  else:
    # Page returns a 404 not found
    sys.stdout.write(args.operator.replace("-", " ").title() + "\n")
    sys.stdout.write("\n\n" + "Could not find operator! \n")

  sys.stdout.write("\n\n")

if __name__ == "__main__":
  main()