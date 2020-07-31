#!/usr/bin/env python3

"""This module is the starting point for all commands and will
call related functions based on what is specified to retrieve
information."""

import argparse

from scraper import find_all_operator_info
from recruitop import find_recruitment_combos

# created 27/07/2020
# last edited: 29/07/2020
# version: 1.0.0
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
        func=use_scraper
    )


def use_scraper(args: argparse.Namespace) -> None:
    """Starts the `scraper` subcommand by calling the appropriate
    function from the scraper module."""
    find_all_operator_info(args)


def initialize_recruit_args(
        parser: argparse.ArgumentParser
) -> None:
    """Set up the `recruitop` subparser's the flags and arguments."""
    parser.add_argument(
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

    parser.add_argument(
        "-b", "--beneficial",
        help="""Only displays the combinations that only give you a
                4, 5 or 6 star.
                """,
        action="store_true"
    )

    parser.set_defaults(
        func=use_recruitment_parser
    )


def use_recruitment_parser(args: argparse.Namespace) -> None:
    """Starts the `recruitop` subcommand by calling the appropriate
    function from the recruitop module."""
    find_recruitment_combos(args)

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
                    recruitment tags!
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
