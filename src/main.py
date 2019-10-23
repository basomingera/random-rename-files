#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys


def main():
    pass


if __name__ == '__main__':
    
    possible_action = {'r', 'u', 'm'}
    possible_format = {'n', 'a', 'l'}

    flags = len(sys.argv)
    if flags ==1 :
        directory = '.'
        action = 'r'
        format = 'a'
    elif flags == 2:
        directory = '.'
        action = 'r'
        format = 'a'
        print("TODO")
    elif flags == 3:
        directory = '.'
        action = 'r'
        format = 'a'
        print("TODO")
    else:
        print("Print wrong flags were given")
        directory = 'x'
        action = 'x'
        format = 'x'
        #return 2

    # check the action to be accomplished
    if action == 'r':
        pass
    elif action == 'u':
        pass
    elif action == 'm':
        pass
    else:
        print("ERROR: wrong flags")
        #return 1

    print(directory, action, format)
