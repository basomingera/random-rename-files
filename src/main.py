#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

DEBUG = False


# give random names and save original names to a file
def rename(this_directory, this_format):
    print("Renaming files in directory: ", this_directory, " with format: ", this_format)


# remove given random names
def undo_rename(this_directory, this_format):
    print("Un-renaming files in directory: ", this_directory, " with format: ", this_format)


# give file mixed names
def mix_naming(this_directory, this_format):
    print("Mix-renaming files in directory: ", this_directory, " with format: ", this_format)


def check_flag(the_flag):
    size = len(the_flag)

    if size < 0:
        if DEBUG:
            print("length of flags is:", size)
        return 'ERROR'
    elif the_flag[0] == '-' and size > 1:
        if DEBUG:
            print("the flag:", the_flag, " is for format and action")
        return 'fa'  # format and action
    else:
        if DEBUG:
            print("the flag:", the_flag, " is for location")
        return 'dir'


if __name__ == '__main__':
    # r:rename | u:undo-renaming | m:mix-naming
    possible_action = {'r', 'u', 'm'}
    # n: numbers | a:alphanumeric | l:letters
    possible_format = {'n', 'a', 'l'}

    directory = '.'
    action = 'r'
    rand_format = 'a'

    flags = sys.argv[1:]
    flags_size = len(flags)
    if DEBUG:
        print("The provided flags are: ", flags, " with size: ", flags_size)

    if flags_size == 0:
        pass
    elif flags_size <= 2:
        for each_flag in flags:
            if DEBUG:
                print("Checking for flag: ", each_flag)
            if check_flag(each_flag) == 'dir':
                directory = each_flag
            elif check_flag(each_flag) == 'fa':
                for char in each_flag[1:]:
                    if char in possible_action:
                        action = char
                    elif char in possible_format:
                        rand_format = char
                    else:
                        action = 'x'
            else:
                action = 'x'
    else:
        print("Wrong flags given")
        exit(2)

    # check the action to be accomplished
    if action == 'r':
        rename(directory, rand_format)

    elif action == 'u':
        undo_rename(directory, rand_format)
    elif action == 'm':
        mix_naming(directory, rand_format)
    else:
        print("ERROR: wrong flags")
        exit(1)

exit(0)
