"""A module that contains functions related to retrieving information
from a web source, instead of a file."""

import sys
import requests
from inputfuncs.input_reader import (
    read_line_from_file,
    read_lines_into_dict
)


def scrape_website(url):
    """Sends a GET request to a certain url and returns the Response
    object if status code is 200.

    Returns None if the server responds with a different code.
    """
    result = requests.get(url)

    # if (True): # debugging
    if result.status_code == 200:
        return result

    return None


def scrape_for_operator(operator):
    """Sends a GET request for a certain operator and returns the
    Response object if status code is 200.

    Returns None (as per scrape_website() implementation) if server
    responds with a different code.
    """
    url_replacement_names = read_lines_into_dict(
        "./info/scraper/urlOperatorReplacements.txt")

    operator_url = read_line_from_file("./info/scraper/url.txt")
    operator_url = (
        operator_url + "operator/" + operator
        if operator not in url_replacement_names.keys()
        else operator_url + "operator/"
        + url_replacement_names[operator]
    )

    return scrape_website(operator_url)


def scrape_json(json_url):
    """Sends a GET request to a JSON url for a certain operator and
    returns the Response object if status code is 200.

    Returns None (as per scrape_website() implementation) if server
    responds with a different code.
    """

    return scrape_website(json_url)


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
