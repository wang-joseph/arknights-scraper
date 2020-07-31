"""This module contains all the implementation for the 'scraper'
function in the 'ark' library, with both JSON parsing and Gamepress
implementation implemented"""

import argparse
import sys

from halo import Halo  # extremely important
from bs4 import BeautifulSoup

from operatorclasses.operator import Operator

from inputfuncs.input_reader import (
    read_lines_into_dict,
    read_line_from_file
)
from inputfuncs.scraper_functions import (
    scrape_for_operator,
    scrape_json
)
from scraperfuncs.global_parser_functions import parse_stats

# Import the needed search functions for Gamepress
from scraperfuncs.gamepress_search_functions import (
    find_talents,
    find_base_skills,
    create_stats_json,
    find_siblings_of_breakpoint,
    find_skills
)

# Import the needed search functions for Aceship's JSON
from scraperfuncs.json_parser_functions import (
    filter_description,
    create_stats_dict,
    parse_talents,
    parse_skills,
    parse_base_skills
)

# created 06/06/2020
# last edited: 29/07/2020
# version: 2.2.1
# author: Joseph Wang (EmeraldEntities)
# description: a CLI scraper designed to find all information about an
#              operator on gamepress, etc.

### FUNCTIONS ########################


def get_operator_dict(operator):
    """Searches the Aceship character JSON for a specified operator,
    and returns the associated character dict and the character key
    in the JSON if found.

    If the operator was not found, return an empty dict and None
    for the key, indicating that the scraper should try using
    Gamepress instead of the JSON, as the character is not
    in the JSON yet.
    """
    # Since the JSON I first use to find info uses
    # properly formatted names, I have to convert any name
    # to a properly formatted one

    # TODO: Does this break DRY? This appears in gamepress too
    replacement_names = read_lines_into_dict(
        "./info/scraper/jsonOperatorReplacements.txt"
    )

    formatted_name = operator.replace("-", " ").title()
    proper_name = (
        formatted_name
        if formatted_name not in replacement_names.keys()
        else replacement_names[formatted_name]
    )

    # with open("character_table.json", "r", encoding="utf8") as f:
    #     operator_raw_json = json.load(f)  # debug
    operator_raw_json = scrape_json(read_line_from_file(
        "./info/scraper/operatorJsonUrl.txt"
    ))
    if operator_raw_json is None:
        return {}, None

    operator_dict = {}
    operator_key = None
    operator_json = operator_raw_json.json()
    # operator_json = operator_raw_json #debug
    for operator in operator_json.keys():
        # So that names like "SilverAsh" don't screw up the parser,
        # we take the key and convert it to the title form (Silverash)
        if operator_json[operator]["name"].title() == proper_name:
            operator_key = operator
            operator_dict = operator_json[operator]
            break

    return operator_dict, operator_key


def parse_operator_data(
        args,
        operator_dict,
        operator_key,
        operator
):
    """ Depending on whether operator_dict is empty or not, get
    operator information from either Gamepress or the JSON files,
    and return an Operator object with all the needed information.
    """
    if operator_dict == {} or args.gamepress:
        operator = get_info_from_gamepress(
            args,
            operator
        )
    else:
        operator = parse_info_from_json(
            args,
            operator_dict,
            operator_key
        )

    return operator


