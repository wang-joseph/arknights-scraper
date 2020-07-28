import sys
import json
import argparse
import itertools
from halo import Halo  # extremely important
from typing import Optional, List, Type, Dict, AbstractSet, Sequence

from operatorclasses.TaggedOperator import TaggedOperator
from operatorclasses.MetadataPrioritySet import MetadataPrioritySet

from input_reader import read_line_from_file, read_lines_into_dict
from scraper_functions import scrape_json

# created 27/06/2020
# last edited: 28/07/2020
# version: 1.1.0
# author: Joseph Wang (EmeraldEntities)
# description: a CLI for matching recruitment tags to ops

### FUNCTIONS ########################


def initialize_operator_list() -> Optional[List[Type[TaggedOperator]]]:
    operatortags_rawjson = scrape_json(read_line_from_file(
        "./info/recruitops/recruitTagJsonUrl.txt"
    ))
    # with open('tags_zh.json', 'r', encoding="utf8") as f:
    #     operatortags_rawjson = json.load(f)  # debug

    if operatortags_rawjson == None:
        return None

    # Getting the json content returns a list, so we call it a
    # list appropriately
    operatortags_list = operatortags_rawjson.json()
    # operatortags_list = operatortags_rawjson # debug
    operator_list = []

    name_replacements = read_lines_into_dict(
        './info/recruitops/operatorNameReplacements.txt'
    )

    # initialize an easy to access list of operators and their tags
    #
    # Some operators aren't available in HH and thus they are labelled
    # as 'hidden' or 'globalHidden' in the json.
    for operator in operatortags_list:
        if (
            operator['hidden'] == True
            or (
                'globalHidden' in operator.keys()
                and operator['globalHidden'] == True
            )
        ):
            continue

        operator_list.append(
            TaggedOperator(
                operator['name_en'],
                operator['level'],
                operator['tags'] + [operator['type'].rstrip()]
            )
            if operator['name_en'] not in name_replacements
            else TaggedOperator(
                name_replacements[operator['name_en']],
                operator['level'],
                operator['tags'] + [operator['type'].rstrip()]
            )
        )

    return operator_list


def initialize_tag_dictionary(
    operator_list: Sequence[Type[TaggedOperator]]
) -> Dict[str, AbstractSet[str]]:
    tag_dict = {}

    with open(
        './info/recruitops/alltags.txt',
        'r',
        encoding='utf8'
    ) as f:
        current_line = f.readline()
        while current_line != '' and current_line != '\n':
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
    if operator.get_rarity() >= 6:
        return False

    return True


def get_formatted_op(operator: Type[TaggedOperator]) -> str:
    return f"{operator.get_name()}: {operator.get_rarity()}*"
######################################


def main(args: argparse.Namespace) -> None:
    spinner = Halo(text="Retrieving...", spinner="dots", color="magenta")
    spinner.start()

    op_list = initialize_operator_list()
    if op_list == None:
        spinner.fail("Failed.")
        sys.stdout.write(
            "\n\nThe tag JSON could not be fetched! Try again later."
        )
    else:
        spinner.text = "Calculating..."
        spinner.color = "yellow"

        tag_dict = initialize_tag_dictionary(op_list)

        translation_dict = read_lines_into_dict(
            './info/recruitops/tagConversions.txt'
        )
        # TODO: this is probably unnecessary
        reversed_translation_dict = read_lines_into_dict(
            './info/recruitops/formattedTagConversions.txt',
            reversed=True
        )

        proper_tags = []

        # TODO: this tag process could probably be more optimized
        for tag in args.tags:
            if tag.lower() in translation_dict.keys():
                proper_tags.append(translation_dict[tag.lower()])
            else:
                # TODO: exit nicer
                raise Exception(
                    'One or more of the tags does not exist.'
                )

        messages = []
        all_matches = []
        priority_values = {
            '1': 0,
            '2': -1,
            '3': 0,
            '4': 1,
            '5': 2,
            '6': 3,
        }

        # Since ops only have 3 tags, we get all combinations with 1-3
        # length
        for amount_of_tags in range(1, 4):
            all_combos = itertools.combinations(
                proper_tags,
                amount_of_tags
            )
            for combo in all_combos:

                # Every combo will always have at least 1 entity, so
                # we want the starting selection of operators all
                # from the first tag, which we then splice out and then
                # loop using the remaining tags.

                # note: copy is reallllyyy important
                # TODO: maybe make this better
                possible_ops = (
                    tag_dict[combo[0]].copy()
                    if translation_dict['top-operator'] in combo
                    else set(
                        filter(
                            is_not_top_op,
                            tag_dict[combo[0]].copy()
                        )
                    )
                )

                converted_string = reversed_translation_dict[combo[0]]
                for tag in combo[1:]:
                    # To prevent looping over this twice, we just get
                    # the converted chinese-to-english
                    # tag string here, and use if it we need it.
                    converted_string += " + " \
                        + reversed_translation_dict[tag]
                    # TODO: maybe make this better
                    new_ops = (
                        tag_dict[tag].copy()
                        if translation_dict['top-operator'] in combo
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

                if len(possible_ops) > 0:
                    current_match = MetadataPrioritySet(
                        possible_ops,
                        priority_values
                    )

                    current_match.add_data(
                        'tags',
                        converted_string
                    )

                    all_matches.append(current_match)

        sorted_selection = sorted(
            all_matches,
            key=lambda s: s.get_priority()
        )

        for op_set in sorted_selection:
            sorted_op_set = sorted(
                op_set.get_intrinsic_set_copy(),
                key=lambda o: o.get_rarity(),
                reverse=True
            )
            messages.append(op_set.get_data('tags'))
            messages.append(
                ", \n".join(
                    list(map(
                        get_formatted_op,
                        sorted_op_set
                    ))
                )
                + "\n"
            )

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
