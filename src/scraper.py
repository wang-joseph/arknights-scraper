import requests
import argparse
import sys
import re
import json  # json parsing
from halo import Halo  # extremely important
from bs4 import BeautifulSoup

from operatorclasses.Operator import Operator

from input_reader import read_lines_into_dict, read_line_from_file
from scraper_functions import (
    scrape_website,
    scrape_for_operator,
    scrape_json
)
from global_parser_functions import parse_stats

# created 06/06/2020
# last edited: 27/07/2020
# version: 2.2.0
# author: Joseph Wang (EmeraldEntities)
# description: a CLI scraper designed to find all information about an
#              operator on gamepress, etc.

### FUNCTIONS ########################


def get_operator_dict(operator):
    # Since the JSON I first use to find info uses
    # properly formatted names, I have to convert any name
    # to a properly formatted one

    # TODO: Does this break DRY? This appears in gamepress too
    replacement_names = read_lines_into_dict(
        "./info/jsonOperatorReplacements.txt"
    )

    formatted_name = operator.replace("-", " ").title()
    proper_name = (
        formatted_name
        if formatted_name not in replacement_names.keys()
        else replacement_names[formatted_name]
    )

    # with open('character_table.json', 'r', encoding="utf8") as f:
    #     operator_raw_json = json.load(f)  # debug
    operator_raw_json = scrape_json(read_line_from_file(
        "./info/operatorJsonUrl.txt"
    ))
    if operator_raw_json == None:
        return {}

    operator_dict = {}
    operator_key = None
    operator_json = operator_raw_json.json()
    # operator_json = operator_raw_json #debug
    for operator in operator_json.keys():
        if operator_json[operator]['name'] == proper_name:
            operator_key = operator
            operator_dict = operator_json[operator]
            break

    return operator_dict, operator_key


def parse_operator_data(args, operator_dict, operator_key):
    if operator_dict == {} or args.gamepress:
        operator = get_info_from_gamepress(
            args
        )
    else:
        operator = parse_info_from_json(
            args,
            operator_dict,
            operator_key
        )

    return operator


def get_info_from_gamepress(args):
    # Import the needed search functions for Gamepress
    from gamepress_search_functions import (
        find_talents,
        find_base_skills,
        create_stats_json,
        find_siblings_of_breakpoint,
        find_skills
    )

    response = scrape_for_operator(args.operator)
    if response != None:
        src = response.content

        images_dict = read_lines_into_dict("./info/imageToText.txt")
        replacement_names = read_lines_into_dict(
            "./info/jsonOperatorReplacements.txt"
        )

        soup = BeautifulSoup(src, "lxml")
        # soup = BeautifulSoup(open("debug.html", "r", encoding="utf-8"), "lxml") # debugging

        # Finding the default information that should be displayed
        # for every operator (eg. tags, description, etc.)
        tags = list(
            map(
                lambda souptxt: souptxt.text.strip(),
                soup.find_all("div", "tag-title")
            )
        )

        # We can find the rarity of an operator by finding the div
        # named rarity-cell and counting how many images of stars
        # are in it
        rarity = len(soup.find("div", "rarity-cell").find_all("img"))

        profession_text = (
            soup.find("div", "profession-title")
            .text.strip()
        )

        desc = soup.find_all("div", "description-box")

        desc_text = (
            ["No proper description."]
            if (len(desc) < 3)
            else [
                "".join(
                    find_siblings_of_breakpoint(desc[item])).strip() + '\n'
                for item in range(3)
            ]
        )

        # Since the alternative JSON I use to find stats may have
        # another name for an operator, I have to convert any name
        # to a proper one recognized by that specific json
        formatted_name = args.operator.replace("-", " ").title()
        proper_name = (
            formatted_name
            if formatted_name not in replacement_names.keys()
            else replacement_names[formatted_name]
        )

        operator = Operator(
            proper_name,
            rarity,
            profession_text,
            desc_text,
            tags
        )

        # Any optional messages/properties are stored in
        # operator.properties for convenience and also to make sure
        # that printing properties doesn't take 50 lines of code.
        # Also, we can reuse the properties this way as it is stored
        # in a compact location.

        # Skills are different; since we have a mutually exclusive group
        # we need to format input a tiny bit before we continue
        # with skills.

        if args.vskills:
            skill_tiers_to_check = ([
                'skill-upgrade-tab-1',
                'skill-upgrade-tab-7',
                'skill-upgrade-tab-10'
            ]
                if rarity > 3
                else [
                'skill-upgrade-tab-1',
                'skill-upgrade-tab-7'
            ])
        else:
            skill_tiers_to_check = (
                ['skill-upgrade-tab-10']
                if rarity > 3
                else ['skill-upgrade-tab-7']
            )

        check_skills = args.skills or args.vskills

        # Taking advantage of python's functional programming paradigms
        # to adhere to DRY principles

        # TODO: is this even good practice???
        # I'm trying to adhere to DRY principles but this makes me
        # start to sweat and foam at the mouth
        conditionals = [
            [
                'skills',
                check_skills,
                find_skills,
                [soup, skill_tiers_to_check]
            ],
            [
                'talent',
                args.talent,
                find_talents,
                [soup, images_dict]
            ],
            [
                'base skills',
                args.base,
                find_base_skills,
                [soup, images_dict]
            ],
        ]

        stats_requirements = [
            args.info,
            create_stats_json,
            [soup, proper_name]
        ]
        set_operator_properties(
            args,
            conditionals,
            stats_requirements,
            operator
        )
    else:
        # The request failed, operator not found
        operator = None

    return operator


