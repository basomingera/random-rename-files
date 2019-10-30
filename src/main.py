#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from os.path import exists, isfile
from os import listdir, rename
import hashlib
import random
import string
import math
import json


DEBUG = False
ORIGINAL_NAMES = ".original_names.json"
MIN_NAME_SIZE = 4


# generate random names
def random_names(total_names, name_size, random_formats):
    """Generate a random string of fixed length """
    letters = string. ascii_letters
    numbers = string.digits

    generated_random_names = set()

    while len(generated_random_names) < total_names:
        if random_formats == 'l':
            current_name =  ''.join(random.choice(letters) for i in range(name_size))
        elif random_formats == 'n':
            current_name = ''.join(random.choice(numbers) for i in range(name_size))
        else:
            current_name =  ''.join(random.choice(letters + numbers) for i in range(name_size))

        if current_name not in generated_random_names:
            generated_random_names.add(current_name)

    return generated_random_names


# give random names and save original names to a file
def rename_files(this_directory, this_format):
    print("Renaming files in directory: ", this_directory, " with format: ", this_format)
    list_of_files = listdir(this_directory)
    total_files = len(list_of_files)
    # print(list_of_files)

    if not exists(this_directory+ORIGINAL_NAMES):

        translation_dict = {}
        for file in list_of_files:
            if not isfile(this_directory+file):
                continue
            hash_value = hashlib.sha256(open(this_directory+file,'rb').read()).hexdigest()
            translation_dict[hash_value] = this_directory+file

        json_translation = json.dumps(translation_dict)
        f = open(this_directory+ORIGINAL_NAMES, "w")
        f.write(json_translation)
        f.close()

    new_names = random_names(total_files, max(MIN_NAME_SIZE, math.ceil(math.log(total_files, 10))), this_format)
    # print(list_of_files, new_names)

    for file, newName in zip(list_of_files, new_names):
        if not isfile(this_directory + file) or file == 'main.py' or file == this_directory+ORIGINAL_NAMES:
            continue
        else:
            extension = file.split('.')[-1] if '.' in file else ''
            rename(r''+this_directory+file, r''+this_directory+newName+'.'+extension)

    # print(list_of_files)


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

    directory = './'
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
                if not exists(directory) or isfile(directory):
                    print("%s" % directory, " is not a valid directory!")
                    exit(3)
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
        rename_files(directory, rand_format)

    elif action == 'u':
        undo_rename(directory, rand_format)
    elif action == 'm':
        mix_naming(directory, rand_format)
    else:
        print("ERROR: wrong flags")
        exit(1)

exit(0)
