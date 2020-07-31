"""This module contains all the functions necessary for gathering
information from Gamepress."""

import re
import sys
from bs4 import Tag
from inputfuncs.input_reader import read_line_from_file
from inputfuncs.scraper_functions import scrape_website

# created 01/07/2020
# last edited: 30/07/2020
# version: 1.3.2
# author: Joseph Wang (EmeraldEntities)


def find_siblings_of_breakpoint(soupobj):
    """Gets all the text from the sibling of a breakpoint and return as
    list of strings.

    Sometimes, a description could be formatted with a br, which
    bs4 doesn't work well with when doing o.text.strip().
    To solve that, we find the <br>'s sibling text (both previous and
    next siblings), take the text, and format the text ourselves,
    adding a `\\n` wherever needed.

    If a <br> tag isn't found, just return the object's text, stripped.
    """
    brkpoint = soupobj.find_all('br')

    # TODO: those two for loops are so similar omg
    if brkpoint != []:
        description_list = []
        prev_brk_text = []
        # previous_siblings gives you the tags in reverse,
        # so you have to reverse it after getting them all
        # also oh my freaking goodness both isinstance AND break
        # in the same block?? execute this man
        for sibling in brkpoint[0].previous_siblings:
            if isinstance(sibling, Tag):
                if sibling.name == 'br':
                    break

                prev_brk_text.append(sibling.text.strip())
            else:
                prev_brk_text.append(str(sibling))
        prev_brk_text.reverse()
        prev_brk_text[-1] += '\n'
        description_list += prev_brk_text

        # We only need to get the previous siblings for the
        # first <br> tag. Then we can just get the
        # next siblings for every other <br> tag
        # to complete the description.
        for br_tag in brkpoint:
            next_brk_text = []

            for sibling in br_tag.next_siblings:
                if isinstance(sibling, Tag):
                    if sibling.name == 'br':
                        break

                    next_brk_text.append(sibling.text.strip())
                else:
                    next_brk_text.append(str(sibling))
            next_brk_text[-1] += '\n'
            description_list += next_brk_text

        return description_list
    else:
        return soupobj.text.strip()


# Specific section locators
def find_talents(soup, images_dict):
    """Locates the talents section from the specified BeautifulSoup
    object (which should contain an operator page), formates the text,
    and returns a list of strings containing the formatted talents.

    The `images_dict` dictionary is needed to convert images into their
    CLI equivalents.

    The talents are located using the 'talent-cell' class as a
    startpoint, and formatting the text found in there.
    """
    all_cells = soup.find_all("div", "talent-cell")

    if len(all_cells) == 0:
        return ["\n\nTalents\nNo talents found!"]

    messages = []
    messages.append("\n\nTalents\n")

    for cell in all_cells:
        all_children = cell.find_all("div", "talent-child")

        for child in all_children:
            text = ""

            # Converting images to their text equivalent
            images = child.find_all("img")

            image_texts = []
            for image in images:
                image_texts.append(images_dict[image.attrs["src"]])
            # Adds a delimiter (-) and a new line to
            # seperate the text from the name of talent, pot, etc.
            # cause FORMATTING
            image_texts.append("-\n")

            # Formatting and getting rid of the newlines and whatnot
            # The lists assist with formatting and proper segmenting
            # of the talents
            all_text = []
            for string in child.stripped_strings:
                all_text.append(string)

            # inserts image_texts into all_text at index 2
            all_text[2: 2] = image_texts
            all_text[0] = all_text[0].rstrip() + " -"

            for phrase in all_text:
                text = text + phrase + " "

            text = text.rstrip()  # get rid of any placed newlines
            # extra newline to make reading a bit easier on the eyes
            messages.append(text + "\n")

    return messages


