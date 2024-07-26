# Pyzzle v1.0.0

A python programming puzzle game for teaching beginner programmers about python, especially those who have not programmed before.

## Instructions

Load a `.pyzzle` file using the file dialog in the upper left of the window. Puzzle pieces will be shown on the screen, and instructions will be shown in the upper right corner.
The instructions tell you what the program you are writing should do, and it is your job to arrange the puzzle pieces such that the resulting program has the expected output.

Click and drag the pieces until they are in the desired positions, the ones colored green will be considered your solution. 
Then click "Run!" under the Input box on the right. 
The Input box will be filled with the program you arranged the puzzle pieces into, and the Output box will show what the assembled program printed. 
If the program uses the `input()` function to get user input, a pop-up window will show up instead, allowing input entry.
Note that not all pieces are required to be part of the solution!

## Making puzzles

The `.pyzzle` file format is very simple. In essence, it's a UTF-8 encoded text file with two sections: the Instruction section and the Code section.

The Instruction section is delimited by "PYZZLE_INSTRUCTIONS_START" and "PYZZLE_INSTRUCTIONS_END". Between these strings are the instructions for the puzzle in plain text.
Pyzzle currently does no processing of this text, so make sure it's not too wide, otherwise the rest of the program GUI might be hidden away if it doesn't fit.

The Code section is delimited by "PYZZLE_CODE_START" and "PYZZLE_CODE_END". Between these strings are lines of python code, including indentation, that is to be converted to puzzle pieces.
Empty lines will be ignored when creating the puzzle pieces, but comments will be included.

The pieces start in random positions, so it is viable to input the whole python program without shuffling it, 
unless you are afraid students will read the file before trying to solve the puzzle. (But if they can do that, their skill is probably beyond what this exercise can give them.)

### File skeleton
```py
PYZZLE_INSTRUCTIONS_START
Write a program that prints Hello World
PYZZLE_INSTRUCTIONS_END
PYZZLE_CODE_START
print("Hello World")
PYZZLE_CODE_END
```

## Installation

The program is written in Python 3 and is tested on Python version 3.10.5 and 3.8.10, but may work on versions as early as 3.7.
It has no dependencies outside the Python standard library.

Download it using `git` or as a zip file from this GitHub page.
If you intend to make your own puzzles, you only need the `pyzzle.py` file, though a few example puzzles (Swedish language) are included in the `assets` folder.

Run the program using Python:
- Windows:
```ps
python pyzzle.py
```
- Linux/Mac (not tested): 
```bash
python3 pyzzle.py
```