def get_info_from_gamepress(args, operator_name):
    """Gets information for a certain operator from a Gamepress
    page, and return an Operator object with the necessary information
    based on the flags in args.

    If no Gamepress page is found with the specified operator's name
    (or the page is down), this function will return None.

    This function independantly gathers the barebones information
    (name, rarity, description, etc.), but then creates a
    'conditional list' (That is, consisting of a function to call,
    a conditional (usually a flag), and arguments). That is then
    passed to another function that matches those conditionals, calls
    the appropriate, necessary functions which return information,
    which is then assigned to the Operator object that is
    to be returned.
    """
    response = scrape_for_operator(operator_name)
    if response is not None:  # response succeeds
        src = response.content

        images_dict = read_lines_into_dict(
            "./info/scraper/imageToText.txt"
        )
        replacement_names = read_lines_into_dict(
            "./info/scraper/jsonOperatorReplacements.txt"
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
                    find_siblings_of_breakpoint(desc[item])).strip() + "\n"
                for item in range(3)
            ]
        )

        # Since the alternative JSON I use to find stats may have
        # another name for an operator, I have to convert any name
        # to a proper one recognized by that specific json
        formatted_name = operator_name.replace("-", " ").title()
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
        # with skills info gathering.

        if args.vskills:
            skill_tiers_to_check = (
                [
                    "skill-upgrade-tab-1",
                    "skill-upgrade-tab-7",
                    "skill-upgrade-tab-10"
                ]
                if rarity > 3
                else [
                    "skill-upgrade-tab-1",
                    "skill-upgrade-tab-7"
                ]
            )
        else:
            skill_tiers_to_check = (
                ["skill-upgrade-tab-10"]
                if rarity > 3
                else ["skill-upgrade-tab-7"]
            )

        check_skills = args.skills or args.vskills

        # Taking advantage of python's functional programming paradigms
        # to adhere to DRY principles

        # TODO: is this even good practice???
        # I'm trying to adhere to DRY principles but this makes me
        # start to sweat and foam at the mouth
        conditionals = [
            [
                "skills",
                check_skills,
                find_skills,
                [soup, skill_tiers_to_check]
            ],
            [
                "talent",
                args.talent,
                find_talents,
                [soup, images_dict]
            ],
            [
                "base skills",
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
        # Set the operator object's properties based on conditional
        # list
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
    """Gets information for a certain operator from various JSON
    files, and return an Operator object with the necessary information
    based on the flags in args.

    This function assumes a check was already done to ensure the
    operator exists in the JSON files.

    Like the Gamepress function, this function independantly
    gathers the barebones information (name, rarity, description, etc.),
    but then creates a 'conditional list' (That is, consisting of a
    function to call for each property, a conditional (usually a flag),
    and arguments).

    That is then passed to another function that matches those
    conditionals, calls the appropriate, necessary functions which
    return information, which is then assigned to the Operator object
    that is to be returned.
    """
    description_text = filter_description(operator_dict["description"])

    formatted_json_prof = read_lines_into_dict(
        "./info/scraper/formattedJsonProfessions.txt"
    )
    # Set up the operator object with the good fetches
    operator = Operator(
        operator_dict["name"],
        operator_dict["rarity"] + 1,
        formatted_json_prof[operator_dict["profession"].title()],
        [
            description_text + "\n",
            operator_dict["itemUsage"] + "\n",
            operator_dict["itemDesc"] + "\n\n"
        ],
        operator_dict["tagList"],
    )

    # This is repeated but I feel that's fine for abstraction
    if args.vskills:
        skill_tiers_to_check = (
            [1, 7, 10]
            if operator_dict["rarity"] + 1 > 3
            else [1, 7]
        )
    else:
        skill_tiers_to_check = (
            [10]
            if operator_dict["rarity"] + 1 > 3
            else [7]
        )

    check_skills = args.skills or args.vskills

    conditionals = [
        [
            "skills",
            check_skills,
            parse_skills,
            [operator_dict, skill_tiers_to_check]
        ],
        [
            "talent",
            args.talent,
            parse_talents,
            [operator_dict]
        ],
        [
            "base skills",
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
    """With the specified operator, initializes the operator's
    properties and stats.

    Depending on the specified conditions and whether they were met
    or not, this function will call each properties' associated
    find/parse function with the specified arguments in each
    condition. That way, each Operator object will only have
    the necessary amount of information, as opposed to all the
    information, to cut down on request calls.

    Since the operator specified is expected to be an Operator object,
    this function will return nothing as all changes would be to the
    actual operator object.
    """
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


def find_operator_info(
        args: argparse.Namespace,
        operator_name: str
) -> None:
    """With the specified arguments, calls all the functions
    needed to find information and print all information
    out to the screen.

    This function will determine whether to use Gamepress
    or JSON for information, then call either one's appropriate
    information-getting functions and build an Operator object using
    the provided information.

    The Operator object will be used for printing. Nothing is returned.
    """
    spinner = Halo(text="Fetching...", spinner="dots", color="magenta")
    # Initialize the arguments for cmd purposes
    spinner.start()

    operator_dict, operator_key = get_operator_dict(operator_name)

    spinner.text = "Parsing..."
    spinner.color = "yellow"

    operator = parse_operator_data(
        args,
        operator_dict,
        operator_key,
        operator_name)
    # ----------------------------------------

    if operator is not None:
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
                sys.stdout.write(text + "\n")

    else:
        spinner.fail("Failed.")
        sys.stdout.write(
            "\n\n"
            + operator_name.replace("-", " ").title()
            + "\n"
        )
        sys.stdout.write(
            "\n"
            + "Could not find operator! "
            + "Either the server is down, or your spelling is! \n"
        )

    sys.stdout.write("\n\n")


def find_all_operator_info(
        args: argparse.Namespace
) -> None:
    """Finds each operator's info as specified in args.operator and
    prints the info the the screen."""
    for index, operator in enumerate(args.operator):
        find_operator_info(args, operator)
        sys.stdout.write(
            ""
            if index + 1 == len(args.operator)
            else "------------------------------------\n\n"
        )


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
