import sys
from typing import Sequence, Any

# created 27/07/2020
# last edited: 28/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: Just a class to hold relevant information about an
#              operator while tag searching


class TaggedOperator:
    """The class for storing simplistic recruitment information about Operators.

    Each operator is assigned tags that people use to recruit them.
    This object stores those tags, an associated name, and a rarity and 
    bundles them up together so that all these attributes are 
    easily-accessable and reusable.

    Public variables:

    Public methods:
    get_tags_length()

    get_name()

    get_tags()

    get_rarity()

    """

    def __init__(
            self,
            name: str,
            rarity: int,
            tags: Sequence[str]
    ) -> None:
        """Initializes a TaggedOperator object.

        Keyword arguments:
        name -- string, the name of the operator
        rarity -- int, the rarity of the operator as an integer
        tags -- list, a list of strings containing the recruitment tags
        associated with this operator
        """
        self._name = name
        self._tags = tags
        self._rarity = rarity

    def __repr__(self) -> str:
        """Returns a representation of this object in string format."""
        return self._name

    def __hash__(self) -> int:
        """Calcuates and returns the hash value of this object.

        This method will use the name of this operator as the hash
        for it, meaning that you should avoid giving two 
        TaggedOperator objects the same name if they are not meant to
        be the same thing.
        """
        return hash(self._name)

    def __eq__(self, other: object) -> bool:
        """Determines if this is equal to something else."""
        return (
            self.__class__ == other.__class__
            and self._name == other.get_name()
            # and self._tags == other.get_tags() # not necessary for now
        )

    def get_tags_length(self) -> int:
        """Retrieves how many tags are stored in this object."""
        return len(self._tags)

    def get_name(self) -> str:
        """Retrieves the name of this operator."""
        return self._name

    def get_tags(self) -> Sequence[str]:
        """Retrieves all the tags of this operator, as a list of strings."""
        return self._tags

    def get_rarity(self) -> int:
        """Retrieves the rarity of this operator, as an integer."""
        return self._rarity


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
