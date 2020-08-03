"""This module controls everything to do with storing, editing,
displaying, and destroying shortcuts (or aliases) to tags."""

import sys
import argparse
from typing import Tuple, List

from halo import Halo  # extremely important

from inputfuncs.input_reader import (
    read_lines_into_dict
)

# created 31/06/2020
# last edited: 31/07/2020
# version: 1.0.0
# author: Joseph Wang (EmeraldEntities)
# description: an editor containing functions for manipulating
#             tag shortcuts


def create_tag_shortcut(args: argparse.Namespace) -> None:
    """Creates a new shortcut for a tag for later use.

    If the shortcut already exists in the shortcut list, overwrite
    the old shortcut with the new tag. If this happens, the overwriting
    process time is proportional to the size of the shortcut list,
    as the function will overwrite and rewrite the entire list.

    Prints directly to the screen. If the tag specified was
    not found, return early. Returns nothing.
    """
    spinner = Halo(text="Adding...", spinner="dots", color="red")
    spinner.start()

    # Load the dicts needed to accomplish this task
    shortcut_dict = read_lines_into_dict(
        "./info/recruitops/tagShortcuts.txt"
    )
    translation_dict = read_lines_into_dict(
        "./info/recruitops/tagConversions.txt"
    )

    # Make sure the tag specified actually exists and that the
    # shortcut name doesn't already exist in the translation dict.
    if args.tag in translation_dict.keys():
        tag_name = translation_dict[args.tag]
    else:
        spinner.fail("Failed.")
        sys.stdout.write(
            f"\n\nCould not find the tag '{args.tag}'!\n\n"
        )
        return

    if args.shortcut in translation_dict.keys():
        spinner.fail("Failed.")
        sys.stdout.write(
            f"\n\nShortcut '{args.shortcut}' cannot be changed!\n\n"
        )
        return

    # Actually create the shortcut to a tag
    if args.shortcut not in shortcut_dict.keys():
        with open(
            "./info/recruitops/tagShortcuts.txt",
            "a",
            encoding="utf8"
        ) as f:
            f.write(args.shortcut + " " + tag_name + "\n")

    else:
        # If the shortcut exists, we'll have to override the tag
        # and it.
        key_list, val_list = zip(*shortcut_dict.items())

        line_num = key_list.index(args.shortcut)
        index = 0

        with open(
            "./info/recruitops/tagShortcuts.txt",
            "w",
            encoding="utf8"
        ) as f:
            while index < len(key_list):
                if index == line_num:
                    # override the old value with new one
                    f.write(args.shortcut + " " + tag_name + "\n")
                else:
                    # preserve the old values as they're unrelated
                    f.write(key_list[index] + " " + val_list[index] + "\n")

                index += 1

    # Write success message
    spinner.succeed("Success!")
    sys.stdout.write(  # this is just to keep it under line limit
        "\n\nSuccessfully added shortcut '"
        + args.shortcut
        + "' for tag '"
        + args.tag
        + "'!\n\n"
    )


def list_tag_shortcuts(args: argparse.Namespace) -> None:
    """Retrieves the shortcut-tag information and formats it in a
    specified way.

    Returns nothing as it prints out directly to the display.

    Formats based on whether `args.reverse` is True or not
    by calling a separate function that will independantly fetch
    the proper information in the formatted and correct way.
    (ie. either (tags -> shortcuts) or (shortcuts -> tags)).
    """

    spinner = Halo(text="Searching...", spinner="dots", color="blue")
    spinner.start()

    # Call the appropriate function to get the appropriate info
    if args.reverse:
        succeeded, messages = list_reversed_tag_shortcuts(args)
    else:
        succeeded, messages = list_proper_tag_shortcuts(args)

    # Succeeded flag lets us know whether to fail the spinner or not
    # in an easier to understand and less scuffed way.
    # TODO: this seems scuffed but slightly less so
    if succeeded:
        spinner.succeed("Success!")
    else:
        spinner.fail("Failed.")

    # Write all the stored messages
    # spinner.succeed("Success!")
    for message in messages:
        sys.stdout.write(message + "\n")

    sys.stdout.write("\n")  # padding for formatting


