import re, json, sys, requests
from bs4 import Tag

from inputReader import readLineFromFile

# created 01/07/2020
# last edited: 02/07/2020
# version: 1.1.0
# author: Joseph Wang (EmeraldEntities)

def findTalents(soup, imagesDict):
  allCells = soup.find_all("div", "talent-cell")

  if len(allCells) == 0: 
    return ["\n\nTalents\nNo talents found!"]

  messages = []
  messages.append("\n\nTalents\n")

  for cell in allCells:
    allChilds = cell.find_all("div", "talent-child")

    for child in allChilds:
      text = ""

      # Converting images to their text equivalent
      images = child.find_all("img")
      
      imageTexts = []
      for image in images:
        imageTexts.append(imagesDict[image.attrs["src"]])
      # Adds a delimiter (-) and a new line to seperate the text from the name of talent, pot, etc. cause FORMATTING
      imageTexts.append("-\n")

      # Formatting and getting rid of the newlines and whatnot
      # The lists assist with formatting and proper segmenting of the talents
      allText = []
      for string in child.stripped_strings:
        allText.append(string)

      allText[2: 2] = imageTexts # inserts imageTexts into allText at index 2
      allText[0] = allText[0].rstrip() + " -"

      for phrase in allText:
        text = text + phrase + " " 

      messages.append(text + "\n") # extra newline to make reading a bit easier on the eyes

  return messages

def findBaseSkills(soup, imagesDict):
  buildingCells = soup.find_all("div", "building-buff-cell")

  if len(buildingCells) == 0:
    return ["\n\nBase Skills\nNo base skills found!"]

  messages = []
  messages.append("\n\nBase Skills\n")
  
  if len(buildingCells) == 0:
    return ["No base skills found!"]

  for cell in buildingCells:
    text = ""

    # The base skills are laid out in top-cell, bottom-cell format
    # Finding them seperately helps with formatting, even if it's technically a bit slower than
    # just finding the whole div chunk and parsing with that.
    topCell = cell.find("div", "top-cell")
    bottomCell = cell.find("div", "bottom-cell")
    
    # Potentials don't help with base skills, so this is only for E1, E2, etc.
    image = imagesDict[topCell.find("img").attrs["src"]]

    # # Formatting and saving the text
    for string in topCell.stripped_strings:
      text = text + string + "  "

    text += image + "\n "

    for string in bottomCell.stripped_strings:
      text = text + string + " "

    messages.append(text + "\n") # newline to make reading a bit easier

  return messages

def findStats(soup, operator): #TODO: 
  #Load in the json file
  statsUrl = readLineFromFile("./info/url.txt") + "/stat-rankings?_format=json"
  
  statsInfo = requests.get(statsUrl)
  # with open("debug.json", 'r') as f: # debugging
  #   statsInfo = json.load(f)

  messages = []
  messages.append("\n\nOperator Stats\n")
  
  statsJson = None
  for jsonFile in statsInfo.json():
  # for jsonFile in statsInfo: # debugging
    if jsonFile["title"] == operator:
      statsJson = jsonFile
      break # whoa a bad break

  if statsJson == None: 
    return ["\n\nOperator Stats\nNo stats found!"]


  # Find myStats from the operator's site
  goodScripts = soup.find_all('script', '')
  for script in goodScripts:
    if re.search(r"myStats =", str(script)):
      myStatsScript = script
      break # oh no another bad break

  levels = ["ne", "e1", "e2"]
  attributes = ["arts", "cost", "block"]

  for attr in attributes:
    allStats = (re.findall(fr'"{attr}": "(.*)"', str(myStatsScript)))

    # Since 'block' has both a base and max (which doesn't matter),
    # we're gonna only take every other index.
    if attr == 'block':
      allStats = allStats[::2]

    # Make sure that allStats always has three attributes
    if len(allStats) == 3:
      for stat in range(len(allStats)):
        # We're gonna manually add the stat to our statsJson dictionary so we can format it later
        statsJson[levels[stat] + "_" + attr] = allStats[stat]
    else:
      # just to make sure we don't break the program later if there's a bad parse somewhere
      messages.append("Something went wrong while grabbing res, block, and cost. Please report this!")
      return messages

  #TODO: make this less stupid 
  if statsJson["max_atkne"] != "":
    maxStats = [
      "E0 max atk: " + statsJson["max_atkne"] + " atk",
      "E0 max def: " + statsJson["max_defne"] + " def",
      "E0 max hp : " + statsJson["max_hpne"] + " hp",
      "E0 res    : " + statsJson["ne_arts"],
      "E0 block  : " + statsJson["ne_block"],
      "E0 cost   : " + statsJson["ne_cost"] + " dp \n",
    ]

    if statsJson["max_atke1"] != "":
      maxStats += [
        "E1 max atk: " + statsJson["max_atke1"] + " atk",
        "E1 max def: " + statsJson["max_defe1"] + " def",
        "E1 max hp : " + statsJson["max_hpe1"] + " hp",
        "E1 res    : " + statsJson["e1_arts"],
        "E1 block  : " + statsJson["e1_block"],
        "E1 cost   : " + statsJson["e1_cost"] + " dp \n",
      ]

      if statsJson["max_atke2"] != "":
        maxStats += [
        "E2 max atk: " + statsJson["max_atke2"] + " atk",
        "E2 max def: " + statsJson["max_defe2"] + " def",
        "E2 max hp : " + statsJson["max_hpe2"] + " hp",
        "E2 res    : " + statsJson["e2_arts"],
        "E2 block  : " + statsJson["e2_block"],
        "E2 cost   : " + statsJson["e2_cost"] + " dp \n"
      ]
    messages += maxStats
  else:
    # Very minor formatting issue but this is to get rid of the new line inserted by the final formatter
    # by simply adding it to the first element of the list and not a seperate list element
    messages[0] += "No stats found!"

  return messages

