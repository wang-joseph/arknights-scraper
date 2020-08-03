#!/usr/bin/env python3

"""This module is the starting point for all commands and will
call related functions based on what is specified to retrieve
information."""

import argparse

from scraper import find_all_operator_info
from recruitop import find_recruitment_combos
from recruitfuncs.tag_shortcut_editor import (
    create_tag_shortcut,
    list_tag_shortcuts,
    delete_tag_shortcut
)

# created 27/07/2020
# last edited: 31/07/2020
# version: 1.1.0
# author: Joseph Wang (EmeraldEntities)
# description: The parent argparser for everything in this scraper's
#              suite

### FUNCTIONS ########################


def initialize_scraper_args(
        parser: argparse.ArgumentParser
) -> None:
    """Set up the `scraper` subcommand's flags and arguments"""
    skills_group = parser.add_mutually_exclusive_group()
    skills_group.add_argument(
        "-s", "--skills",
        help="""Displays the max tier of each of the
                specified operator's skills.
                """,
        action="store_true"
    )
    skills_group.add_argument(
        "-v", "--vskills",
        help="""Stands for 'verbose skills'. Displays the 1st tier,
                7th tier, and M3 (if possible) tier of
                each of the specified operator's skills.
                """,
        action="store_true"
    )

    parser.add_argument(
        "operator",
        help="""The operator you want information about.
                For spaces, use a '-' in place of the space.
                No special characters. If you want info about
                multiple operators, put a space between each operator
                you want information about.
                """,
        action="extend",
        nargs="+",
        type=str
    )

    parser.add_argument(
        "-i", "--info",
        help="Displays the specified operator's stats.",
        action="store_true"
    )
    parser.add_argument(
        "-t", "--talent",
        help="Displays the specified operator's talent.",
        action="store_true"
    )
    parser.add_argument(
        "-b", "--base",
        help="Displays the specified operator's base skills.",
        action="store_true"
    )
    parser.add_argument(
        "-g", "--gamepress",
        help="""Forces the parser to only use gamepress.gg.
                Use this if your internet connection is really slow.
                """,
        action="store_true"
    )

    parser.add_argument(
        "-a", "--all",
        help="""Displays all the information about this
                specified operator. Unless paired with the -v tag,
                this will only show the max tier of each skill
                this operator has. If you want to force gamepress.gg,
                pair this with the -g tag. Otherwise, it'll use the
                default JSON-first approach.
                """,
        action="store_true"
    )

    parser.set_defaults(
        func=find_all_operator_info
    )


# def use_scraper(args: argparse.Namespace) -> None:
#     """Starts the `scraper` subcommand by calling the appropriate
#     function from the scraper module."""
#     find_all_operator_info(args)