def find_base_skills(soup, images_dict):
    """Locates the base skills section in the provided BeautifulSoup
    object (which should contain an operator page), formats the text,
    and returns a list of formatted messages.

    The `images_dict` dictionary is required to convert images into
    their CLI equivalents.

    The 'building-buff-cell' class is used to find where the
    base skills are.
    """
    building_cells = soup.find_all("div", "building-buff-cell")

    if len(building_cells) == 0:
        return ["\n\nBase Skills\nNo base skills found!"]

    messages = []
    messages.append("\n\nBase Skills\n")

    if len(building_cells) == 0:
        return ["No base skills found!"]

    for cell in building_cells:
        text = ""

        # The base skills are laid out in top-cell, bottom-cell format
        # Finding them seperately helps with formatting, even if it's technically a bit slower than
        # just finding the whole div chunk and parsing with that.
        top_cell = cell.find("div", "top-cell")
        bottom_cell = cell.find("div", "bottom-cell")

        # Potentials don't help with base skills, so this is only for E1, E2, etc.
        image = images_dict[top_cell.find("img").attrs["src"]]

        # # Formatting and saving the text
        for string in top_cell.stripped_strings:
            text = text + string + "  "

        text += image + "\n "

        for string in bottom_cell.stripped_strings:
            text = text + string + " "

        messages.append(text + "\n")  # newline to make reading a bit easier

    return messages


def create_stats_json(soup, operator):
    """Creates the JSON file (dictionary) containing all the operator's stats, and returns it.

    This dictionary MUST have the basic operator stats
    (ie. atk, def, hp) and will return `None` if these
    stats are not found (if the JSON file I use for these stats is
    down, or the operator cannot be found.)

    This function will first look and load the basic stats
    (ATK, DEF, HP) for each stage.
    Then it will attempt to load (Block, Cost, Res) from the
    operator website under the variable myStats.
    Finally, it will attempt to load (Redeploy Time, Attack Interval)
    from the operator website from a different section.
    Thus, this function will look 3 times for the specified attributes.

    If any of these searches fails (except for the first one,
    which is essential), this function will simply set
    that attribute's value as -1, indicating failure to retrieve.
    """
    # Load in the json file for all operators
    # TODO: should I make a response obj to hold any possible errors?

    # Do this seperately because if I did it every time
    # that would be a waste of time
    # for requests that don't need this info.
    stats_url = read_line_from_file(
        "./info/scraper/url.txt") + "/stat-rankings?_format=json"
    stats_info = scrape_website(stats_url)

    if stats_info is None:
        # print("Could not get the JSON file!")
        return {}  # Request failed

    stats_json = None
    for json_file in stats_info.json():
        # for json_file in stats_info: # debugging
        # Find the title so that names like GreyThroat don't screw
        # up the parser.
        if json_file["title"].title() == operator:
            stats_json = json_file
            break  # whoa a bad break

    if stats_json is None:
        # print("No operator found!")
        return {}  # No operator found in the big JSON file

    # Find myStats from the operator's site
    # This is so we can find res, cost, and block
    good_scripts = soup.find_all('script', '')
    for script in good_scripts:
        if re.search(r"myStats =", str(script)):
            mystats_script = script
            break  # oh no another bad break

    levels = ["ne", "e1", "e2"]
    wanted_attributes = ["arts", "cost", "block"]

    # We're gonna find every stage of each wanted attribute,
    # and then add each stage to our stats json.
    for attr in wanted_attributes:
        all_stats = (
            re.findall(
                fr'"{attr}": "(\d+)"', str(mystats_script)
            )
        )

        # Since 'block' has both a base and max (which doesn't matter),
        # we're gonna only take every other index.
        if attr == 'block':
            all_stats = all_stats[::2]

        # Make sure that all_stats has SOMETHING in it.
        # We can't just check for 3 cause some operators don't have E2s
        # or E1s
        if len(all_stats) != 0:
            for stat, lvl in zip(all_stats, levels):
                # We're gonna manually add the stat to our
                # stats_json dictionary so we can format it later
                stats_json[lvl + "_" + attr] = \
                    int(stat)
        else:
            # Just to make sure we don't break the program later
            # if there's a bad parse somewhere
            #
            # We'll set every level to -1, because when the program
            # later parses these stats, it checks to see if
            # level_atk in stats_dict is empty. If it has something in
            # level_atk but nothing here, it'll break, but if it has
            # nothing in level_atk but something here, nothing happens.
            for lvl in levels:
                # -1 to symbolize failure
                stats_json[lvl + "_" + attr] = -1

    # other_stats will provide us with the atk speed
    # and redeploy time stats.
    other_stats = soup.find_all('div', 'other-stat-value-cell')

    if len(other_stats) > 0:
        # Convert every object into their stripped strings counterpart
        for stat in other_stats:
            cur_stats_list = []
            for string in stat.stripped_strings:
                cur_stats_list.append(string)

            if "Attack Interval" in cur_stats_list:
                stats_json['atk_int'] = float(cur_stats_list[-1])

            elif "Redeploy Time" in cur_stats_list:
                stats_json['deploy_time'] = int(cur_stats_list[-1])

    # Failsafes, in case
    stats_json['atk_int'] = (
        -1
        if 'atk_int' not in stats_json.keys()
        else stats_json['atk_int']
    )
    stats_json['deploy_time'] = (
        -1
        if 'deploy_time' not in stats_json.keys()
        else stats_json['deploy_time']
    )

    return stats_json