def findSkills(soup): 
  # skill-cell is the class name that all skill blocks have, so we need to get them all
  allSkills = soup.find_all('div', 'skill-cell')

  # If the operator doesn't have any skill blocks, they don't have any skills we can parse
  if len(allSkills) == 0:
    return ["\n\nSkills\nNo skills found!"]

  messages = []
  messages.append("\n\nOperator Skills (Highest Levels)\n")

  for skill in allSkills:
    # Finding the skill title
    title = skill.find('div', 'skill-title-cell')
    messages.append(title.text.strip())

    # Let's be honest, everyone only cares about the top level of this skill...
    maxUpgradeLevel = 'skill-upgrade-tab-10'
    maxLevel = skill.find_all('div', maxUpgradeLevel)

    spString = ""
    # We gotta do this check because some operators can't actually get mastery on their skills
    if len(maxLevel) == 0:
      maxUpgradeLevel = 'skill-upgrade-tab-7'
      maxLevel = skill.find_all('div', maxUpgradeLevel)
      spString += f"{'Lv7':15}"
    else:
      spString += f"{'Lv7 M3':15}"

    for i in range(len(maxLevel)):

      # Since the page uses <br> to split text, we're gonna find the <br>, find the text before and after it,
      # and use it for ourselves too.

      # Note: this will work for multiple br tags (hopefully), but as far as I can tell they only use one per in desc
      # oh well, future proofing!
      brkpoint = maxLevel[i].find_all('br')
      
      if brkpoint != []: #TODO: make this code better omg
        descriptionText = " "
        prevBrkText = []

        # Previous_siblings gives you the tags in reverse, so you have to reverse it after getting them all
        # also oh my freaking goodness both isinstance AND break in the same block?? execute this man
        for sibling in brkpoint[0].previous_siblings:
          if isinstance(sibling, Tag):
            if sibling.name == "br":
              break

            prevBrkText.append(sibling.text.strip())
          else:
            prevBrkText.append(sibling)
        prevBrkText.reverse()

        descriptionText += "".join(prevBrkText) + "\n"

        # We only need to get the previous siblings for the first <br> tag. Then we can just get the
        # next siblings for every other <br> tag to complete the description.
        for br in brkpoint:
          nextBrkText = ""

          for sibling in br.next_siblings:
            if isinstance(sibling, Tag):
              if sibling.name == "br":
                break

              nextBrkText += sibling.text.strip()
            else:
              nextBrkText += sibling

          descriptionText += nextBrkText + "\n"

        maxLevel[i] = descriptionText
      else:
        maxLevel[i] = maxLevel[i].text.strip()

    # Add some informative text to max level
    # maxLevel now looks like ['spcost', 'initalsp', 'duration', ...'duration']
    # We format it accordingly
    maxLevel[0] = "SP cost: " + maxLevel[0]
    maxLevel[1] = "Initial SP: " + maxLevel[1]
    maxLevel[2] = "Duration: " + maxLevel[2]
    description = maxLevel[3:] # The description will always be whatever is after the first 3 chunks of text

    # Using f-string width formatting, we can get the width of each text to be the same
    spString += f"{maxLevel[0]:18}{maxLevel[1]:22}{maxLevel[2]}"

    messages.append(spString)
    # Add a \n to the last item in description for consistent formatting!!!!!
    messages += description + ["\n"]

  # Get rid of the last \n in all messages for consistent formatting!!!!!!
  messages[-1] = messages[-1].rstrip()
  return messages

if __name__ == "__main__":
  sys.stdout.write("Wrong python file to run! The main file to run is `scraper.py`.\n\n")