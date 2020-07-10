import sys
import re
import json

from input_reader import read_line_from_file, read_lines_into_dict
from scraper_functions import scrape_json

# created 05/07/2020
# last edited: 09/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: These functions are to parse information from Aceship's excellent JSON file.


def filter_description(description):
    description_text = (
        description
        .replace('</>', '')
        .replace('<', '')
        .replace('>', ' ')
    )

    description_text = re.sub(
        r' *(@[a-zA-Z]+\.[a-zA-Z]+) *',
        " ",
        description_text
    )

    return description_text


# Specific section locators
def create_stats_dict(operator_dict):
    stats = {}

    # The JSON is greater than 80k lines long, I'm just gonna throw
    # this check here just so that this program doesn't
    # die if these aren't here
    if 'phases' in operator_dict.keys() \
            and len(operator_dict['phases']) > 0 \
            and 'attributesKeyFrames' in operator_dict['phases'][0].keys() \
            and len(operator_dict['phases'][0]['attributesKeyFrames']) > 0 \
            and 'data' in operator_dict['phases'][0]['attributesKeyFrames'][0].keys():

        all_stats = operator_dict['phases']

        attrs = [  # we're gonna use $ as a substitution indicator
            ('max_atk$', 'atk'),
            ('max_def$', 'def'),
            ('max_hp$', 'maxHp'),
            ('$_arts', 'magicResistance'),
            ('$_block', 'blockCnt'),
            ('$_cost', 'cost'),
        ]

        levels = ['ne', 'e1', 'e2']
        levels = levels[:len(all_stats)]

        # set up the basic stats (eg. hp, atk, etc...)
        for i, lvl in zip(range(len(all_stats)), levels):
            for attr in attrs:
                # Always grab the max level's stats
                stats[
                    attr[0].replace('$', lvl)
                ] = all_stats[i]['attributesKeyFrames'][1]['data'][attr[1]]

        stats['atk_int'] = (
            all_stats[0]['attributesKeyFrames'][0]['data']['baseAttackTime']
        )
        stats['deploy_time'] = (
            all_stats[0]['attributesKeyFrames'][0]['data']['respawnTime']
        )

        stats['atk_int'] = (
            -1
            if 'atk_int' not in stats.keys()
            else stats['atk_int']
        )
        stats['deploy_time'] = (
            -1
            if 'deploy_time' not in stats.keys()
            else stats['deploy_time']
        )

        return stats

    else:
        return {}


def parse_talents(operator_dict):
    messages = []
    messages.append("\n\nTalents\n")

    # We're gonna first make sure everything is there so the
    # program doesn't kill itself.
    if 'talents' in operator_dict.keys() \
            and len(operator_dict['talents']) > 0:
        # The JSON is well formatted, so our code doesn't
        # need to be too detailed. We can just fetch the data
        # and format it how we want to.
        for talent in operator_dict['talents']:
            for stage in talent['candidates']:
                messages.append(
                    stage['name'] + " - "
                    + "Lvl " + str(stage['unlockCondition']['level'])
                    + " "
                    + "E" + str(stage['unlockCondition']['phase'])
                    + " "
                    + "Pot" + str(stage['requiredPotentialRank'] + 1)
                    + " - "
                )
                messages.append(
                    " "
                    + filter_description(stage['description'])
                    + "\n"
                )

        return messages
    else:
        # Assuming nothing was found, we can assume this operator
        # has no talents (though I dunno if this will ever run...)
        return ["\n\nTalents\nNo talents found!"]


def get_base_jsons():
    # with open('building_data_zh.json', 'r', encoding="utf8") as f:
    #     base_skills_json = json.load(f)  # debug
    base_skills_req = scrape_json(read_line_from_file(
        "./info/baseSkillsJsonUrl.txt"
    ))
    riic_req = scrape_json(read_line_from_file(
        "./info/riicJsonUrl.txt"
    ))
    base_skills_json, riic_json = {}, {}

    if base_skills_req != None:
        base_skills_json = base_skills_req.json()
    if riic_req != None:
        riic_json = riic_req.json()

    # with open('riic.json', 'r', encoding='utf8') as f:
    #     riic_json = json.load(f)

    return base_skills_json, riic_json


def parse_base_skills(operator_key):
    # We'll have to load in two seperate jsons...
    base_skills_json, riic_json = get_base_jsons()

    # If the jsons fail to load, or if the key can't be found in the
    # base skills json, we have to quit so our program
    # doesn't kill itself.
    if base_skills_json == {} or riic_json == {}:
        return ["\n\nBase Skills\nBase skill JSONs failed to load!"]

    if operator_key not in base_skills_json['chars'].keys():
        return ["\n\nBase Skills\nCould not find matching base skill!"]

    messages = []
    messages.append("\n\nBase Skills\n")

    # Since we want to remain consistent with gamepress description,
    # we have a file that converts the shorter room names to the proper
    # room names that we'll be displaying.
    formatted_JSON_rooms = read_lines_into_dict(
        './info/formattedJsonRooms.txt'
    )

    char = base_skills_json['chars'][operator_key]
    # Looks messy, but needed for traversing the jsons
    for bchar in char['buffChar']:
        if len(bchar['buffData']) > 0:
            for bskill in bchar['buffData']:
                # We're just trying to replicate what is got
                # from gamepress.gg
                bskill_info = riic_json[bskill['buffId']]

                zh_bskill_info = \
                    base_skills_json['buffs'][bskill['buffId']]

                messages.append(
                    bskill_info['name']
                    + "  "
                    + "Lvl: "
                    + str(bskill['cond']['level'])
                    + "  "
                    + "(" + zh_bskill_info['buffName'] + ")"
                    + "  "
                    + "Room Type:  "
                    + formatted_JSON_rooms[
                        zh_bskill_info['roomType'].title()
                    ]
                    + "  "
                    + "E" + str(bskill['cond']['phase'])
                )

                messages.append(
                    " " + bskill_info['desc'] + "\n"
                )

    return messages


