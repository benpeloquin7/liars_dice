"""
Terminology:
-Agent: Our intelligent AI that will be simulating moves in advance and carrying out a smart policy.
-Player: An agent or an opponent.
-Round: The length of gameplay between when dice are (re)rolled and someone callsBluff/confirmsBid.
"""

import random
from collections import Counter

NUM_PLAYERS = 3
DICE_SIDES = 6
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

class GameState:
    def __init__(self):
        pass

    def getLegalActions(self):
        raise Exception("abstract")

    def generateSuccessor(self):
        raise Exception("abstract")

    def isWin(self, playerIndex):
        return False

    def isLose(self, playerIndex):
        return False

    def getNextPlayer(self):
        nextPlayer = (self.currentPlayerIndex + 1) % NUM_PLAYERS
        # skip players that are out
        while self.numDicePerPlayer[nextPlayer] == 0:
            nextPlayer = (self.currentPlayerIndex + 1) % NUM_PLAYERS

        return nextPlayer


class InitialGameState(GameState):
    def __init__(self, numDicePerPlayer, currentPlayerIndex):
        """
        Generates a new state by copying information from its predecessor.
        """
        self.hands = [Counter(random.randint(1,DICE_SIDES) for _ in range(numDice)) for numDice in numDicePerPlayer]
        self.bid = None
        self.currentPlayerIndex = currentPlayerIndex
        self.numDicePerPlayer = numDicePerPlayer
        # maintain count of active players   
        #self.activePlayers = len()

        assert len(numDicePerPlayer) == NUM_PLAYERS

    def getLegalActions(self):
        """
        Returns the legal actions for the player specified.
        """
        totalNumberOfDice = sum(self.numDicePerPlayer)
        return [('bid', value, count, self.currentPlayerIndex)
                for value in range(1, DICE_SIDES + 1) for count in range(1, totalNumberOfDice + 1)]

    def generateSuccessor(self, action):
        """
        Returns the successor state after the specified player takes the action.
        """
        verb, value, count, bidPlayer = action
        assert verb == 'bid'

        return MedialGameState(self.numDicePerPlayer, self.hands, self.getNextPlayer(), action)

    def isLose(self, playerIndex):
        return self.numDicePerPlayer[playerIndex] == 0

    def isWin(self, playerIndex):
        return self.numDicePerPlayer[playerIndex] > 0 and\
               all(numDice == 0 for otherPlayer, numDice in enumerate(self.numDicePerPlayer) if otherPlayer != playerIndex)

class MedialGameState(GameState):
    def  __init__(self, numDicePerPlayer, hands, currentPlayerIndex, bid):
        self.hands = hands
        self.currentPlayerIndex = currentPlayerIndex
        self.bid = bid
        self.numDicePerPlayer = numDicePerPlayer

    def getLegalActions(self):
        """
        Returns the legal actions for the player specified.
        """
        currentCount = self.bid[2]
        totalNumberOfDice = sum(sum(hand.values()) for hand in self.hands)
        actions = [('bid', value, count, self.currentPlayerIndex)
                for value in range(1, DICE_SIDES + 1) for count in range(currentCount + 1, totalNumberOfDice + 1)]

        actions.append(('confirm', self.bid[1], self.bid[2], self.currentPlayerIndex))
        actions.append(('deny', self.bid[1], self.bid[2], self.currentPlayerIndex))

        return actions

    def generateSuccessor(self, action):
        """
        Returns the successor state after the specified player takes the action.
        """
        verb, value, count, bidPlayerIndex = action
        if verb == 'bid':

            return MedialGameState(self.numDicePerPlayer,
                                   self.hands,
                                   self.getNextPlayer(),
                                   action)
        else:
            # Note:
            # -----
            # For any action the 'winner' goes next

            # copy numDicePerPlayer
            numDicePerPlayer = [numDice for numDice in self.numDicePerPlayer]
            trueCountOfReleventDie = sum(hand[value] for hand in self.hands)

            if verb == 'confirm':
                if count == trueCountOfReleventDie:
                    for playerIndex, numDice in enumerate(numDicePerPlayer):
                        if playerIndex != self.currentPlayerIndex and numDice > 0:
                            # each player loses a die, except the confirming player
                            numDicePerPlayer[playerIndex] -= 1
                            nextPlayer = self.currentPlayerIndex
                else:
                    # confirming player loses a die
                    numDicePerPlayer[self.currentPlayerIndex] -= 1
                    # whoever 'wins' goes next
                    nextPlayer = bidPlayerIndex
            else:
                assert verb == 'deny'
                if count < trueCountOfReleventDie:
                    # prev player loses a die
                    numDicePerPlayer[bidPlayerIndex] -= 1
                    nextPlayer = self.currentPlayerIndex
                else:
                    # denying player loses a die, same as confirming
                    numDicePerPlayer[self.currentPlayerIndex] -= 1
                    nextPlayer = bidPlayerIndex

            return InitialGameState(numDicePerPlayer, nextPlayer)

igs = InitialGameState([2, 2, 2], 0)
# mgs = igs.generateSuccessor(igs.getLegalActions()[0])
# igs.isWin(0)
#
# print mgs.getLegalActions()[0]
# mgs.generateSuccessor(mgs.getLegalActions()[0]).isWin(2)