def list_reversed_tag_shortcuts(
        args: argparse.Namespace
) -> Tuple[bool, List[str]]:
    """Retrieves either all tags and their shortcuts or a specified
    tag and its shortcut, formats them, and then prints to the screen.
    Returns nothing.

    Returns a tuple containing a boolean at the first index to show
    whether this function failed or succeeded, and a list of messages
    at the second index.

    The user is able to input a shortcut to a tag as a reference to
    that tag. However, as a result of implementation, this function
    will take more time the more shortcuts there are.

    If the shortcut to the tag is built-in, a star will be put next
    to it indicating that this tag cannot be removed or overwritten.
    """
    messages = ["\n\nTag Shortcuts\n"]

    # Load dictionaries, this time in reverse
    #
    # We avoid combining because the values are lists, and I don't
    # feel like combining them right now
    # TODO: these dict calls can probably be optimized
    rev_shortcut_dict = read_lines_into_dict(
        "./info/recruitops/tagShortcuts.txt",
        reverse=True,
        overwrite=False
    )
    rev_conversion_dict = read_lines_into_dict(
        "./info/recruitops/tagConversions.txt",
        reverse=True,
        overwrite=False
    )
    # to see what tag the user inputted
    # this could take some time depending on the amount of shortcuts
    # though... but I think it's better this way for sake of efficiency
    conversion_dict = {
        **read_lines_into_dict(
            "./info/recruitops/tagConversions.txt",
        ),
        **read_lines_into_dict(
            "./info/recruitops/tagShortcuts.txt",
        )
    }

    rev_translation_dict = read_lines_into_dict(
        "./info/recruitops/formattedTagConversions.txt",
        reverse=True
    )

    # Add stars after the important shortcuts that can't be
    # deleted or overwritten.
    for key in rev_conversion_dict:
        rev_conversion_dict[key] = (
            list(map(
                lambda sc: sc + " *",
                rev_conversion_dict[key]
            ))
        )

    # Get all tag-shortcut connections if needed
    if args.mode == "all":
        for key in rev_translation_dict:
            # It may seem redundant to go from tag to key and then key to
            # tag, but this formats the tag and also has an efficiency
            # of O(1), so it's fine.
            #
            # We know that every tag has at least one builtin shortcut,
            # so no need to check if there is a shortcut for a tag.
            #
            # We're also doing some checks here to make sure that
            # everything is properly formatted if there's only one
            # tag for it, and that commas are in a correct place,
            # and that shortcuts exist for that tag, and that
            # shortcuts are formatted well...
            messages.append(
                f"{rev_translation_dict[key]}\n"
                + (
                    ",\n".join(rev_conversion_dict[key])
                    if key not in rev_shortcut_dict.keys()
                    else (
                        ",\n".join(
                            rev_conversion_dict[key]
                            + rev_shortcut_dict[key]
                        )
                    )
                )
                + "\n"
            )
    # Get specified tags
    else:
        # Make sure there are shortcuts
        if len(args.shortcut) == 0:
            return (False, ["\n\nNo shortcuts provided."])

        # Make sure that the tag actually exists
        for tag in args.shortcut:
            if tag.lower() not in conversion_dict.keys():
                return (False, [f"\n\nCould not find tag '{tag}'."])

        # Get the actual tags-shorcut connections requested
        for tag in args.shortcut:
            # It may seem redundant to go from tag to key and then key
            # to tag, but this formats the tag and also has an
            # efficiency of O(1), so it's fine.
            key = conversion_dict[tag]

            messages.append(
                f"{rev_translation_dict[key]}\n"
                + (
                    ",\n".join(rev_conversion_dict[key])
                    if key not in rev_shortcut_dict.keys()
                    else (
                        ",\n".join(
                            rev_conversion_dict[key]
                            + rev_shortcut_dict[key]
                        )
                    )
                )
                + "\n"
            )

    # Get rid of the \n that is always present at the last element
    # for consistant formatting
    messages[-1] = messages[-1].rstrip()

    return (True, messages)


