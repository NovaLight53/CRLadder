# CRLadder
All files used for a Clash Royale Ladder simulation

The files in this repo are either python files or csv files. The CSV files are the raw data from many tests of the functions KTsim, continueSim, trophyCapsim, simulation or finalSimulation. 

The python files are as follows: LadderSim2.py and player.py

LadderSim2 is a file that contains 4 difference CR ladder simulations and multiple helper functions to carry these out, convert between pandas data frames and numpy arrays, along with a function to generate graphs of data. 

player is a file with the Player class, which models a clash royale player with attributes id, trophies, skill, wins, losses, king tower, card levels, skill and percent of games NOT on ladder.  

To run a simulation:

Clone the repo and download the files

Run the player class and the ladderSim file

To use my initial baseline data, type baselineDF = pd.read_csv('baselineData.csv') to import the data as a dataframe, then arr = dfToArr(baselineDF) to convert it into an array. Finally you can input the array into the playerArr argument of any simulation function.  Note that FinalSim does not have any arguments, it simply uses the "best" ladder and runs it on a much larger scale (12 seasons, 4x the players)
