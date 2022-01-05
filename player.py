#import pandas as pd
import random
import math

class Player():
    """
    Class to model a Clash Royale Player
    
    Attributes: 
        id: Identification number
        trophies: Represents the number of trophies the object has
        wins: Number of wins in the duration of the simulation
        losses: Number fo losses in the duration of the simulation
        kt: King tower
        cardLevel: Represents the card level
        skill: Optional parameter that represents the skill, as skill affects who wins the match
        partyPct: Percentage that a player plays 2v2.  Reflected in them not being added to the queue as often
    Methods:
        playMatch
        winsMatch
        matchAllowed
        reset
        getData
    """
    def __init__(self, id= 0, trophies = 5000, wins = 0, losses = 0, kingLevel = 11, cardLevel = 88, totalLvlDiff =0, skill = None, partyPct = 0):
        """Initializes instance variables

        Args: 
            id: Identification number
            trophies: Represents the number of trophies the object has
            wins: Number of wins in the duration of the simulation
            losses: Number fo losses in the duration of the simulation
            kt: King tower
            cardLevel: Represents the card level
            skill: Optional parameter that represents the skill, as skill affects who wins the match
            partyPct: Percentage that a player plays 2v2.  Reflected in them not being added to the queue as often
        """
        self.id = id
        self.trophies = trophies
        self.wins = wins
        self.losses = losses
        self.kt = kingLevel
        self.cardLevel = cardLevel
        self.totalLvlDiff = totalLvlDiff
        self.skill = skill
        self.pp = partyPct

    def __repr__(self):
        """String representation of a player"""
        return str((self.id, self.trophies, self.wins, self.losses, self.kt, self.cardLevel, self.totalLvlDiff, self.pp))
        #s = ''
        #Left this in for a more comprehensive string representation of a player object
        # s += f"Trophies: {self.trophies} \n"
        # s += f"wins: {self.wins} \n"
        # s += f"Losses: {self.losses} \n"
        # s += f"King Level: {self.kt} \n"
        # s += f"Card Level: {self.cardLevel} \n"
        # s += f"Total Lvl Diff: {self.totalLvlDiff}"
        # s += f"Skill: {self.skill} \n"
        #return s


    def __lt__(self, opponent):
        """Determines if a player has less trophies than their opponent."""
        return self.trophies < opponent.trophies

    def __eq__(self, other):
        """Checks if 2 players are the same"""
        return self.id == other.id

    def matchAllowed(self, opponent):
        """Checks if a match is allowed to be played"""
        return abs(self.trophies -opponent.trophies) <= 40 # generally matches tend to be within 40 trophies
    
    def playMatch(self, opponent, gatesList = [5000]):
        """Plays a match between players. 
        Updates the attributes on both the player(self) and opponent attributes.
        
        Args: 
        opponent: another player object
        gatesList: List of trophy gates
        """
        selfLevels = self.cardLevel + self.kt
        oppLevels = opponent.cardLevel + opponent.kt
        lvlDiff = abs(oppLevels - selfLevels)
        self.totalLvlDiff += lvlDiff
        opponent.totalLvlDiff += lvlDiff
        if oppLevels > selfLevels:
            if random.random() < chanceOfOverlvl(oppLevels - selfLevels):
                opponent.winsMatch(self, gatesList = gatesList)
            else:
                self.winsMatch(opponent, gatesList = gatesList)
        elif selfLevels > oppLevels:
            if random.random() < chanceOfOverlvl(selfLevels - oppLevels):
                self.winsMatch(opponent, gatesList = gatesList)
            else:
                opponent.winsMatch(self, gatesList = gatesList)
        else: #equal levels,Skill based
            if opponent.skill > self.skill:
                moreSkilled = opponent
            else:
                moreSkilled = self
            chanceOfBetter = changeOfMoreSkill(abs(opponent.skill-self.skill))
            if random.random() > chanceOfBetter: #less skilled player wins
                if moreSkilled == opponent:
                    self.winsMatch(opponent, gatesList = gatesList)
                else:
                    opponent.winsMatch(self)
            else: #more skilled player wins
                if moreSkilled == opponent:
                    opponent.winsMatch(self, gatesList = gatesList)
                else:
                    self.winsMatch(opponent, gatesList = gatesList)

    def winsMatch(self, opponent, gatesList = [5000]):
        """Updates the player and opponent objects when the player wins

        Args:
        Opponent: Player object. Represents the player that lost the match
        gatesList: List of integers representing trophy gates. Used for tweaking trophy gates
        No return"""
        self.wins +=1
        exchanged = 30 + int((1/12) *(opponent.trophies - self.trophies))
        self.trophies += exchanged
        opponent.losses += 1
        original = opponent.trophies
        lossPct = lossPercent(opponent.trophies)
        #lossPct = lossPercent(opponent.trophies, self, opponent)
        opponent.trophies += -1*int(lossPct * exchanged)

        for gate in gatesList:
            if opponent.trophies < gate <= original:
                opponent.trophies = gate
                break

    def getData(self, skill = False):
        """Gets the player's data and returns it as a list."""
        if not skill:
            return [self.id, self.trophies, self.wins, self.losses, self.kt, self.cardLevel, self.totalLvlDiff]
        else:
            return [self.id, self.trophies, self.wins, self.losses, self.kt, self.cardLevel, self.totalLvlDiff, self.skill, self.pp]
            
    def reset(self):
        """Resets the player object's trophies. """
        if self.trophies >= 7000:
            self.trophies = min((6600, int(self.trophies - 0.3*(self.trophies-5000))))
        elif 6000 <= self.trophies< 7000:
            self.trophies = int(self.trophies - 0.4*(self.trophies - 5000))
        elif 5000 <= self.trophies < 6000:
            self.trophies = int(self.trophies - 0.5*(self.trophies - 5000))
        else:
            pass