def initialize_recruit_args(
        parser: argparse.ArgumentParser
) -> None:
    """Set up the `recruitop` subparser's the flags and arguments."""
    #TODO: make this its own folder? maybe?
    # For setting up shortcut parsers for easy shortcut binding to
    # tags (eg. defr = defender), and other parsers
    subparsers = parser.add_subparsers(
        help="Decide what recruitment option to perform.",
    )

    # The shortcut subparser
    shortcut_adder_parser = subparsers.add_parser(
        "create",
        description="Create a new shortcut for a tag."
    )

    shortcut_adder_parser.add_argument(
        "shortcut",
        help="""A name that will refer to a certain tag. If this
            shortcut already exists in the list of shortcuts, this
            command will overwrite that shortcut.""",
        type=str
    )
    shortcut_adder_parser.add_argument(
        "tag",
        help="The original tag that the new shortcut should refer to.",
        type=str
    )
    shortcut_adder_parser.set_defaults(
        func=create_tag_shortcut
    )

    # The listing subparser
    shortcut_listing_parser = subparsers.add_parser(
        "list",
        description="List all shortcuts or find a specific shortcut."
    )
    shortcut_listing_parser.add_argument(
        "mode",
        help="""Specify the specific searching mode. `all` will list
                all the shortcuts and their appropriate tag
                equivalents (or tags and their shortcut equivalents
                if paired with --reverse), while `select` allows you
                to specify a shortcut (or shortcuts) to specifically
                look up. Note that specifying shortcuts while in
                `all` mode will do nothing, as `all` mode will list
                all the shortcuts anyways.
                """,
        choices=["all", "select"],
        action="store"
    )
    shortcut_listing_parser.add_argument(
        "shortcut",
        help="""A specific shortcut or shortcuts and their tag
            equivalent to be found. Only applicable in `select` mode.
            """,
        nargs="*",
        type=str
    )
    shortcut_listing_parser.add_argument(
        "-r", "--reverse",
        help="""Instead of specifying a shortcut, allows you to specify
                a tag instead, and finds all the shortcuts that mean
                that tag. If paired with the --all command, lists all
                the tags and all the shortcuts that mean that tag.
                """,
        action="store_true"
    )
    shortcut_listing_parser.set_defaults(
        func=list_tag_shortcuts
    )

    # The deleting subparser
    shortcut_delete_parser = subparsers.add_parser(
        "delete",
        description="Delete specific shortcuts or all shortcuts."
    )
    shortcut_delete_parser.add_argument(
        "mode",
        help="""Specifies the specific deletion mode (either all the
                shortcuts or specific ones). `all` means delete all
                tags, and `select` means only delete specific ones.
                Specifying shortcuts in `all` mode is redundant, as
                `all` will delete all the shortcuts in the first place.
                """,
        choices=["all", "select"],
        action="store"
    )
    shortcut_delete_parser.add_argument(
        "shortcut",
        help="""The shortcut(s) you want to delete. Only required in
                `select` mode. You can seperate multiple shortcuts
                using spaces.""",
        nargs="*",
        type=str
    )
    shortcut_delete_parser.set_defaults(
        func=delete_tag_shortcut
    )

    # The recruitment tag subparser
    recruit_parser = subparsers.add_parser(
        "recruit",
        description="Find operators that match a recruit tag!",
        aliases=["r", "rec"]
    )

    recruit_parser.add_argument(
        "tags",
        help="""A recruitment tag specified. You can specify as many
                tags as you want here, and this CLI will look for
                operators that match all these tags. For example:
                `ark.py recruit defense defender sniper medic starter`
                Certain shortcuts exist for these tags as well, and can
                be seen in `src/info/recruitop/tagConversion.txt`.
                For spaces, use a '-' in place of the space.
                """,
        action="extend",
        nargs="+",
        type=str
    )

    recruit_parser.add_argument(
        "-b", "--beneficial",
        help="""Only displays the combinations that only give you a
                4, 5 or 6 star.
                """,
        action="store_true"
    )

    recruit_parser.set_defaults(
        func=find_recruitment_combos
    )


# def use_recruitment_parser(args: argparse.Namespace) -> None:
#     """Starts the `recruitop` subcommand by calling the appropriate
#     function from the recruitop module."""
#     find_recruitment_combos(args)


# def use_create_tag_shortcut(args: argparse.Namespace) -> None:
#     """Calls a create tag function to create a new shortcut for a
#     certain recruitment tag."""
#     create_tag_shortcut(args)

######################################


def initialize_parsers() -> argparse.ArgumentParser:
    """Initialize the parent `ark` parser, as well as the various
    subparsers available."""
    # Initialize the parser
    parser = argparse.ArgumentParser(
        description="Various information parsers about info in Arknights!"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="ark v2.3.0"
    )
    subparsers = parser.add_subparsers(help="check sub-command help")

    # Initialize scraper functionality
    scraper_parser = subparsers.add_parser(
        "scraper",
        description="""Find information about any operator
                    (or operators) in Arknights!
                    """,
        aliases=["s", "scrap", "scrape"],
        # prog=sys.argv[0] + " " + sys.argv[1]
    )
    initialize_scraper_args(scraper_parser)

    recruitment_parser = subparsers.add_parser(
        "recruitop",
        description="""Find all operators that match combinations of
                    recruitment tags, or edit shortcuts for tags for
                    future use!
                    """,
        aliases=["r", "recruit", "ro"],
        # prog=sys.argv[0] + " " + sys.argv[1]
    )
    initialize_recruit_args(recruitment_parser)

    return parser


def start_parser() -> None:
    """Starts the parser by initializing it and the subparsers, parsing
    the args, then calling the proper subparser function."""
    parser = initialize_parsers()
    # Parse args and call the appropriate function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    start_parser()
