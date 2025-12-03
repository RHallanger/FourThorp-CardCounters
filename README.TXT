===========================================================

Program Name: FourThorp Card Counting Tool
Author: Team FourThorp
Date: 2025-12-1
Description:
This program is designed to assist blackjack players keep running/true counts of cards
dealt during a game. It supports multiple decks and enables users to input/remove cards
as they are played. The tool calculates and displays the current running count and true count.

Dependencies:
- Python 3.13
- tkinter
- functools

Usage:
Ensure all dependencies with Python3.13 or newer are installed before execution of 4Thorp_Trainer.exe.

Users will be given a GUI interface.

The user is expected to select the mode (add/remove), select the hand that contains the cards wished to be added, and then the card rank itself.
The program will then update the running and true counts accordingly and provide a suggestion for the next best action.
The user can select the number of decks in the shoe at the bottom in a drop-down list.
The user can reset their hand, but maintain the seen cards of the shoe by selecting "Next Hand".
The user can also reset the entire shoe by selecting "New Shoe".

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
This tool can not guarantee success of every blackjack hand, but is designed to assist players in making more informed decisions.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Future Improvements:
- Implement a more advanced strategy suggestion system based on card counting or additional strategies.
- Implement an image analyzer to automatically detect cards from photographs of each hand to automate the card input process.
- Implement statistic tools for additional games.

Members:

Robert Hallanger - Project Manager
- Lead the project, coordinated team efforts, and ensured timely delivery of milestones.
- Oversaw the overall design and functionality of the application.
- Suggested improvements and future features for the tool.
- Created and maintained project documentation and logo.

Ryan Vrbeta - Developer
- Architected and built the final production GUI using the Tkinter framework.
- Developed the core logic modules: `HiLoCounter.py` (Math/State) and `StrategyGuide.py` (Rules engine).
- Implemented the Event-Driven State Machine to handle game flow (Counting vs. Hand Assignment).
- Integrated the Strategy Engine to provide real-time decision feedback based on user input.

Matthew Fuentes - Developer
- Built the Iamge Capture program (no longer used)
- Checked for flow of code and readability within program
- Provided feedback and input on any changes that needed to be made

Kelton Jasper - Tester
  - Tested the code for any bugs.
  - Checked for user friendliness in the GUI.
  - provided imput for any changes that needed to be made.

===========================================================
