import sys
from typing import AbstractSet, Optional, Dict

from operatorclasses.TaggedOperator import TaggedOperator
from operatorclasses.PrioritySet import PrioritySet

# created 28/06/2020
# last edited: 28/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: A priority set, but now it can store various
#             pieces of information ("metadata") by using a
#              dictionary.


class MetadataPrioritySet(PrioritySet):
    """A class that has a priority set, but also some metadata attached.

    This class has an intrinsic PrioritySet, but also a dictionary
    that is able to contain various metadata attached to the
    PrioritySet.

    Public variables:

    Public methods:
    add_data(key, data)

    has_metadata()

    has_data(key)

    get_data(key)

    """

    def __init__(
        self,
        intrinsic_set: AbstractSet[TaggedOperator],
        priority_dict: Dict[str, int]
    ) -> None:
        """Initializes a MetadataPrioritySet

        Do keep in mind that metadata must be appended after
        the creation of this object, for simplicity's sake.

        Keyword arguments:
        intrinsic_set -- set, the intrinsic set to be stored
        priority_dict -- dict, a dict with the values of 
        attributes in the set
        """
        super().__init__(intrinsic_set, priority_dict)
        self._metadata = {}

    def add_data(self, key: str, data: str) -> None:
        """Adds a certain key/data pairing to the metadata dict.

        If the key is already in the metadata, nothing happens.
        """
        if key not in self._metadata.keys():
            self._metadata[key] = data

    def has_metadata(self) -> bool:
        """Checks if there is anything inside the metadata dict.

        If you are looking to see if a key exists in the metadata,
        use has_data(key).
        """
        return self._metadata == {}

    def has_data(self, key: str) -> bool:
        """Checks to see if a certain key exists in the metadata."""
        return (key in self._metadata.keys())

    def get_data(self, key: str) -> Optional[str]:
        """Retrieves data from the metadata dict using a key."""
        if self.has_data(key):
            return self._metadata[key]

        return None

    def get_all_data(self) -> Dict[str, str]:
        """Retrieves the metadata dict and returns it."""
        return self._metadata


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
