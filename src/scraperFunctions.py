import requests
from inputReader import readLineFromFile, readLinesIntoDict

# created 06/06/2020
# last edited: 02/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: A collection of various scraping functions that this program uses

def scrapeWebsite(url):
  """Sends a GET request to a certain url and returns the Response object if status code is 200.
  Returns None if the server responds with a different code.
  """
  result = requests.get(url)

  # if (True): # debugging
  if (result.status_code == 200):
    return result
  
  return None

def scrapeForOperator(operator):
  """Sends a GET request for a certain operator and returns the Response object if status code is 200.
  Returns None (as per scrapeWebsite() implementation) if server responds with a different code.
  """
  urlReplacementNames = readLinesIntoDict("./info/urlOperatorReplacements.txt")

  operatorUrl = readLineFromFile("./info/url.txt")
  operatorUrl = (operatorUrl + "operator/" + operator 
        if operator not in urlReplacementNames.keys()
        else operatorUrl + "operator/" + urlReplacementNames[operator])

  return scrapeWebsite(operatorUrl)