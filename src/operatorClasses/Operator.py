# created 06/06/2020
# last edited: 03/07/2020
# version: 1.1.0
# author: Joseph Wang (EmeraldEntities)
# description: A basic operator object that can be created for parsing/testing

class Operator:
  """The class for creating Operator objects, which stores information about Operators.

  This solely exists so that operator information can be held in a convienient location,
  and can be reused for other future features.

  Public variables:
  name -- string
  rarity -- int
  profession -- string
  description -- list
  tags -- list

  Public methods:
  setProperty(property, value)

  getProperty(property)

  getAllProperties()

  hasProperty(property)

  getFormattedTags()

  """

  def __init__(self, name, rarity, profession, stats={}, description=["No description available!"], tags=["No tags available!"]):
    """Initializes an Operator object.

    Keyword arguments:
    name -- string, the name of the operator
    rarity -- int, the rarity of the operator as a number (5 star = 5, etc.)
    profession -- string, what class the operator is
    stats -- dictionary, the stats of this operator (default {})
    description -- list, a list containing the description strings of an operator (default ["No description available!"])
    tags -- list, a list containing the tags of this operator (default: ["No tags available!"])
    """
    self.name = name
    self.rarity = rarity
    self.profession = profession
    self.description = description
    self.tags = tags

    self._stats = {} if stats == None else stats

    self._properties = {}

  def setProperty(self, prop, value):
    """Set the specified property of this operator to a value, or appends it to the existing property if present"""
    if prop in self._properties.keys():
      #We're assuming all property stuff are in arrays
      self._properties[prop].append(value)
    else:
      self._properties[prop] = value
    
  def getProperty(self, prop):
    """Return the specified property of this operator, which is normally a list, if it has it. Return None otherwise."""
    if (self.hasProperty(prop)):
      return self._properties[prop]
    else:
      return None

  def getAllProperties(self):
    """Return all the stored property names as a list."""
    return self._properties.keys()
  
  def hasProperty(self, prop):
    """Checks to see if this Operator has a property. True if so, False otherwise."""
    if prop in self._properties.keys():
      return True

    return False 

  def getFormattedTags(self):
    """Retrieves all the tags that this Operator has, formatted into a nice string with spacing."""
    tagString = ""
    for tag in self.tags:
      tagString += tag + "     "

    return tagString

  def getAllStats(self):
    return self._stats