def list_proper_tag_shortcuts(
        args: argparse.Namespace
) -> Tuple[bool, List[str]]:
    """Retrieves all shortcuts and their associated tag, or the
    specified shortcut(s) and their associated tag, depending on
    arguments.

    Returns a tuple containing a boolean at the first index to show
    whether this function failed or succeeded, and a list of messages
    at the second index.

    This will not list built-in shortcuts. You can find those by
    using the 'reverse' flag to see what tags can be called using
    what shortcuts.
    """
    messages = []
    # Get all tag conversions
    shortcut_dict = {
        **read_lines_into_dict(
            "./info/recruitops/tagShortcuts.txt",
        )
    }

    # To translate from zh tag to eng tag
    rev_translation_dict = read_lines_into_dict(
        "./info/recruitops/formattedTagConversions.txt",
        reverse=True
    )

    messages = ["\n\nShortcuts\n"]

    # If specified, find all the shortcuts
    if args.mode == "all":
        if len(shortcut_dict.items()) == 0:
            return (False, ["\n\nNo shortcuts found!"])
        else:
            for key, value in shortcut_dict.items():
                messages.append(
                    f"{key:20}---> {rev_translation_dict[value]}"
                )
    else:
        if len(args.shortcut) == 0:
            return (False, ["\n\nNo shortcuts provided."])

        # Make sure the tag exists
        for shortcut in args.shortcut:
            if shortcut not in shortcut_dict.keys():
                return (
                    False,
                    [f"\n\nCould not find shortcut '{shortcut}'."]
                )

        # Format the specific shortcuts
        for shortcut in args.shortcut:
            messages.append(
                f"{shortcut:20} ---> "
                + f"{rev_translation_dict[shortcut_dict[shortcut]]}"
            )

    return (True, messages)


def delete_tag_shortcut(args: argparse.Namespace) -> None:
    """Either deletes a shortcut (or shortcuts) from the list of
    shortcuts, or deletes all the shortcuts from the list of shortcuts.

    Returns nothing as this function will print directly to the screen.
    """
    spinner = Halo(text="Deleting...", spinner="dots", color="red")
    spinner.start()
    # Load dicts
    shortcut_dict = read_lines_into_dict(
        "./info/recruitops/tagShortcuts.txt"
    )

    # Make sure the shortcuts exist if they are included
    if args.mode == "select":
        if len(args.shortcut) == 0:
            spinner.fail("Failed.")
            sys.stdout.write(
                f"\n\nNo shortcuts were provided!\n\n"
            )
            return

        for shortcut in args.shortcut:
            if shortcut not in shortcut_dict.keys():
                spinner.fail("Failed.")
                sys.stdout.write(
                    f"\n\nCould not find the shortcut '{shortcut}'!\n\n"
                )
                return

    # Only one file IO needed (disregarding the read_lines_into_dict)
    # Actually remove tags
    with open(
        "./info/recruitops/tagShortcuts.txt",
        "w",
        encoding="utf8"
    ) as f:
        # If you open a file as w and do nothing, it simply clears
        # everything in the file. We'll simply check if args.all
        # was specified, and if it is, do nothing.
        #
        # Otherwise, actually loop through the dict and don't delete
        # everything.
        if args.mode == "select":
            for key, value in shortcut_dict.items():
                # Skip any tag that matches the shortcut, basically
                # deleting it.
                if key in args.shortcut:
                    continue  # oh no a bad continue

                f.write(key + " " + value + "\n")

    # Write success message
    spinner.succeed("Success!")
    if args.mode == "all":
        sys.stdout.write(
            "\n\nSuccessfully deleted all tags!\n\n"
        )
    else:
        sys.stdout.write(  # this is just to keep it under line limit
            "\n\nSuccessfully deleted "
            + ", ".join(args.shortcut)
            + "!\n\n"
        )
