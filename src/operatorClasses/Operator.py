import sys

# created 06/06/2020
# last edited: 07/07/2020
# version: 1.2.0
# author: Joseph Wang (EmeraldEntities)
# description: A basic operator object that can be created
# for parsing/testing


class Operator:
    """The class for creating Operator objects, which stores information about Operators.

    This solely exists so that operator information can be 
    held in a convienient location, and can be reused for other 
    future features.

    Public variables:
    name -- string
    rarity -- int
    profession -- string
    description -- list
    tags -- list

    Public methods:
    set_property(property, value)

    get_property(property)

    get_all_properties()

    has_property(property)

    get_formatted_tags()

    get_all_stats()

    set_stats(stats)

    has_stats()

    """

    def __init__(
        self,
        name,
        rarity,
        profession,
        description=["No description available!"],
        tags=["No tags available!"]
    ):
        """Initializes an Operator object.

        Keyword arguments:
        name -- string, the name of the operator
        rarity -- int, the rarity of the operator as a number 
        (5 star = 5, etc.)
        profession -- string, what class the operator is
        description -- list, a list containing the description strings 
        of an operator (default ["No description available!"])
        tags -- list, a list containing the tags of this operator 
        (default: ["No tags available!"])
        """
        self.name = name
        self.rarity = rarity
        self.profession = profession
        self.description = description
        self.tags = tags

        self._stats = {}
        self._properties = {}

    def set_property(self, prop, value):
        """Set the specified property of this operator to a value.

        If the value already exists, this method will assume the
        value is a list and append the provided value
        to the existing value.
        """
        if prop in self._properties.keys():
            # We're assuming all property stuff are in arrays
            self._properties[prop].append(value)
        else:
            self._properties[prop] = value

    def get_property(self, prop):
        """Return the specified property of this operator, which is normally a list, if it has it. Return None otherwise."""
        if (self.has_property(prop)):
            return self._properties[prop]
        else:
            return None

    def get_all_properties(self):
        """Return all the stored property names as a list."""
        return self._properties.keys()

    def has_property(self, prop):
        """Checks to see if this Operator has a property. True if so, False otherwise."""
        if prop in self._properties.keys():
            return True

        return False

    def get_formatted_tags(self):
        """Retrieves all the tags that this Operator has, formatted into a string."""
        tag_string = ""
        for tag in self.tags:
            tag_string += tag + "     "

        return tag_string

    # I don't like this, but this is so that we don't need to load in
    # stats for the operator every single time we want them...
    # TODO: Maybe I could merge stats into properties?
    def get_all_stats(self):
        return self._stats

    def set_stats(self, stats):
        self._stats = stats

    def has_stats(self):
        return (not (self._stats == {}) and not (self._stats == None))


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `scraper.py`.\n\n"
    )