def parse_info_from_json(args, operator_dict, operator_key):
    # Import the needed search functions for Aceship's JSON
    from json_parser_functions import (
        filter_description,
        create_stats_dict,
        parse_talents,
        parse_skills,
        parse_base_skills
    )

    description_text = filter_description(operator_dict['description'])

    formatted_json_prof = read_lines_into_dict(
        './info/formattedJsonProfessions.txt'
    )
    # Set up the operator object with the good fetches
    operator = Operator(
        operator_dict['name'],
        operator_dict['rarity'] + 1,
        formatted_json_prof[operator_dict['profession'].title()],
        [
            description_text + '\n',
            operator_dict['itemUsage'] + '\n',
            operator_dict['itemDesc'] + '\n\n'
        ],
        operator_dict['tagList'],
    )

    # This is repeated but I feel that's fine for abstraction
    if args.vskills:
        skill_tiers_to_check = (
            [1, 7, 10]
            if operator_dict['rarity'] + 1 > 3
            else [1, 7]
        )
    else:
        skill_tiers_to_check = (
            [10]
            if operator_dict['rarity'] + 1 > 3
            else [7]
        )

    check_skills = args.skills or args.vskills

    conditionals = [
        [
            'skills',
            check_skills,
            parse_skills,
            [operator_dict, skill_tiers_to_check]
        ],
        [
            'talent',
            args.talent,
            parse_talents,
            [operator_dict]
        ],
        [
            'base skills',
            args.base,
            parse_base_skills,
            [operator_key]
        ],
    ]

    stats_requirements = [
        args.info,
        create_stats_dict,
        [operator_dict]
    ]

    set_operator_properties(
        args,
        conditionals,
        stats_requirements,
        operator
    )

    return operator


def set_operator_properties(args, conds, stats_conds, operator):
    # Checking and calling the appropriate functions
    # for optional flags

    # Also note: we don't actually guarantee each opoerator
    # will have every property for efficency's sake.
    # We just make sure that the operator object has what it needs
    for prop, flag, find_info_function, arguments in conds:
        if flag or args.all:
            operator.set_property(prop, find_info_function(*arguments))

    stats_flag, stats_func, stats_args = stats_conds
    if stats_flag or args.all:
        operator.set_stats(stats_func(*stats_args))

######################################


def main(args: argparse.Namespace) -> None:
    spinner = Halo(text="Fetching...", spinner="dots", color="magenta")
    # Initialize the arguments for cmd purposes
    spinner.start()

    # TODO: reformat this code to make it more logical and stuff
    operator_dict, operator_key = get_operator_dict(args.operator)

    spinner.text = "Parsing..."
    spinner.color = "yellow"

    operator = parse_operator_data(args, operator_dict, operator_key)
    # ----------------------------------------

    if operator != None:
        spinner.succeed("Success!")
        if operator_dict == {} or args.gamepress:
            sys.stdout.write("\nSkipping JSON; Using gamepress.\n")

        # Print out the results
        sys.stdout.write("\n\n" + operator.name + "   ")
        sys.stdout.write("*" * operator.rarity + "   ")  # Star rarity
        sys.stdout.write(operator.profession + "\n")

        sys.stdout.write(operator.get_formatted_tags() + "\n\n")

        for desc_text in operator.description:
            sys.stdout.write(desc_text)

        all_properties = [
            operator.get_property(prop)
            for prop in operator.get_all_properties()
        ]
        # Fetch the stats
        all_messages = (
            [parse_stats(operator.get_all_stats())] + all_properties
            if (operator.has_stats())
            else all_properties
        )

        for prop in all_messages:
            for text in prop:
                sys.stdout.write(text + '\n')

    else:
        spinner.fail("Failed.")
        sys.stdout.write(
            "\n\n"
            + args.operator.replace("-", " ").title()
            + "\n"
        )
        sys.stdout.write(
            "\n"
            + "Could not find operator! "
            + "Either the server is down, or your spelling is! \n"
        )

    sys.stdout.write("\n\n")


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
