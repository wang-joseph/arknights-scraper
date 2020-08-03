# arknights-scraper

A small scraper/parser that allows you to find detailed operator information and other arknights info right in your command line for when you're too lazy to spin up your browser to find info on the newest operator.

Designed to be a pretty small, simple, and non-instrusive project. This program won't save any information fetched. There may be some formatting errors!

There are multiple subparsers with different commands, but in general, in order to fetch the information, this program uses both [Aceship](https://github.com/Aceship)'s AMAZING json file(s) and/or [gamepress.gg](https://gamepress.gg/). Thanks to both of them!

## Libraries used

-   [requests](https://requests.readthedocs.io/en/master/) (to GET the data)
-   [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) (to help parse through the data)
-   [argparse](https://docs.python.org/3/library/argparse.html) (standard lib — so that command line works and is nice to work with)
-   [re](https://docs.python.org/3/library/re.html) (standard lib regex — useful for working with strings)
-   [json](https://docs.python.org/3/library/json.html) (standard lib — needed for working with JSON)
-   [halo](http://halo.josealerma.com/index.html) (literally the best and most important library)
-   [typing](https://docs.python.org/3/library/typing.html) (typehints classes are nice)

See requirements.txt for the versions of each library.

## Details

The only important file (and main file) is `ark.py`. Everything other file contains functions or classes that are used by this program to implement subcommands, handle format, retrieve data, etc.

### Commands

All command usage details were taken from the argparse `-h` command.

#### scraper

aliases: `{s, scrap, scrape}`

This subcommand will look for and display information about any operator currently in arknights. It'll first look at [Aceship](https://github.com/Aceship)'s JSON files and see if they have the operator. If that fails, it'll look at the [gamepress.gg](https://gamepress.gg/) page. Nothing is stored locally, and it shouldn't take that long to look the operators up!

usage: `ark.py scraper [-h] [-s | -v] [-i] [-t] [-b] [-g] [-a] operator [operator ...]`

Find information about any operator (or operators) in Arknights!

**Positional Arguments:**

-   `operator` The operator you want information about. For spaces, use a '-' in place of the space. No special characters. If you want info about multiple operators, put a space between each operator you want information about.

**Optional Arguments:**

-   `-h, --help` Show this help message and exit.
-   `-s, --skills` Displays the max tier of each of the specified operator's skills.
-   `-v, --vskills` Stands for 'verbose skills'. Displays the 1st tier, 7th tier, and M3 (if possible) tier of each of the specified operator's skills.
-   `-i, --info` Displays the specified operator's stats.
-   `-t, --talent` Displays the specified operator's talent.
-   `-b, --base` Displays the specified operator's base skills.
-   `-g, --gamepress` Forces the parser to only use gamepress.gg. Use this if your internet connection is really slow.
-   `-a, --all` Displays all the information about this specified operator. Unless paired with the -v tag, this will only show the max tier of each skill this operator has. If you want to force gamepress.gg, pair this with the -g tag. Otherwise, it'll use the default JSON-first approach.

#### recruitop

aliases: `{r, recruit, ro}`

This is a smaller subcommand that consists of 4 different subparsers, but the main purpose of this subcommand is to accept recruitment tags and show you the best combinations possible, in CLI format. The list will go from bottom-to-top in terms of priority, and any number of tags can be specified.

The list is sorted based on an experimental priority system, so if you _really_ care about getting the best combo for your buck, you can skim through all the tags and see if a certain operator stands out to you. The system should work fine if there are some distinct good combos, though. Please report anything strange!

The four subparsers that exist are `recruit`, which handles the actual recruitment search and is what is focused on here. However, the `create`, `delete`, and `list` subparsers also exist, and are there so that you can create your own custom shortcuts to tags (like how 'to' becomes 'top operator') for your convenience! If you're curious about how those work, check out the argparse `-h` command for those subparsers!

usage: `ark.py recruitop recruit [-h] [-b] tags [tags ...]`

Find all ops that match combinations of tags!

**Positional Arguments:**

-   `tags` A recruitment tag specified. You can specify as many tags as you want here, and this CLI will look for operators that match all these tags. For example: `ark.py recruit defense defender sniper medic starter`. Certain shortcuts exist for these tags as well, and can be seen in `src/info/recruitop/tagConversion.txt`. For spaces, use a '-' in place of the space.

**Optional Arguments:**

-   `-h, --help` show this help message and exit
-   `-b, --beneficial` Only displays the combinations that only give you a 4, 5 or 6 star.

## To-Do

-   [x] ~~Add basic operator information~~
    -   [x] ~~Add basic information~~
    -   [x] ~~Add support for talents~~
    -   [x] ~~Add support for skills~~
    -   [x] ~~Add support for stats~~
    -   [x] ~~Add support for base skills~~
-   [ ] Add quality of life updates
    -   [x] ~~Add different skill levels, not just max?~~
    -   [x] ~~Add multiple operator searching support~~
    -   [ ] Add support for upgrade information
-   [x] ~~Add a subparser for other commands~~
-   [x] ~~Add recruitment tag functionality~~
-   [ ] Add recruitment tag quality of life updates
    -   [x] ~~Add the ability for people to make their own aliases/shortcuts~~
    -   [ ] Make a more consistant priority system
    -   [x] ~~More options to control info (eg. contol rarity being displayed, etc)~~
    -   [x] ~~Highlight 'good recruitment combos' (ie. anything with only 4, 5, or 6 stars)~~
-   [x] ~~Restructure the project and make it look neater and ready for more subcommands~~
-   [ ] Add idk other functionality when needed
    -   [ ] Add operator comparison?
    -   [ ] Add stage functionality?
    -   [ ] Add item descriptions?
