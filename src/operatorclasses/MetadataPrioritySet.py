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
    def __init__(
        self,
        intrinsic_set: AbstractSet[TaggedOperator],
        priority_dict: Dict[str, int]
    ) -> None:
        super().__init__(intrinsic_set, priority_dict)
        self._metadata = {}

    def add_data(self, key: str, data: str) -> None:
        if key not in self._metadata.keys():
            self._metadata[key] = data

    def has_metadata(self) -> bool:
        return self._metadata == {}

    def has_data(self, key: str) -> bool:
        return (key in self._metadata.keys())

    def get_data(self, key: str) -> Optional[str]:
        if self.has_data(key):
            return self._metadata[key]

        return None

    def get_all_data(self) -> Dict[str, str]:
        return self._metadata


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
