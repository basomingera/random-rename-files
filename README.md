# random-rename-files
This Python3 script gives random names to files within a folder and creates a text file to keep track of previous names.
Imagine having a music car player without random play option .... one way to deal with it is to give the files random names every time they are being put on a USB stick.
# DESCRIPTION
The intentinon for this project is to make a command-line program to rename files with random names fo different formats. It will require the Python interpreter version 3.2+ and it will not be platform specific.

    python3 main.py [directory] [-options] 
    e.g: python3 main.py ../ -ra (rename files in upper directory with alphanumeric random names)
# OPTIONS
Options are in 2 types: actions and formats

> Actions (default: r)

    r: rename the files in the given directory
    u: undo random renaming of files in the given directory. This requires the presence of a files that kept the changes from original file names
    m: mix random names with the origina mames
    
> Formats (default a)

    n: give numeric random names
    a: give alphanumeric random names
    l: give only random names with letters ( no number)
