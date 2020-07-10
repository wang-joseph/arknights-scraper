import sys

# created 05/07/2020
# last edited: 05/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: This holds any parser/formatter functions that should be
# used by both Aceship JSON parsing and Gamepress parsing


def parse_stats(stats_dict):
    messages = []
    messages.append("\n\nOperator Stats\n")

    if stats_dict == {}:
        return [
            "\n\nOperator Stats\nCould not retrieve stats for some reason!"
        ]

    levels = ["ne", "e1", "e2"]
    formatted_levels = ["E0 max", "E1 max", "E2 max"]
    max_stats = []

    # Fetch the basic stats for each level (if it exists)
    # We check the max atk stat for each, and if it's not a ""
    # then we know that operator has that lvl
    for lvl in range(len(formatted_levels)):
        if "max_atk" + levels[lvl] in stats_dict.keys() \
                and stats_dict["max_atk" + levels[lvl]] != "":
            max_stats += [
                formatted_levels[lvl],
                "Max atk: " +
                str(stats_dict[f"max_atk{levels[lvl]}"]) + " atk",
                "Max def: " +
                str(stats_dict[f"max_def{levels[lvl]}"]) + " def",
                "Max hp : "
                + str(stats_dict[f"max_hp{levels[lvl]}"]) + " hp",
                "Res    : "
                + str(stats_dict[f"{levels[lvl]}_arts"]),
                "Block  : "
                + str(stats_dict[f"{levels[lvl]}_block"]),
                "Cost   : "
                + str(stats_dict[f"{levels[lvl]}_cost"]) + " dp \n"
            ]

    if len(max_stats) == 0:
        # Very minor formatting issue but this is to get rid of
        # the new line inserted by the final formatter
        # by simply adding it to the first element of
        # the list and not a seperate list element
        messages[0] += "No stats found!"

    messages += max_stats

    # Retrieve the attack interval and redeploy time
    # By adding an empty space at the end, we fool the parser
    # into inserting only 1 newline
    messages += [
        "Attack Interval: " + str(stats_dict['atk_int']) + " s"
    ]
    messages += [
        "Deployment Time: " + str(stats_dict['deploy_time']) + " s"
    ] + [""]

    return messages


if __name__ == "__main__":
    sys.stdout.write(
        "Wrong python file to run! The main file to run is `scraper.py`.\n\n"
    )
