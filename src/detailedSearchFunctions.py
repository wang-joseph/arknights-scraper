import re, json, sys, requests
from bs4 import Tag

from scraperFunctions import scrapeWebsite
from inputReader import readLineFromFile

# created 01/07/2020
# last edited: 03/07/2020
# version: 1.2.1
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

      text = text.rstrip() # get rid of any placed newlines
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

def createStatsJSON(soup, operator):
  """Creates the JSON file (dictionary) containing all the operator's stats, and returns it.

  This dictionary MUST have the basic operator stats (ie. atk, def, hp) and will return `None` if these 
  stats are not found (if the JSON file I use for these stats is down, or the operator cannot be found.)

  This function will first look and load the basic stats (ATK, DEF, HP) for each stage.
  Then it will attempt to load (Block, Cost, Res) from the operator website under the variable myStats.
  Finally, it will attempt to load (Redeploy Time, Attack Interval) from the operator website
  from a different section.
  Therefore, this function will look 3 times for the specified attributes.

  If any of these searches fails (except for the first one, which is essential), this function will simply set
  that attribute's value as `"-1"`, indicating failure to retrieve.
  """
  # Load in the json file for all operators
  # TODO: should I make a response obj to hold any possible errors?

  # Do this seperately because if I did it every time that would be a waste of time
  # for requests that don't need this info.
  statsUrl = readLineFromFile("./info/url.txt") + "/stat-rankings?_format=json"
  statsInfo = scrapeWebsite(statsUrl)

  if statsInfo == None:
    return None # Request failed
  
  statsJson = None
  for jsonFile in statsInfo.json():
  # for jsonFile in statsInfo: # debugging
    if jsonFile["title"] == operator:
      statsJson = jsonFile
      break # whoa a bad break

  if statsJson == None: 
    return None # No operator found in the big JSON file



  # Find myStats from the operator's site
  # This is so we can find res, cost, and block
  goodScripts = soup.find_all('script', '')
  for script in goodScripts:
    if re.search(r"myStats =", str(script)):
      myStatsScript = script
      break # oh no another bad break

  levels = ["ne", "e1", "e2"]
  wantedAttributes = ["arts", "cost", "block"]

  for attr in wantedAttributes:
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
      for stat in range(len(allStats)):
        statsJson[levels[stat] + "_" + attr] = '-1' # -1 to symbolize failure



  # otherStats will provide us with the atk speed and redeploy time stats.
  otherStats = soup.find_all('div', 'other-stat-value-cell')
  
  if len(otherStats) > 0:
    # Convert every object into their stripped strings counterpart
    for stat in range(len(otherStats)):
      curStatsList = []
      for string in otherStats[stat].stripped_strings:
        curStatsList.append(string)

      if "Attack Interval" in curStatsList:
        statsJson['atk_int'] = curStatsList[-1]
      
      elif "Redeploy Time" in curStatsList:
        statsJson['deploy_time'] = curStatsList[-1]
  
  # Failsafes, in case
  if 'atk_int' not in statsJson.keys():
    statsJson['atk_int'] = -1
  if 'deploy_time' not in statsJson.keys():
    statsJson['deploy_time'] = -1



  return statsJson

def parseStats(statsJson):
  messages = []
  messages.append("\n\nOperator Stats\n")

  if statsJson == {}:
    return ["\n\nOperator Stats\nEither the stats JSON is down, or we couldn't find your operator!"]

  levels = ["ne", "e1", "e2"]
  formattedLevels = ["E0", "E1", "E2"]
  maxStats = []

  # Fetch the basic stats for each level (if it exists)
  # We check the max atk stat for each, and if it's not a "" then we know that operator has that lvl
  for lvl in range(len(formattedLevels)):
    if statsJson["max_atk" + levels[lvl]] != "":
      maxStats += [
        formattedLevels[lvl],
        "Max atk: " + statsJson[f"max_atk{levels[lvl]}"] + " atk",
        "Max def: " + statsJson[f"max_def{levels[lvl]}"] + " def",
        "Max hp : " + statsJson[f"max_hp{levels[lvl]}"] + " hp",
        "Res    : " + statsJson[f"{levels[lvl]}_arts"],
        "Block  : " + statsJson[f"{levels[lvl]}_block"],
        "Cost   : " + statsJson[f"{levels[lvl]}_cost"] + " dp \n"
      ]
  
  if len(maxStats) == 0:
    # Very minor formatting issue but this is to get rid of the new line inserted by the final formatter
    # by simply adding it to the first element of the list and not a seperate list element
    messages[0] += "No stats found!"

  messages += maxStats

  # Retrieve the attack interval and redeploy time
  # By adding an empty space at the end, we fool the parser into inserting only 1 newline
  messages += ["Attack Interval:  " + statsJson['atk_int']]
  messages += ["Deployment Time:  " + statsJson['deploy_time']] + [""]

  return messages

def findSiblingsOfBreakpoint(soupObj):
  """Gets all the text from the sibling of a breakpoint and return as list of strings.
  
  Sometimes, a description could be formatted with a br, which bs4 doesn't work well with when doing o.text.strip().
  To solve that, we find the <br>'s sibling text and format the text ourselves, adding a `\\n` wherever needed.

  If a <br> tag isn't found, just return the object's text, stripped.
  """
  brkpoint = soupObj.find_all('br')
      
  if brkpoint != []: #TODO: make this code better omg (like, those two for loops are so similar omg)
    descriptionList = []
    prevBrkText = []
    # Previous_siblings gives you the tags in reverse, so you have to reverse it after getting them all
    # also oh my freaking goodness both isinstance AND break in the same block?? execute this man
    for sibling in brkpoint[0].previous_siblings:
      if isinstance(sibling, Tag):
        if sibling.name == "br":
          break

        prevBrkText.append(sibling.text.strip())
      else:
        prevBrkText.append(str(sibling))
    prevBrkText.reverse()
    prevBrkText[-1] += "\n"
    descriptionList += prevBrkText

    # We only need to get the previous siblings for the first <br> tag. Then we can just get the
    # next siblings for every other <br> tag to complete the description.
    for br in brkpoint:
      nextBrkText = []

      for sibling in br.next_siblings:
        if isinstance(sibling, Tag):
          if sibling.name == "br":
            break

          nextBrkText.append(sibling.text.strip())
        else:
          nextBrkText.append(str(sibling))
      nextBrkText[-1] += '\n'
      descriptionList += nextBrkText

    return descriptionList
  else:
    return soupObj.text.strip()

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
      maxLevel[i] = "".join(findSiblingsOfBreakpoint(maxLevel[i]))

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
    
    # Filter out any "" that might be appended and any extra \n
    description[0] = ' ' + description[0] # Adding a space before every description for good readability
    description = list(map(lambda x: x.rstrip(), description))
    description = list(filter(lambda x: x != "", description))

    # Add a \n to the last item in description for consistent formatting!!!!!
    messages += description + ["\n"]

  # Get rid of the last \n in all messages for consistent formatting!!!!!!
  messages[-1] = messages[-1].rstrip()
  return messages

if __name__ == "__main__":
  sys.stdout.write("Wrong python file to run! The main file to run is `scraper.py`.\n\n")