import sys
from typing import AbstractSet, Dict

from operatorclasses.TaggedOperator import TaggedOperator
# created 28/06/2020
# last edited: 28/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: A priority set (that is, a class that hols a
#             set, but also an intrinsic priority that can be
#             compared with others)


class PrioritySet:
    def __init__(
        self,
        intrinsic_set: AbstractSet[TaggedOperator],
        priority_dict: Dict[str, int]
    ):

        self._intrinsic_set = intrinsic_set
        self._priority = self._calc_priority(priority_dict)

    def __repr__(self) -> str:
        return (
            f"{str(self._priority)} : "
            + f"{self._intrinsic_set.__repr__()}"
        )

    def __eq__(self, other: object) -> bool:
        return (
            self.__class__ == other.__class__
            and self._intrinsic_set == other.get_intrinsic_set()
        )

    def _calc_priority(self, priority_dict: Dict[str, int]) -> int:
        cur_val = 0
        for val in self._intrinsic_set:
            cur_val += priority_dict[str(val.get_rarity())]

        # TODO: Maybe i could move this out of here later
        # that way this class becomes more generalized
        cur_val -= len(self._intrinsic_set) * 3

        return cur_val

    def get_priority(self) -> int:
        return self._priority

    def get_intrinsic_set_copy(self) -> AbstractSet[TaggedOperator]:
        return self._intrinsic_set.copy()

    def get_intrinsic_set(self) -> AbstractSet[TaggedOperator]:
        return self._intrinsic_set


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
