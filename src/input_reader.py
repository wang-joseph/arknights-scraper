import re
import sys

# created 01/07/2020
# last edited: 07/07/2020
# version: 1.1.0
# author: Joseph Wang (EmeraldEntities)
# description: These are just basic input functions that I'll use
# in various different functions.


def read_line_from_file(file):
    """Reads one line from a file and returns it as string."""
    with open(file, "r") as f:
        result = f.readline()

    return result


def read_lines_into_dict(file):
    """Reads multiple lines from a file and returns it as a dict."""
    new_dict = {}

    with open(file, "r") as f:
        current_line = f.readline()

        while current_line != "\n":
            line_info = re.split(r'\s+', current_line.rstrip())

            line_info[0] = line_info[0].replace('+', ' ')
            line_info[1] = line_info[1].replace('+', ' ')

            new_dict[line_info[0]] = line_info[1]

            current_line = f.readline()
    return new_dict


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `scraper.py`.\n\n"
    )