#Non class methods:

def lossPercent(trophies):
    """Calculates the percent of trophies lost at given trophy range."""
    # p1Lvl = p1.kt + p1.cardLevel #p1 is winner
    # p2Lvl = p2.kt + p2.cardLevel
    # lvlDiff = abs(p1Lvl - p2Lvl)
    # if p2Lvl > p1Lvl:
    #     return 1
    # else:
    #     return 1 - 0.033*lvlDiff
    if 4000 <= trophies < 5000:
        return 1
    elif 5000 <= trophies < 5300:
        return 0.8
    elif 5300 <= trophies < 6000:
        return 0.9
    else: 
        return 1
def createPlayer(kingLvl, id= 0,trophies = 5000, wins = 0, losses = 0, skill = None, partyPct = 0):
    """Creates a player with a specified king tower."""
    if kingLvl == 8:
        cardLevel = random.choice(range(60, 81))
    elif kingLvl == 9:
        cardLevel= random.choice(range(68, 89))
    elif kingLvl == 10:
        cardLevel= random.choice(range(76, 105))
    elif kingLvl == 11:
        cardLevel= random.choice(range(84, 113))
    elif kingLvl == 12:
        cardLevel= random.choice(range(92, 113))
    elif kingLvl == 13:
        cardLevel= random.choice(range(96, 113))
    elif kingLvl == 14:
        cardLevel= random.choice(range(104, 113))
    else:
        raise ValueError("Invalid King Tower")
    return Player(id = id, trophies = trophies, wins = wins, losses = losses, kingLevel=kingLvl, cardLevel=cardLevel, skill = skill )
    

def chanceOfOverlvl(lvlDiff):
    """Returns the chance of the over leveled player winning if the level difference is "lvlDiff"."""
    return 0.0186*lvlDiff + 0.521 

def changeOfMoreSkill(skillDiff):
    return 0.5 + skillDiff/2.5


def createRealPlayers(kingLvl, id= 0,trophies = 5000, wins = 0, losses = 0, skill = None, pp = 0):
    """Creates player with more "real" card levels.  """
    if kingLvl == 8:
        cardLevel = int(random.gauss(70, 3.5))
    elif kingLvl == 9:
        cardLevel= int(random.gauss(78, 3))
    elif kingLvl == 10:
        cardLevel= int(random.gauss(90, 5)) #Gaussian is most likely
    elif kingLvl == 11:
        cardLevel= int(min(random.gauss(98, 9),112)) #max possible lvls is 112
    elif kingLvl == 12:
        cardLevel= int(min(random.gauss(102, 7),112))
    elif kingLvl == 13:
        cardLevel= int(min(random.gauss(104, 5),112))
    elif kingLvl == 14:
        cardLevel= int(min(random.gauss(108, 3),112))
    else:
        raise ValueError("Invalid King Tower")
    return Player(id = id, trophies = trophies, wins = wins, losses = losses, kingLevel=kingLvl, cardLevel=cardLevel, skill = skill, partyPct= pp )