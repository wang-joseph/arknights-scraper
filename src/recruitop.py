"""This module controls everything to do with recruitment and
recruitment tags by taking in inputs, generating all possible
1-3 tag combinations, and finding operators that match those combos."""

import sys
import argparse
import itertools
from typing import Optional, List, Type, Dict, AbstractSet, Sequence

from halo import Halo  # extremely important

from operatorclasses.tagged_operator import TaggedOperator
from operatorclasses.metadata_priorityset import MetadataPrioritySet

from inputfuncs.input_reader import (
    read_line_from_file,
    read_lines_into_dict
)
from inputfuncs.scraper_functions import scrape_json

# created 27/06/2020
# last edited: 29/07/2020
# version: 1.1.0
# author: Joseph Wang (EmeraldEntities)
# description: a CLI for matching recruitment tags to ops
# TODO: move some of the functions into a recruitfuncs module?

### FUNCTIONS ########################


def initialize_operator_list() -> Optional[List[Type[TaggedOperator]]]:
    """Initializes a list of TaggedOperators with names and tags and
    returns said list.

    This function uses a recruitment json created by Aceship to find
    each operator's tags, so if this function is unable to find the
    json, it will return None which should be caught.

    Otherwise, it will generate a list of TaggedOperator objects, each
    with a name, rarity, and recruitment tags.

    Note that hidden operators (globalHidden or hidden) will not be
    included in this list.
    """
    operatortags_rawjson = scrape_json(read_line_from_file(
        "./info/recruitops/recruitTagJsonUrl.txt"
    ))
    # with open("tags_zh.json", "r", encoding="utf8") as f:
    #     operatortags_rawjson = json.load(f)  # debug

    if operatortags_rawjson is None:
        return None

    # Getting the json content returns a list, so we call it a
    # list appropriately
    operatortags_list = operatortags_rawjson.json()
    # operatortags_list = operatortags_rawjson # debug
    operator_list = []

    name_replacements = read_lines_into_dict(
        "./info/recruitops/operatorNameReplacements.txt"
    )

    # initialize an easy to access list of operators and their tags
    #
    # Some operators aren't available in HH and thus they are labelled
    # as 'hidden' or 'globalHidden' in the json.
    for operator in operatortags_list:
        if (
                operator["hidden"]
                or (
                    "globalHidden" in operator.keys()
                    and operator["globalHidden"]
                )
        ):
            continue

        operator_list.append(
            TaggedOperator(
                operator["name_en"],
                operator["level"],
                operator["tags"] + [operator["type"].rstrip()]
            )
            if operator["name_en"] not in name_replacements
            else TaggedOperator(
                name_replacements[operator["name_en"]],
                operator["level"],
                operator["tags"] + [operator["type"].rstrip()]
            )
        )

    return operator_list


def initialize_tag_dictionary(
        operator_list: Sequence[Type[TaggedOperator]]
) -> Dict[str, AbstractSet[str]]:
    """Using a list of operators, initializes a dictionary matching
    tags to operators that have those tags, and then returns it.

    The keys are in Chinese because of the json, making it a bit
    harder to work with. Otherwise, it simply matches a tag with each
    of the operators that has it.

    Keyword arguments:
    operator_list -- list, a list of TaggedOperator that is used to
    build the dictionary
    """
    tag_dict = {}

    with open(
            "./info/recruitops/alltags.txt",
            "r",
            encoding="utf8"
    ) as f:
        current_line = f.readline()
        while current_line != "" and current_line != "\n":
            # By using sets to compare, we can
            # easily combine results of searches later
            tag_dict[current_line.rstrip()] = set([])

            current_line = f.readline()

    for operator in operator_list:
        for tag in operator.get_tags():
            if tag in tag_dict.keys():
                tag_dict[tag].add(operator)

    return tag_dict


def is_not_top_op(operator: Type[TaggedOperator]) -> bool:
    """Determines if an Operator has a rarity of 6
    and returns True if not."""
    return operator.get_rarity() < 6


def get_formatted_op(operator: Type[TaggedOperator]) -> str:
    """Returns a formatted string consisting of an Operator's name
    and rarity."""
    return f"{operator.get_name()}: {operator.get_rarity()}*"


