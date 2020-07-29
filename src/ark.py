#!/usr/bin/env python3

import sys
import argparse
from typing import Type

# created 27/07/2020
# last edited: 27/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: The parent argparser for everything in this scraper's
#              suite

### FUNCTIONS ########################


def initialize_scraper_args(
    parser: Type[argparse.ArgumentParser]
) -> None:
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
        action='store_true'
    )

    parser.add_argument(
        "operator",
        help="""The operator you want information about. 
                For spaces, use a '-' in place of the space. 
                No special characters.
                """,
        type=str,
        # nargs='+'  # TODO: multiple operator support??
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
        '-g', '--gamepress',
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
                this operator has.
                """,
        action="store_true"
    )

    parser.set_defaults(
        func=use_scraper
    )


def use_scraper(args: argparse.Namespace) -> None:
    from scraper import main

    main(args)


def initialize_recruit_args(
    parser: Type[argparse.ArgumentParser]
) -> None:
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
    from recruitop import main

    main(args)

######################################


def main() -> None:
    # Initialize the parser
    parser = argparse.ArgumentParser(
        description="Various information parsers about info in Arknights!"
    )
    parser.add_argument(
        '--version',
        action='version',
        version='ark v2.2.0'
    )
    subparsers = parser.add_subparsers(help='check sub-command help')

    # Initialize scraper functionality
    scraper_parser = subparsers.add_parser(
        'scraper',
        description="Find information about any operator in Arknights!",
        aliases=['s', 'scrap'],
        # prog=sys.argv[0] + " " + sys.argv[1]
    )
    initialize_scraper_args(scraper_parser)

    recruitment_parser = subparsers.add_parser(
        'recruitop',
        description="Find all ops that match combinations of recruitment tags!",
        aliases=['r', 'recruit', 'ro'],
        # prog=sys.argv[0] + " " + sys.argv[1]
    )
    initialize_recruit_args(recruitment_parser)

    # Parse args and call the appropriate function
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
