import random
from collections import Counter

NUM_PLAYERS = 3
INITIAL_NUM_DICE_PER_PLAYER = 3
DICE_SIDES = 6

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

    def isGameOver(self):
        # only one player can have dice for the game to be over
        return 1 == sum(1 for numDice in self.numDicePerPlayer if numDice > 0)

    def getNextPlayer(self):
        nextPlayer = (self.currentPlayerIndex + 1) % NUM_PLAYERS
        # skip players that are out
        while self.numDicePerPlayer[nextPlayer] == 0:
            nextPlayer = (self.currentPlayerIndex + 1) % NUM_PLAYERS

        return nextPlayer

    def getCurrentPlayerIndex(self):
        return self.currentPlayerIndex

class InitialGameState(GameState):
    def __init__(self, numDicePerPlayer, currentPlayerIndex):
        """
        Generates a new state by copying information from its predecessor.
        """
        self.hands = [Counter(random.randint(1,DICE_SIDES) for _ in range(numDice)) for numDice in numDicePerPlayer]
        self.bid = None
        self.currentPlayerIndex = currentPlayerIndex
        self.numDicePerPlayer = numDicePerPlayer
        self.totalNumDice = sum(numDicePerPlayer)

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
        return self.numDicePerPlayer[playerIndex] > 0 and self.totalNumDice == self.numDicePerPlayer[playerIndex]

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