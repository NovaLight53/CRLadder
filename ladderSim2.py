import random
import player as pl
import pandas as pd
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import seaborn as sns

#Global variables
COLS = ["ID", "Trophies", "Wins","Losses", "King Tower", "Card Level","Total Level Difference", "LvlDiff/Match"]
PALETTE = sns.color_palette("mako_r", as_cmap=True)


def createArray(numPlayers, trophies):
    """Creates an array of player objects
    
    Args:
    numPlayers: Integer, number of player objects to be created
    trophies: the starting number of trophies
    """
    playerList = [pl.createPlayer(random.choice(range(8,15)), id = i, trophies= trophies) for  i in range(numPlayers)]
    return np.asarray(playerList)

def simulate(numPlayers, initialTrophies, numMatches, gatesList = [5000]):
    """Simulates the CR ladder with numPlayers players starting at initialTrophies
    Used to set a baseline for uniform distribution of players across KTs
    plays numMatches matches
    Args:  numPlayers - int, number of players in the ladder
    initialTrophies - int, initial starting numbr of trophies
    numMatches - int, Number of matches to play
    """
    playerArr = createArray(numPlayers, initialTrophies)
    queue = np.asarray([random.choice(playerArr)], dtype = object)
    matchesPlayed = 0
    maxQueueSize = 0
    while matchesPlayed < numMatches:
        if matchesPlayed %(numMatches//10) == 0:
            print(matchesPlayed)
        if queue.size> maxQueueSize:
            maxQueueSize = queue.size
        if queue.size == 0:
            queue = np.append(queue, random.choice(playerArr))
            pass
        else:
            newPlayer = random.choice(playerArr)
            addPos = np.searchsorted(queue, newPlayer)
            if newPlayer in queue:
                pass #can't play against themself
            else:
                addPos = np.searchsorted(queue, newPlayer)
                try:
                    opponent = queue[addPos]
                except IndexError as error:
                    queue = np.insert(queue, addPos, newPlayer)
                    pass
                if opponent.matchAllowed(newPlayer):
                    newPlayer.playMatch(opponent, gatesList = gatesList)
                    matchesPlayed += 1
                    queue = np.delete(queue, addPos)
                else:
                    queue = np.insert(queue, addPos, newPlayer)
    playerArr.sort()
    print(f"Max queue size: {maxQueueSize}")
    return playerArr

def continueSim(playerArr, numMatches, mode = None, cardLvlRule = 0, KTdiff = 0, KTcutoff = 5000, gatesList = [5000]):
    """Continues a simulation for numMatches more games, Very slow if using mode isn't none
    Args: 
    playerArr: Array of player objects.  
    numMatches: Number of matches to be played
    mode: The type of matchmaking to use.  Either 'KT', 'CL', 'KTCL'
    cardLvlRule: Int, the maximum difference in card levels allowed in a match
    KTdiff: The maximum difference in king tower between both players
    KTcutoff: The maximum trophies where the KT diff rule applies. """
    queue = np.asarray([random.choice(playerArr)], dtype = object)
    matchesPlayed = 0
    maxQueueSize = 0
    numMatches += 10 #off sets the matches played counter
    while matchesPlayed < numMatches:

        if matchesPlayed %(numMatches//10) == 0:
            print(matchesPlayed)
            matchesPlayed += 1 #just to prevent spam
        if queue.size == 0:
            queue = np.append(queue, random.choice(playerArr))
            pass
        if queue.size> maxQueueSize:
            maxQueueSize = queue.size
            
        else:
            newPlayer = random.choice(playerArr)
            addPos = np.searchsorted(queue, newPlayer)
            if newPlayer in queue:
                pass #can't play against themself
            else:
                addPos = np.searchsorted(queue, newPlayer)
                try:
                    opponent = queue[addPos]
                except IndexError as error: #always occurs at the end of the list. 
                    queue = np.insert(queue, addPos, newPlayer)
                    pass 
                try: 
                    if allowMatch(newPlayer, opponent, mode = mode, cardLvlRule = cardLvlRule, KTdiff = KTdiff, KTcutoff = KTcutoff):
                            newPlayer.playMatch(opponent, gatesList = gatesList)
                            matchesPlayed += 1
                            queue = np.delete(queue, addPos)
                    else:
                             queue = np.insert(queue, addPos, newPlayer)  
                except UnboundLocalError as error:
                    print("Error")
    playerArr.sort()
    return playerArr

def KTsim(playerArr, numMatches, KTdiff = 1, KTcutoff = 6000, gatesList = [5000]):
    """Simulates a king tower matchmaking system, but uses separate queues to optimize performance
    Args: 
    playerArr: Array of player objects, sorted by trophies
    numMatches: number of matches to be played
    KTdiff: The difference in king tower between 2 players matched against each other
    KTcutoff:  The point where king tower matchmaking ends"""
    queueDict = {}
    for kt in range(8, 15):
        queueDict[str(kt)] = np.asarray([]) #separated queue for players under cutoff (MUCH FASTER)
    if max(playerArr).trophies >= KTcutoff:
        generalQueue = np.asarray([max(playerArr)]) #general queue for players over the cutoff
    else:
        generalQueue = np.asarray([])
    matchesPlayed = 0
    while matchesPlayed < numMatches:
        if matchesPlayed %(numMatches//10) == 0:
            print(matchesPlayed)
        newPlayer = random.choice(playerArr)
        if newPlayer.trophies > KTcutoff:
            addPos= np.searchsorted(generalQueue, newPlayer)
            if addPos == generalQueue.size:
                addPos = addPos - 1
            opponent = generalQueue[addPos]
            try: 
                if allowMatch(newPlayer,opponent,mode='KT',KTdiff=KTdiff,KTcutoff=KTcutoff):
                    newPlayer.playMatch(opponent, gatesList = gatesList)
                    matchesPlayed += 1
                    generalQueue = np.delete(generalQueue, addPos)
                else:
                    generalQueue = np.insert(generalQueue, addPos, newPlayer)  
            except UnboundLocalError as error:
                print("Error")
        else: #need to use KT queues
            opponent = findOpponent(queueDict, newPlayer, KTdiff, KTcutoff)
            if opponent == newPlayer: #there is no opponents, add to proper queue
                queueDict = addToQueue(queueDict, newPlayer)
            else:
                newPlayer.playMatch(opponent,gatesList = gatesList)
                matchesPlayed += 1
                queueDict = remFromQueue(queueDict, opponent)
    playerArr.sort()
    return playerArr

def trophyCapSim(playerArr, numMatches, capList):
    """Simulates the ladder when all matches are capped by the trophy range at which the match occurs. No King Tower, No Card Level mm"""
    queue = np.asarray([random.choice(playerArr)], dtype = object)
    matchesPlayed = 0
    while matchesPlayed < numMatches:
        if matchesPlayed %(numMatches//10) == 0:
            print(matchesPlayed)
        if queue.size == 0:
            queue = np.append(queue, random.choice(playerArr))
            pass
        else:
            newPlayer = random.choice(playerArr)
            addPos = np.searchsorted(queue, newPlayer)
            if newPlayer in queue:
                pass #can't play against themself
            else:
                addPos = np.searchsorted(queue, newPlayer)
                if addPos == queue.size:
                    addPos += -1
                    opponent = queue[addPos]
                else:
                    opponent = queue[addPos]
                if allowMatch(newPlayer, opponent):
                    originalLevels = [newPlayer.cardLevel, opponent.cardLevel]
                    cap = (8 + np.searchsorted(capList, min(newPlayer.trophies, opponent.trophies)))*8
                    newPlayer.cardLevel = min(newPlayer.cardLevel, cap)
                    opponent.cardLevel = min(opponent.cardLevel, cap)
                    newPlayer.playMatch(opponent)
                    matchesPlayed += 1
                    queue = np.delete(queue, addPos)
                    newPlayer.cardLevel = originalLevels[0]
                    opponent.cardLevel = originalLevels[1]
                else:
                    queue = np.insert(queue, addPos, newPlayer)
    playerArr.sort()
    return playerArr


def capByTrophies(playerArr, caps):
    """Caps a player's card level with their trophies
    Caps are based off of the max avg card lvl: 72, 80, 88, 96, 104, 112. Below first, capped at 64
    Args:
    playerArr- array of player objects
    caps: List of 6 items representing the trophy locations where card lvls are capped at. 

    Returns:list of original card levels
    """
    originalLvls = [p.cardLevel for p in playerArr]
    for pla in playerArr:
        cap = (8 + np.searchsorted(caps, pla.trophies))*8
        pla.cardLevel = min(pla.cardLevel, cap)
    return originalLvls



def capByKt(data):
    """Returns a player object array with all players card level capped at their king tower
    Args: data- Player object array"""
    for p in data:
        if p.cardLevel > 8*p.kt: #cap by King tower
            p.cardLevel = 8*p.kt
    return data

def addToQueue(qDict,player):
    """adds the player to the correct queue in the qDict"""
    key = str(int(player.kt))
    q = qDict[key]
    if q.size == 0:
        qDict[key] = np.append(q, player)
    elif player not in q:
            addPos = np.searchsorted(q, player)
            qDict[key] = np.insert(q, addPos, player)
    return qDict

def remFromQueue(qDict, player):
    """Removes the player from the correct queue in the qDict"""
    key = str(int(player.kt))
    q = qDict[key]
    delPos = np.searchsorted(q, player)
    if delPos == q.size:
        delPos = delPos-1
    qDict[key] = np.delete(q, delPos)
    return qDict  

def findOpponent(qDict, p, ktDiff, ktCutoff):
    """Finds an opponent if p.trophies is under the KT threshold. 
    Only call this if ktCutoffRule(p) == False 
    ktDiff >=0 """
    key = int(p.kt) #ensure int, not float
    orderToCheck = [str(key)]
    for diff in range(1, ktDiff+1):
        if 8 <= key + diff <= 14:
            orderToCheck += [str(key + diff)]
        if 8<= key - diff <= 14:
            orderToCheck += [str(key - diff)]
    for ktQueue in orderToCheck:
        q = qDict[ktQueue]
        addPos = np.searchsorted(q, p)
        if q.size == 0:
            pass
        elif addPos == q.size:
            opponent = q[addPos-1]
        else:
            opponent = q[addPos]
        try:
            if allowMatch(p, opponent, mode = 'KT', KTdiff = ktDiff, KTcutoff = ktCutoff):
                return opponent
        except UnboundLocalError as error:
            pass
    return p

def allowMatch(p1, p2, mode = None, cardLvlRule = 100, CLcutoff = 5000, KTdiff = 0, KTcutoff = 5000):
    """Checks if a match is allowed with the card level an king tower rules
    Args:
    p1: Player object
    p2: PLayer object
    mode: Type of matchmaking.  Either None, 'KT' or CL
    cardLevelRule - int, the maximum difference allowed in card levels
    CLcutoff- int, Max trophes where card level MM occurs
    KTdiff- int, maximum difference in king tower
    KTcutoff- int, max trophies where king tower MM occurs """
    cardRule = lambda p1, p2: abs(p1.cardLevel - p2.cardLevel) < cardLvlRule
    KTDiffRule = lambda p1, p2: abs(p1.kt - p2.kt) <= KTdiff
    if p1.id == p2.id:
        return False
    elif p1.matchAllowed(p2) == False:
        return False
    elif mode == 'CL':
        return cardRule(p1, p2) or p1.trophies > CLcutoff
    elif mode == 'KT':
        return KTDiffRule(p1, p2) or p1.trophies > KTcutoff 
    elif mode == 'KTCL': #Specialized simulation for this hasn't been made
        return (KTDiffRule(p1, p2) or p1.trophies > KTcutoff) and cardRule(p1, p2)
    else:
        return True
        
def plots(data, filename):
    """Makes 6 plots from the data and saves them:
    Bar graph of Lvl diff/Match vs King Tower
    Bar graph of lvl diff/match vs card level
    Histogram of Trophies and King Tower
    Histogram of card levels and king tower
    Scatterplot of card lvls vs trophies
    Scatterplot of lvl diff/match vs trophies
    
    Args: 
    data: Numpy array of player objects
    filename: String to be used as the file name
    """
    df = arrToDF(data)
    df2 = arrToDF(sepByCards(data))
    plt.figure(figsize = (6, 6))
    sns.barplot(x = "King Tower", y = "LvlDiff/Match", data = df)
    plt.savefig(filename + '1')
    plt.close()
    
    plt.figure(figsize = (20,6))
    sns.barplot(x = "Card Level", y = "LvlDiff/Match", data = df)
    plt.xticks(rotation = -45)
    plt.savefig(filename + '2')
    plt.close()

    plt.figure(figsize = (20, 8))
    sns.histplot(data = df,
            x = 'Trophies', 
            hue = 'King Tower',
            stat = 'count',
            palette = PALETTE,
            multiple = 'stack')
    plt.savefig(filename + '3')
    plt.close()

    plt.figure(figsize = (20, 8))
    sns.histplot(data=df2, 
             x = 'Trophies',
             hue = 'Card Level',
             stat = 'count',
             palette = sns.color_palette("CMRmap_r", n_colors = 13),
             multiple = 'stack')
    plt.savefig(filename + '4')
    plt.close()
    
    plt.figure(figsize = (16, 8))    
    sns.relplot(data = df, x = "Trophies", y = "Card Level", hue = "King Tower", palette = PALETTE)
    plt.savefig(filename + '5')
    plt.close()

    plt.figure(figsize = (20, 8))
    sns.relplot(data = df, x='Trophies', y = 'LvlDiff/Match', hue = 'King Tower', palette = PALETTE)
    plt.savefig(filename + '6')
    plt.close()
    
def sepByCards(arr):
    """Separates an array of player objecs by cards
    Args:
    arr: Array of player objects
    """
    playerCopy = [] #need to deepcopy the array
    for p in arr:
            new = pl.Player(id = p.id,
                            trophies=p.trophies,
                            wins=p.wins,
                            losses=p.losses,
                            kingLevel=p.kt,
                            cardLevel=p.cardLevel, 
                            totalLvlDiff=p.totalLvlDiff)
            playerCopy += [new]
    newArr = np.asarray(playerCopy)
    for player in newArr:
        if 60 <= player.cardLevel <= 63:
            player.cardLevel = '60-63'
        elif 64 <= player.cardLevel <= 67:
            player.cardLevel = '64-67'
        elif 68 <= player.cardLevel <= 71:
            player.cardLevel = '68-71'
        elif 72 <= player.cardLevel <= 75:
            player.cardLevel = '72-75'
        elif 76 <= player.cardLevel <= 79:
            player.cardLevel = '76-79'
        elif 80 <= player.cardLevel <= 83:
            player.cardLevel = '80-83'
        elif 84 <= player.cardLevel <= 87:
            player.cardLevel = '84-87'
        elif 88 <= player.cardLevel <= 91:
            player.cardLevel = '88-91'
        elif 92 <= player.cardLevel <= 95:
            player.cardLevel = '92-95'
        elif 96 <= player.cardLevel <= 99:
            player.cardLevel = '96-99'
        elif 100 <= player.cardLevel <= 103:
            player.cardLevel = '100-103'
        elif 104 <= player.cardLevel <= 107:
            player.cardLevel = '104-107'
        elif 108 <= player.cardLevel:
            player.cardLevel = '108-112'
    return newArr

def arrToDF(arr):
    """Converts an array of player objects to a dataframe
    Args: arr- Array of Player objects
    Returns: dataframe. 
    """
    #dataInLists = [p.getData() + [(p.totalLvlDiff/(p.wins+p.losses))] for p in arr]
    dataInLists = []
    for p in arr:
        new = p.getData()
        if p.wins+p.losses == 0:
            new += [0]
        else:
            new += [(p.totalLvlDiff/(p.wins+p.losses))]
        dataInLists += [new]
    return pd.DataFrame(data = dataInLists, columns = COLS)
     
def storeDF(df, filename):
    """Stores the dataframe in csv file filename
    Args:
    df:  Dataframe to store
    filename: string, name of file"""
    df.to_csv(filename, index_label = False)
    
def dfToArr(df, reset = False):
    """Converts a dataframe back into a numpy array of player objects
    Args
    df: A dataFrame with the data to be converted to an array of objects"""
    arrays = df.to_numpy()
    playerList = []
    if reset:
        for p in arrays:
            new = pl.Player(id = p[0], trophies = p[1],wins=0,losses =0, kingLevel=p[4],cardLevel = p[5],totalLvlDiff=0)
            new.reset()
            playerList += [new]
    else:
        for p in arrays:
            new = pl.Player(id = p[0],trophies=p[1],wins=p[2],losses=p[3],kingLevel=p[4],cardLevel=p[5], totalLvlDiff=p[6])
            playerList += [new]
    return np.asarray(playerList)

def CLsim(playerArr, numMatches, CLrule, CLcutoff, gatesList = [5000]):
    """Card level matchmaking simulation
    Args:
    playerArr: Array of player objects
    numMatches: int, number of matches to play
    CLrule: int, The max difference in card lvls between 2 players
    CLcutoff: int, the max trophes where CL mm occurs
    gatesList: List of ints representing trophy gates. 
    """
    queueDict = createDict()
    matchesPlayed = 0
    generalQueue = np.asarray([])
    while matchesPlayed < numMatches:
        if matchesPlayed %(numMatches//10) == 0:
            print(matchesPlayed)
        newPlayer = random.choice(playerArr)
        if newPlayer.trophies > CLcutoff:
            addPos= np.searchsorted(generalQueue, newPlayer)
            if generalQueue.size == 0:
                generalQueue = np.append(generalQueue, newPlayer)
                pass
            elif addPos == generalQueue.size:
                addPos = addPos - 1
            opponent = generalQueue[addPos]
            try: 
                if allowMatch(newPlayer,opponent,mode='CL',cardLvlRule=CLrule,CLcutoff=CLcutoff):
                    newPlayer.playMatch(opponent, gatesList = gatesList)
                    matchesPlayed += 1
                    generalQueue = np.delete(generalQueue, addPos)
                else:
                    generalQueue = np.insert(generalQueue, addPos, newPlayer)  
            except UnboundLocalError as error:
                print("Error")
        else: #need to use CL queues
            opponent = findOppCL(queueDict, newPlayer, CLrule)
            if opponent == newPlayer: #there is no opponents, add to proper queue
                queueDict = addToCQ(queueDict, newPlayer)
            else:
                newPlayer.playMatch(opponent,gatesList = gatesList)
                matchesPlayed += 1
                queueDict = remFromCQ(queueDict, opponent)
    playerArr.sort()
    return playerArr

def createDict():
    """Creates a card level dictionary"""
    d = {}
    for level in range(60, 113):
        d[str(level)] = np.asarray([], dtype = object)
    return d

def addToCQ(qDict, player):
    """Adds a player to the card level queue"""
    key = str(int(player.cardLevel))
    q = qDict[key]
    if q.size == 0:
        qDict[key] = np.append(q, player)
    elif player not in q:
            addPos = np.searchsorted(q, player)
            qDict[key] = np.insert(q, addPos, player)
    return qDict

def remFromCQ(qDict, player):
    key = str(int(player.cardLevel))
    q = qDict[key]
    delPos = np.searchsorted(q, player)
    if delPos == q.size:
        delPos = delPos-1
    qDict[key] = np.delete(q, delPos)
    return qDict  

def findOppCL(qDict, p, CLrule):
    """Finds an opponent in a card level matchmaking ladder. 
    Args:
    qDict: A dictionary of card level queues
    p: A player object 
    CLrule: Integer, a number of card levels difference to check """
    key = int(p.cardLevel) #ensure int, not float
    orderToCheck = [str(key)]
    for diff in range(1, CLrule+1):
        if 60 <= key + diff <= 112:
            orderToCheck += [str(key + diff)]
        if 60<= key - diff <= 112:
            orderToCheck += [str(key - diff)]
    for clQueue in orderToCheck:
        q = qDict[clQueue]
        addPos = np.searchsorted(q, p)
        if q.size == 0:
            pass
        elif addPos == q.size:
            opponent = q[addPos-1]
        else:
            opponent = q[addPos]
        try:
            if allowMatch(p, opponent, mode = 'CL', cardLvlRule=CLrule):
                return opponent
        except UnboundLocalError as error:
            pass
    return p
    

def test(initialArr, matchesPerSzn, filename, mode = None, CLrule = 100, CLcutoff= 5000, KTrule=1, KTcutoff = 1, gatesList = [5000]):
    """Runs 5 seasons of a simulation"""
    data = initialArr
    for season in [1, 2, 3, 4,5]:
        if mode == None: 
            data = continueSim(data, numMatches = matchesPerSzn, mode = None)
            print(f"Season {season} Complete")
        elif mode == 'KT':
            data = KTsim(data, numMatches = matchesPerSzn, KTdiff = KTrule, KTcutoff = KTcutoff)
            print(f"Season {season} Complete")
        elif mode == 'CL':
            data = CLsim(data, matchesPerSzn, CLrule, CLcutoff)
            print(f"Season {season} Complete")
        if season == 5:
            break
        else:
            for p in data:
                p.reset()
    #plots(data, filename)
    return data    

def finalSimulation():
    """Uses the result of 70 million battles to play out the most fair matchmaking rules for numSeason seasons.
    Rules: No KTmm, No CLmm, Trophy caps are [5300, 5600, 6000, 6300, 6600, 7000]. 
    Plays 16 million battles per season for 12 seasons"""
    kingTowers = []
    playerL = []
    while len(kingTowers) < 100000:  #initialize king towers
        kt = round(random.gauss(11, 1.5))
        if kt in range(8, 15):
             kingTowers += [kt]
        else:
             pass
    for i in range(100000): #establish player array
        kt = kingTowers[i]
        newP = pl.createRealPlayers(kingLvl = kt,id = i, skill = random.gauss(0.5, 0.16667), pp = random.gauss(0.2, 0.15))
        playerL += [newP]
    playerArr = np.asarray(playerL)
    queue = np.asarray([random.choice(playerArr)], dtype = object)
    matchesPlayed = 0
    for season in range(1,13):
        while matchesPlayed < 16000000:
            if matchesPlayed %(2400000) == 0:
                print(matchesPlayed)
            if queue.size == 0:
                queue = np.append(queue, random.choice(playerArr))
                pass
            else:
                newPlayer = random.choice(playerArr)
                if newPlayer in queue:
                    pass #can't play against themself
                elif random.random() < newPlayer.pp: #player isn't playing ladder
                    pass
                else:
                    addPos = np.searchsorted(queue, newPlayer)
                    if addPos == queue.size:
                        addPos += -1
                        opponent = queue[addPos]
                    else:
                        opponent = queue[addPos]
                    if allowMatch(newPlayer, opponent):
                        originalLevels = [newPlayer.cardLevel, opponent.cardLevel]
                        cap = (8 + np.searchsorted([5300, 5600, 6000, 6300, 6600, 7000], min(newPlayer.trophies, opponent.trophies)))*8
                        newPlayer.cardLevel = min(newPlayer.cardLevel, cap)
                        opponent.cardLevel = min(opponent.cardLevel, cap)
                        newPlayer.playMatch(opponent)
                        matchesPlayed += 1
                        queue = np.delete(queue, addPos)
                        newPlayer.cardLevel = originalLevels[0]
                        opponent.cardLevel = originalLevels[1]
                    else:
                        queue = np.insert(queue, addPos, newPlayer)
        print(f"Season {season} complete")
        for p in playerArr:
            p.reset()
        matchesPlayed = 0
    playerArr.sort()
    return playerArr


    



