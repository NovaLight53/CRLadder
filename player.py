#import pandas as pd
import random

class Player():
    """Class to model a Clash Royale Player
    Attributes: 
        id: Identification number
        trophies: Represents the number of trophies the object has
        wins: Number of wins in the duration of the simulation
        losses: Number fo losses in the duration of the simulation
        kt: King tower
        cardLevel: Represents the card level
        skill: Optional parameter that represents the skill, as skill affects who wins the match
    Methods:
        - play match
        - wins match


    """
    def __init__(self, id= 0, trophies = 5000, wins = 0, losses = 0, kingLevel = 11, cardLevel = 88, totalLvlDiff =0, skill = None):
        """Constructor, initializes instance variables
        id: Identification number
        trophies: Represents the number of trophies the object has
        wins: Number of wins in the duration of the simulation
        losses: Number fo losses in the duration of the simulation
        kt: King tower
        cardLevel: Represents the card level
        skill: Optional parameter that represents the skill, as skill affects who wins the match
        """
        self.id = id
        self.trophies = trophies
        self.wins = wins
        self.losses = losses
        self.kt = kingLevel
        self.cardLevel = cardLevel
        self.totalLvlDiff = totalLvlDiff
        self.skill = skill

    def __repr__(self):
        """String representation"""
        s = ''
        return str([self.id, self.trophies, self.wins, self.losses, self.kt, self.cardLevel, self.totalLvlDiff, self.skill])
        # s += f"Trophies: {self.trophies} \n"
        # s += f"wins: {self.wins} \n"
        # s += f"Losses: {self.losses} \n"
        # s += f"King Level: {self.kt} \n"
        # s += f"Card Level: {self.cardLevel} \n"
        # s += f"Skill: {self.skill} \n"
        #return s

    #other methods

    def __lt__(self, opponent):
        return self.trophies < opponent.trophies

    def __eq__(self, other):
        return self.id == other.id

    def matchAllowed(self, opponent) -> bool:
        return abs(self.trophies -opponent.trophies) <= 40 # generally matches tend to be within 40 trophies
    
    def playMatch(self, opponent):
        """Plays a match between players. 
        Updates the attributes on both the player(self) and opponent attributes.
        Params: oppoent - another player object"""
        selfLevels = self.cardLevel + self.kt
        oppLevels = opponent.cardLevel + opponent.kt
        lvlDiff = abs(oppLevels - selfLevels)
        self.totalLvlDiff += lvlDiff
        opponent.totalLvlDiff += lvlDiff
        if oppLevels > selfLevels:
            if random.random() < chanceOfOverlvl(oppLevels - selfLevels):
                opponent.winsMatch(self)
            else:
                self.winsMatch(opponent)
        elif selfLevels > oppLevels:
            if random.random() < chanceOfOverlvl(selfLevels - oppLevels):
                self.winsMatch(opponent)
            else:
                opponent.winsMatch(self)
        else: #equal levels, 50% chance of winning. 
            if random.random() > 0.5:
                self.winsMatch(opponent)
            else:
               opponent.winsMatch(self)

    def winsMatch(self, opponent):
        """Updates the self and opponent objects when self player wins
        Params: Opponent: A Player object. Represents the player that lost the match
        No return"""
        self.wins +=1
        exchanged = 30 + int((1/12) *(opponent.trophies - self.trophies))
        self.trophies += exchanged
        opponent.losses += 1
        lossPct = lossPercent(opponent.trophies)
        opponent.trophies += -1*int(lossPct * exchanged)
        if opponent.trophies < 5000:
            opponent.trophies = 5000

    def getData(self, skill = False):
        """Returns the data in a list form"""
        if not skill:
            return [self.id, self.trophies, self.wins, self.losses, self.kt, self.cardLevel, self.totalLvlDiff]
        else:
            return [self.id, self.trophies, self.wins, self.losses, self.kt, self.cardLevel, self.totalLvlDiff, self.skill]
            
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
    """Calculates the percent of trophies lost depending on the starting trophies
    Used to tweak inflation"""
    if 4000 <= trophies < 5000:
        return 1
    elif 5000 <= trophies < 5600:
        return 0.7
    elif 5600 <= trophies < 6300:
        return 0.8
    elif 6300 <= trophies < 7000:
        return 0.9
    else: 
        return 1
def createPlayer(kingLvl, id= 0,trophies = 5000, wins = 0, losses = 0, skill = None):
    """Creates a player with a specified king tower"""
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
    """Returns the chance of the over leveled player winning if the level difference is "lvlDiff"
    Experimentally determined from 90k battles"""
    return 0.0186*lvlDiff + 0.521 