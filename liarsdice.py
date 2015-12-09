import random
from collections import Counter

NUM_PLAYERS = 3
INITIAL_NUM_DICE_PER_PLAYER = 5
DICE_SIDES = 6
SHOW_ALL_HANDS = True

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

    def isGameOver(self, playerIndex = None):
        if playerIndex is not None:
            return self.isWin(playerIndex) or self.isLose(playerIndex)

        # only one player can have dice for the game to be over
        return 1 == sum(1 for numDice in self.numDicePerPlayer if numDice > 0)

    def getNextPlayer(self):
        nextPlayer = (self.currentPlayerIndex + 1) % NUM_PLAYERS
        # skip players that are out
        while self.numDicePerPlayer[nextPlayer] == 0:
            nextPlayer = (nextPlayer + 1) % NUM_PLAYERS

        return nextPlayer

    def getCurrentPlayerIndex(self):
        return self.currentPlayerIndex

    def getHandsString(self):
        gameStateString = ''
        for playerIndex, hand in enumerate(self.hands):
            gameStateString += 'Player %d  |  %s\n' % (playerIndex, ','.join(str(h) for h in hand.elements()))

        return gameStateString

class InitialGameState(GameState):
    def __init__(self, numDicePerPlayer, currentPlayerIndex, roundHistory, gameHistory):
        """
        Generates a new state by copying information from its predecessor.
        """
        self.hands = [Counter(random.randint(1,DICE_SIDES) for _ in range(numDice)) for numDice in numDicePerPlayer]
        self.bid = None
        self.roundHistory= []
        self.gameHistory = gameHistory
        [self.gameHistory.append(act) for act in roundHistory]
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

        return MedialGameState(self.numDicePerPlayer, self.hands, self.getNextPlayer(), [], self.gameHistory, action)

    def isLose(self, playerIndex):
        return self.numDicePerPlayer[playerIndex] == 0

    def isWin(self, playerIndex):
        return self.numDicePerPlayer[playerIndex] > 0 and self.totalNumDice == self.numDicePerPlayer[playerIndex]

    def __str__(self):
        return self.getHandsString() + '\nNo current bid\n'

class MedialGameState(GameState):
    def  __init__(self, numDicePerPlayer, hands, currentPlayerIndex, roundHistory, gameHistory, bid):
        self.hands = hands
        self.currentPlayerIndex = currentPlayerIndex
        self.gameHistory = gameHistory
        self.roundHistory = roundHistory
        self.roundHistory.append(bid)
        self.bid = bid
        self.numDicePerPlayer = numDicePerPlayer
        self.totalNumDice = sum(numDicePerPlayer)

    def getLegalActions(self):
        """
        Returns the legal actions for the player specified.
        """
        currentCount = self.bid[2]
        totalNumberOfDice = sum(sum(hand.values()) for hand in self.hands)
        actions = [('bid', value, count, self.currentPlayerIndex)
                for value in range(1, DICE_SIDES + 1) for count in range(currentCount + 1, totalNumberOfDice + 1)]

        actions.append(('confirm', self.bid[1], self.bid[2], self.bid[3]))
        actions.append(('deny', self.bid[1], self.bid[2], self.bid[3]))

        return actions

    def generateSuccessor(self, action):
        """
        Returns the successor state after the specified player takes the action.
        """
        verb, value, bidCount, previousBidPlayerIndex = action
        if verb == 'bid':

            return MedialGameState(self.numDicePerPlayer,
                                   self.hands,
                                   self.getNextPlayer(),
                                   self.roundHistory,
                                   self.gameHistory,
                                   action)
        else:
            # Note:
            # -----
            # For any action the 'winner' goes next

            # copy numDicePerPlayer
            numDicePerPlayer = [numDice for numDice in self.numDicePerPlayer]
            trueCountOfReleventDie = sum(hand[value] for hand in self.hands)

            if verb == 'confirm':
                if bidCount == trueCountOfReleventDie:
                    for playerIndex, numDice in enumerate(numDicePerPlayer):
                        if playerIndex != self.currentPlayerIndex and numDice > 0:
                            # each player loses a die, except the confirming player
                            numDicePerPlayer[playerIndex] -= 1
                            nextPlayer = self.currentPlayerIndex
                else:
                    # confirming player loses a die
                    numDicePerPlayer[self.currentPlayerIndex] -= 1
                    # whoever 'wins' goes next
                    nextPlayer = previousBidPlayerIndex
            else:
                assert verb == 'deny'
                if trueCountOfReleventDie < bidCount:
                    # prev player loses a die
                    numDicePerPlayer[previousBidPlayerIndex] -= 1
                    nextPlayer = self.currentPlayerIndex
                else:
                    # denying player loses a die, same as confirming
                    numDicePerPlayer[self.currentPlayerIndex] -= 1
                    nextPlayer = previousBidPlayerIndex

            return InitialGameState(numDicePerPlayer, nextPlayer, self.roundHistory, self.gameHistory)

    def __str__(self):
        _, value, count, bidPlayer = self.bid
        return self.getHandsString() + "\nPlayer %d bids that there are at least %d %d's\n" % (bidPlayer, count, value)
