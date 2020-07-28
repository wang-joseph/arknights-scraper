import sys
from typing import Sequence, Any

# created 27/07/2020
# last edited: 28/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: Just a class to hold relevant information about an
#              operator while tag searching


class TaggedOperator:
    def __init__(
            self,
            name: str,
            rarity: int,
            tags: Sequence[str]
    ) -> None:
        self._name = name
        self._tags = tags
        self._rarity = rarity

    def __repr__(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other: object) -> bool:
        return (
            self.__class__ == other.__class__
            and self._name == other.get_name()
            # and self._tags == other.get_tags() # not necessary for now
        )

    def get_tags_length(self) -> int:
        return len(self._tags)

    def get_name(self) -> str:
        return self._name

    def get_tags(self) -> Sequence[str]:
        return self._tags

    def get_rarity(self) -> int:
        return self._rarity


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