def generate_operator_set(
        combo: Sequence[str],
        tag_dict: Dict[str, TaggedOperator],
        translation_dict: Dict[str, str],
        reversed_translation_dict: Dict[str, str]
) -> Optional[MetadataPrioritySet]:
    """Using a provided combination of tags, checks if there are
    operators that possess all those tags.

    Returns a MetadataPrioritySet with the combination of tags, a
    calculated priority based on the operators, and the operators
    that match all those tags if operators are found.

    Returns None otherwise.

    Keyword arguments:
    combo -- list, a combination of tags
    tag_dict -- dict, a dict matching tags with operators
    translation_dict -- dict, a dict translating english tags to
    chinese tags
    reversed_translation_dict -- dict, a dict translating chinese tags
    to formatted english tags
    """
    priority_values = {
        "1": 0,
        "2": -2,
        "3": 0,
        "4": 1,
        "5": 2,
        "6": 3,
    }

    # Every combo will always have at least 1 entity, so
    # we want the starting selection of operators all
    # from the first tag, which we then splice out and then
    # loop using the remaining tags.
    #
    # note: copy is reallllyyy important
    # TODO: maybe make this better
    possible_ops = (
        tag_dict[combo[0]].copy()
        if translation_dict["top-operator"] in combo
        else set(
            filter(
                is_not_top_op,
                tag_dict[combo[0]].copy()
            )
        )
    )

    # This is to let us find out the tags we used to get this combo
    converted_string = reversed_translation_dict[combo[0]]

    # We have to loop over the rest of the tags and get the
    # intersection of the current set of operators (from the first tag)
    # and the rest of the operators from the rest of the tags.
    for tag in combo[1:]:
        # To prevent looping over this twice, we just get
        # the converted chinese-to-english
        # tag string here, and use if it we need it.
        converted_string += " + " \
            + reversed_translation_dict[tag]
        # TODO: maybe make this better
        new_ops = (
            tag_dict[tag].copy()
            if translation_dict["top-operator"] in combo
            else set(
                filter(
                    is_not_top_op,
                    tag_dict[tag].copy()
                )
            )
        )
        possible_ops &= new_ops

        if len(possible_ops) <= 0:
            break  # oh no its a bad break

    # If there are operators that satisfy all the tags, this
    # bit of code will run, returning a MetadataPrioritySet.
    # If no operator satisfies them all, this function will return
    # None, indicating no tags.
    if len(possible_ops) > 0:
        # Sorting all the possible ops in order of rarity
        possible_ops = sorted(
            possible_ops,
            key=lambda o: o.get_rarity(),
            reverse=True
        )

        current_match = MetadataPrioritySet(
            possible_ops,
            priority_values
        )

        current_match.add_data(
            "tags",
            converted_string
        )

        return current_match

    return None


def get_all_combinations(
        proper_tags: Sequence[str],
        tag_dict: Dict[str, TaggedOperator],
        translation_dict: Dict[str, str],
        reversed_translation_dict: Dict[str, str]
) -> List[MetadataPrioritySet]:
    """Generates all the combinations of tags possible, gets the
    operators for each combination, and returns a list of
    MetadataPrioritySet with operators that match each tag.

    Keyword arguments:
    proper_tags -- list, the tags provided
    tag_dict -- dict, a dict matching tags with operators
    translation_dict -- dict, a dict translating english tags to
    chinese tags
    reversed_translation_dict -- dict, a dict translating chinese tags
    to formatted english tags
    """

    all_matches = []
    # Since ops only have 3 tags, we get all combinations with 1-3
    # length
    for amount_of_tags in range(1, 4):
        all_combos = itertools.combinations(
            proper_tags,
            amount_of_tags
        )
        for combo in all_combos:
            current_match = generate_operator_set(
                combo,
                tag_dict,
                translation_dict,
                reversed_translation_dict
            )

            if current_match is not None:
                all_matches.append(current_match)

    return all_matches


def format_selections(
        args: argparse.Namespace,
        all_sorted_selection: List[MetadataPrioritySet]
) -> List[str]:
    """Determines how to format a selection of operators,
    and returns a nicely formatted list of messages in strings."""
    # Depending on whether the beneficial arg is specified,
    # one of two different functions could be called.
    if args.beneficial:
        return format_beneficial_tags(all_sorted_selection)
    else:
        return format_normal_tags(all_sorted_selection)