def find_skills(soup, tiers_to_check):
    """Locates the skills section in the provided BeautifulSoup
    object (which should contain an operator page), formats the text,
    and returns a list of formatted messages.

    The tiers-to-check list is to choose a certain amount of skill
    tiers to display.

    The 'skill-cell' class is used to find where the skills are
    stored.
    """
    # skill-cell is the class name that all skill blocks have,
    # so we need to get them all
    all_skills = soup.find_all('div', 'skill-cell')

    # If the operator doesn't have any skill blocks,
    # they don't have any skills we can parse
    if len(all_skills) == 0:
        return ["\n\nSkills\nNo skills found!"]

    messages = []
    # does not have a trailing newline cause a newline
    # is inserted before every skill title, and I like
    # consistant formatting
    messages.append("\n\nOperator Skills")

    for skill in all_skills:
        # Finding the skill title
        # add an extra newline after every different
        # skill for readability
        messages[-1] += '\n'
        title = skill.find('div', 'skill-title-cell')
        messages.append(title.text.strip())

        for tier in tiers_to_check:
            max_upgrade_level = tier
            max_level = skill.find_all('div', max_upgrade_level)

            # Getting the right level for the skill
            sp_string = ""
            if int(tier[-1:]) in [8, 9, 0]:
                mastery_number = 3 if int(
                    tier[-1:]) == 0 else int(tier[-1:]) - 7
                sp_string += f"{'Lv7 M' + str(mastery_number):15}"
            else:
                sp_string += f"{'Lv' + tier[-1:]:15}"

            for i, lvl in enumerate(max_level):
                # Since the page uses <br> to split text,
                # we're gonna find the <br>, find the text before
                # and after it, and use it for ourselves too.
                #
                # This will work for multiple br tags
                max_level[i] = "".join(
                    find_siblings_of_breakpoint(lvl)
                )

            # Add some informative text to max level
            max_level[0] = "SP cost: " + max_level[0]
            max_level[1] = "Initial SP: " + max_level[1]
            max_level[2] = "Duration: " + max_level[2]
            # The description will always be whatever is
            # after the first 3 chunks of text
            description = max_level[3:]

            # Using f-string width formatting, we can get the
            # width of each text to be the same
            #
            # Remember --
            # max_level[0] is spcost
            # max_level[1] is initialsp
            # max_level[2] is duration
            sp_string += f"{max_level[0]:18}{max_level[1]:22}{max_level[2]}"

            messages.append(sp_string)

            # Filter out any "" that might be appended and any extra \n
            # Adding a space before every description
            # for good readability
            description[0] = ' ' + description[0]
            description = list(map(lambda x: x.rstrip(), description))
            description = list(filter(lambda x: x != "", description))

            # Add a '-' * 25 and/or \n to the last item in description
            # for consistent formatting!!!!!
            messages = (
                messages + description + ['--------------------\n']
                if len(tiers_to_check) > 1
                else messages + description
            )

        # Get rid of the last \n in all messages for
        # consistent formatting!!!!!!
        messages[-1] = messages[-1].rstrip()
        # Add an empty string in a list to the end for
        # consistent formatting!!!!!!!
        messages += ['']
    return messages


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `ark.py`.\n\n"
    )
