"""A module that contains the PrioritySet class
(that is, a class that holds a set of tagged operators (currently),
but also an intrinsic 'priority' that can be compared with other
priority sets)."""

import sys
from typing import AbstractSet, Dict

from operatorclasses.tagged_operator import TaggedOperator


class PrioritySet:
    """This class stores a set of operators and also contains a
    priority based on a dictionary that is compared against the set.

    This way, the functionality of a set is preserved, but now
    there is an additional "priority" attribute that can be used
    to compare against other priority sets.

    Public variables:

    intrinsic_set

    priority

    Public methods:

    get_priority()

    get_intrinsic_set_copy()
    """

    def __init__(
            self,
            intrinsic_set: AbstractSet[TaggedOperator],
            priority_dict: Dict[str, int]
    ):
        """Initializes a PrioritySet.

        Keyword arguments:

        intrinsic_set -- set, the intrinsic set to be stored

        priority_dict -- dict, a dict with the values of
        attributes in the set
        """

        self._intrinsic_set = intrinsic_set
        self._priority = self._calc_priority(priority_dict)

    def __repr__(self) -> str:
        """Returns a formatted representation of this priority set."""
        return (
            f"{str(self.intrinsic_set)} : "
            + f"{repr(self.intrinsic_set)}"
        )

    @property
    def intrinsic_set(self) -> AbstractSet[TaggedOperator]:
        """Retrieves this PrioritySet's intrinsic set.

        This will not copy the set, meaning the original
        set could be edited. If you need a copied set, use
        get_intrinsic_set_copy() instead.
        """
        return self._intrinsic_set

    @property
    def priority(self) -> int:
        """Retrieves this priority."""
        return self._priority

    def __eq__(self, other: object) -> bool:
        """Determines whether this priority set is the same as another object."""
        return (
            self.__class__ == other.__class__
            and self.intrinsic_set == other.intrinsic_set
        )

    def _calc_priority(self, priority_dict: Dict[str, int]) -> int:
        """Calculate this set's priority based on a dict that is passed in.

        Each attribute of the set will be checked against the dict and
        a priority score will be assigned. Then, the current score
        will be decreased based on how long the set is
        (implemented -= len(self._intrinsic_set) * 3)

        Keyword arguments:

        priority_dict -- dict, a dictionary with key/value pairs that
        contains values (value) for the attributes of the set (key)
        """
        cur_val = 0
        for val in self.intrinsic_set:
            cur_val += priority_dict[str(val.rarity)]

        # TODO: Maybe i could move this out of here later
        # that way this class becomes more generalized
        cur_val -= len(self.intrinsic_set) * 3

        return cur_val

    def get_intrinsic_set_copy(self) -> AbstractSet[TaggedOperator]:
        """Retrieves a copy of this PrioritySet's intrinsic set.

        This is in case you need to edit the set, but need to preserve
        the original set.
        """
        return self.intrinsic_set.copy()


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