def format_beneficial_tags(
        all_sorted_selection: List[MetadataPrioritySet]
) -> List[str]:
    """Formats the operators so that only combinations of tags that
    have 'beneficial' results (ie. operators with only rarity 4, 5, 6)
    are formatted into the returned list of messages."""
    messages = ["Only beneficial tags:\n"]

    for op_set in all_sorted_selection:
        # We need to make sure this has no 3 or less stars, so we
        # take the last element of this sorted set and check
        # its rarity. If it's higher than 3, the rest of the set
        # should be higher than 3.
        if list(op_set.get_intrinsic_set())[-1].get_rarity() > 3:
            messages.append(
                op_set.get_data("tags")
            )
            messages.append(
                ", \n".join(
                    list(map(
                        get_formatted_op,
                        op_set.get_intrinsic_set_copy()
                    ))
                )
                + "\n"
            )

    if len(messages) == 1:  # since we initialize it with one element
        messages.append("No good combinations found...")

    return messages


def format_normal_tags(
        all_sorted_selection: List[MetadataPrioritySet]
) -> List[str]:
    """Formats the operators so that all working combinations of
    operators are put into the returned list of messages, sorted
    by value of the combinations."""
    messages = []

    for op_set in all_sorted_selection:
        # Since the set is sorted, we can simply get the rarity
        # of the last operator in the set and check tot see if
        # the rarity is greater than 3. If so, we can
        # assume everything in the set is greater than 3 stars,
        # making this a good combination, and we mark
        # it appropriately.
        messages.append(
            op_set.get_data("tags")
            if (
                list(op_set.get_intrinsic_set())[-1]
                .get_rarity() <= 3
            )
            else f"***Good***\n{op_set.get_data('tags')}"
        )
        messages.append(
            ", \n".join(
                list(map(
                    get_formatted_op,
                    op_set.get_intrinsic_set_copy()
                ))
            )
            + "\n"
        )

    return messages

######################################


# TODO: this can be multiple functions
def find_recruitment_combos(args: argparse.Namespace) -> None:
    """Taking the specified namespace of arguments, this function will
    determine combinations of tags, find operators that match those
    combinations, and print to the screen a formatted list of
    combinations and operators, sorted by value bottom-to-top."""
    spinner = Halo(text="Fetching...", spinner="dots", color="magenta")
    spinner.start()

    op_list = initialize_operator_list()
    if op_list is None:
        spinner.fail("Failed.")
        sys.stdout.write(
            "\n\nThe tag JSON could not be fetched! Try again later."
        )
    else:
        spinner.text = "Calculating..."
        spinner.color = "yellow"

        tag_dict = initialize_tag_dictionary(op_list)

        # Get both a proper translation from en to zh dict
        # and a reversed dict initialized for proper tag conversion
        translation_dict = read_lines_into_dict(
            "./info/recruitops/tagConversions.txt"
        )
        reversed_translation_dict = read_lines_into_dict(
            "./info/recruitops/formattedTagConversions.txt",
            reverse=True
        )

        # Take in the user tags and find their proper, translated names
        # so that they can be used with the json.
        proper_tags = []
        # TODO: this tag process could probably be more optimized
        for tag in args.tags:
            if tag.lower() in translation_dict.keys():
                proper_tags.append(translation_dict[tag.lower()])
            else:
                # TODO: exit nicer
                raise Exception(
                    f"The tag '{tag.lower()}' does not exist."
                )

        # Find all possible combinations of each tag combo
        all_matches = get_all_combinations(
            proper_tags,
            tag_dict,
            translation_dict,
            reversed_translation_dict
        )

        # Sort based on priority and format all the possible
        # combinations.
        #
        # Consists of all the tag combinations and results, sorted
        # by priority.
        all_sorted_selection = sorted(
            all_matches,
            key=lambda s: s.get_priority()
        )
        messages = format_selections(args, all_sorted_selection)

        # Print the recruitment results
        spinner.succeed("Success!")
        sys.stdout.write("\n\nRecruitment Results\n\n")  # padding
        sys.stdout.write(
            "Note: the lower down the tag collection, "
            + "the better the tags.\n\n\n"
        )  # padding

        if len(messages) <= 0:
            sys.stdout.write("Could not find any recruitment results.")
        else:
            for msg in messages:
                sys.stdout.write(msg + "\n")
        sys.stdout.write("\n")  # padding


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