def get_skill_jsons():
    # with open('skill_table.json', 'r', encoding="utf8") as f:
    #     skills_json = json.load(f)  # debug
    skills_req = scrape_json(read_line_from_file(
        "./info/skillsJsonUrl.txt"
    ))
    skills_json = {}

    if skills_req != None:
        skills_json = skills_req.json()

    return skills_json


def parse_skills(operator_dict, tiers_to_check):
    skills_json = get_skill_jsons()
    # If failed to load skills_json
    if skills_json == {}:
        return ["\n\nSkills\nSkill JSON failed to load!"]

    # Couldn't find any skills...
    if 'skills' not in operator_dict.keys() \
            or len(operator_dict['skills']) <= 0:
        return ["\n\nSkills\nNo skills found!"]

    messages = []
    messages.append("\n\nOperator Skills")

    for skillnum in range(len(operator_dict['skills'])):
        skill = operator_dict['skills'][skillnum]

        if skill['skillId'] in skills_json.keys():
            messages[-1] += '\n'

            skill_info = skills_json[skill['skillId']]

            # Get the name of the skill
            messages.append(
                "Skill " + str(skillnum + 1) + ": "
                + skill_info['levels'][0]['name']
            )

            for tier in tiers_to_check:
                skill_tier = skill_info['levels'][tier-1]

                # Find the skill point requirements
                # (eg. cost, inital, etc)
                # And the level of the skill
                if tier in [8, 9, 10]:
                    lvl_string = f"{'Lv7 M' + str(abs(7-tier)):15}"
                else:
                    lvl_string = f"{'Lv' + str(tier):15}"

                # Variables to save space
                sp_cost = (
                    'SP cost: ' + str(skill_tier['spData']['spCost']))
                sp_init = (
                    'Initial SP: ' + str(skill_tier['spData']['initSp']))
                sp_dur = (
                    'Duration: '
                    + (
                        str(skill_tier['duration'])
                        if skill_tier['duration'] != -1.0
                        else "-"
                    )
                )

                # Append the skill information to messages
                #
                # Using f-string width formatting, we can get the
                # width of each text to be the same
                messages.append(
                    lvl_string
                    + f"{sp_cost:18}{sp_init:22}{sp_dur}"
                )

                # Retrieve the description from the json
                description = filter_description(
                    skill_tier['description']
                )

                # Unfortunately, the JSON description was meant to
                # work with the web app, so we have to filter it and
                # replace certain attributes with provided values
                properties = re.findall(
                    r" *.*(\{.+\}).* *", description.replace(" ", "\n"))

                for prop in properties:
                    # We get specific details about the regex and group
                    # it.
                    #
                    # From what I can find, each key only has alphabet
                    # letters, numbers, [], _, ., and @.
                    # At the front of the key, there will sometimes be
                    # a '-', which we don't want. After the key,
                    # if there is an ':#%;, we know it's supposed to
                    # be a percentage.
                    prop_re = re.search(
                        r"\{-*([a-zA-Z0-9_.@[\]]+)(:\d+%)*\}",
                        prop
                    )

                    attr = (
                        prop_re
                        .group(1)
                        .strip()
                    )

                    is_percent = prop_re.group(2) is not None

                    # TODO: show other skill tiers?
                    for replacement in skill_tier['blackboard']:
                        if replacement['key'] == attr:
                            # Make the property friendly towards regex
                            prop = (
                                prop.replace("[", r"\[")
                                .replace("]", r"\]")
                            )
                            # Determine whether to represent the
                            # replacement text as percent or not
                            replacement_text = (
                                str(abs(int(replacement['value'] * 100)))+"%"
                                if is_percent
                                else str(abs(int(replacement['value'])))
                            )

                            description = re.sub(
                                prop,
                                replacement_text,
                                description
                            )

                            break  # Oh no a bad break

                messages.append(" " + description)
                if len(tiers_to_check) > 1:
                    messages.append('--------------------\n')
            # Add an empty string in a list to the end for
            # consistent formatting!!!!!!!
            messages += ['']
        else:
            # If, for some reason, you can't find the skill in the
            # skill database, we do this.
            messages.append(
                "Skill " + str(skillnum) + ": "
                + "\nCould not locate this skill in the JSON..."
            )

    return messages


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `scraper.py`.\n\n"
    )
