"""
Terminology:
-Agent: Our intelligent AI that will be simulating moves in advance and carrying out a smart policy.
-Player: An agent or an opponent.
-Round: The length of gameplay between when dice are (re)rolled and someone callsBluff/confirmsBid.
"""

import random

class PlayerRules:
    """
    Represents the rules of the game from players' perspective.
    Specifically, what actions can be performed (getLegalActions) and what will happen
    if an action is taken (applyActions).
    """

    def getLegalActions( state ):
        """
        Returns list of legal actions, given state of the game.
        """
        hands = state.hands
        ante = state.ante
        totalDice = state.totalDice
        assert ante < totalDice, 'Ante exceeds number of dice!' #ISSUE: Should figure out what happens next in this case.

        if not state.round_begin:
            possibleActs.append('callBluff', 'confirmBid')

        for bidQuant in range(ante+1, totalDice+1):
            possibleActs.append([(bidQuant, bidVal) for bidVal in range(1,state.diceSides)])

        return possibleActs
    getLegalActions = staticmethod( getLegalActions )

    def applyAction( state, action, cc ):
        """
        Edits the state to reflect the results of the action.

        cc is an instance of CentralControl.
        """
        legal = PlayerRules.getLegalActions( state )
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        if action == 'callBluff' or action == 'confirmBid':
            cc.evaluateAction(state, action)
            cc.reroll(state)

        else: #Action was a bid.
            state.currBid = action

    applyAction = staticmethod( applyAction )


class CentralControl():
    """
    Currently stores functions that update the gamestate based on player actions.

    May want to merge this with PlayerRules, but the idea is CentralControl is more like "nature", i.e.,
    this class is "allowed" to access gameState.trueHands.
    """
    def __init__(self):
        #ISSUE: Note sure if this should have a constructor, or just be staticmethods like PlayerRules.
        pass

    def evaluateAction(self, state, action ):
        """
        Refers to the true hands in gameState to resolve callBluffs and confirmBids
        """
        trueHands = state.trueHands
        cp = state.data.currentPlayer #current player
        pp = state.data.previousPlayer

        (bidQuant, bidVal) = state.currBid

        s = 0
        #Compute quantity of bidVal that really exist
        for hand in trueHands:
            for val in hand:
                s+= (val == bidVal)

        if action == 'callBluff':
            if bidQuant >= s:
                #cp loses a die
                state.dicePerPlayer[cp] -= 1
            else:
                #pp loses a die
                state.dicePerPlayer[pp] -= 1

        elif action == 'confirmBid':
            if bidQuant != s:
                state.dicePerPlayer[cp] -= 1
            else:
                #Everyone loses a die except cp.
                state.dicePerPlayer = [dice-1 for ix, dice in enumerate(state.dicePerPlayer) if ix != cp]


    def reroll(self, state):
        """
        Rerolls everyone's dice, setting a new .trueHands in the GameState.

        Note that reroll should be called iff dicePerPlayer changes, as in evaluateAction.
        """
        state.trueHands = []
        dpp = state.dicePerPlayer

        for i in range(state.numOpps+1):
            state.trueHands.append([random.randint(1,6) for j in range(0,dpp[i])])


class GameStateData:
    """
    Pacman starter code had a class for GameStateData (game.py) and GameState (pacman.py). Following the same convention,
    GameStateData contains all the data about the GameState, where GameState includes methods for accessing the data.

    Should consider merging it all into one class.
    """
    def __init__( self, prevState = None ):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        if prevState != None:
            self.trueHands = prevState.trueHands.deepCopy()
            self.dicePerPlayer = prevState.dicePerPlayer
            self.numOpps = prevState.numOpps
            self.currBid = prevState.currBid.deepCopy()

            #ISSUE: Obviously these need to incremement. But where should that happen?
            self.currPlayer = prevState.currPlayer
            self.prevPlayer = prevState.prevPlayer

        self.trueHands = []
        self.dicePerPlayer = None
        self.numOpps = None
        self._lose = False
        self._win = False

    def initialize( self, dicePerPlayer, diceSides, numOpps ):
        """
        Initialize the game.
        """
        self.totalDice = dicePerPlayer*numOpps

        self.trueHands = [] #List of sub-lists, where each sub-list holds a different player's dice values. 0th sub-list is agent's.
        self.diceSides = diceSides #Number of sides per dice. Typically 6.
        self.dicePerPlayer = [dicePerPlayer]*(numOpps + 1) #List keeping track of how many dice each player has.
        self.numOpps = numOpps

        for i in range(numOpps+1):
            self.trueHands.append([random.randint(1,6) for j in range(0,dicePerPlayer[i])])

        self.currPlayer = 0 #ISSUE: Always give our agent the first turn?
        self.currBid = (None, None)
        self.prevPlayer = None


class GameState:
    def __init__(self):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState != None: # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()


    def initialize( self, dicePerPlayer, diceSides, numOpps ):
        """
        Creates an initial game state.
        """
        self.data.initialize( self, dicePerPlayer, diceSides, numOpps )

    def getLegalActions( self, playerIndex=0 ):
        """
        Returns the legal actions for the player specified.
        """
        if self.isWin() or self.isLose(): return []

        return PlayerRules.getLegalActions(self)

    def generateSuccessor( self, playerIndex, action):
        """
        Returns the successor state after the specified player takes the action.
        """
        # Check that successors exist
        if self.isWin() or self.isLose(): raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = GameState(self)

        PlayerRules.applyAction( state, action, playerIndex)
        return state
