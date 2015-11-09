from liarsdice import *
import random
import itertools
import math
import pdb

class Agent:
    def chooseAction(self, gameState):
        raise Exception('abstract')

class OracleAgent:
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def chooseAction(self, gameState):
        legalActions = gameState.getLegalActions()
        goodActions = []
        def checkTrue(bid):
            (bidstr, value, count, agentIndex) = bid
            s = 0
            for hand in gameState.hands:
                s += hand[value]

            if s > count:
                return 1
            elif s == count:
                return 2
            else:
                return 0

        #Pick a list of true bids to make.
        for act in legalActions:
            if(checkTrue(act) > 0):
                goodActions.append(act)

        if gameState.bid is not None:
            bid = gameState.bid
            if checkTrue(gameState.bid) == 0:
                return ('deny', bid[1], bid[2], bid[3])
            elif checkTrue(gameState.bid) == 2:
                return ('confirm', bid[1], bid[2], bid[3])
        else:
            ix = random.randint(0, len(goodActions)-1)
            return goodActions[ix]

        pass

class HumanAgent(Agent):
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def chooseAction(self, gameState):
        def validateActionFormat(actionParts):
            if actionParts[0] not in ('bid', 'confirm', 'deny'):
                return False
            if actionParts[0] == 'bid':
                if len(actionParts) != 3:
                    return False
                if not actionParts[1].isdigit() or not actionParts[2].isdigit():
                    return False
            elif len(actionParts) != 1: #confirm or deny
                return False
            return True

        possibleActions = gameState.getLegalActions()
        actionString = raw_input('Player %d, Enter your action: ' % self.agentIndex)
        while True:
            # parse the action
            actionParts = actionString.split()
            if validateActionFormat(actionParts):
                if actionParts[0] == 'bid':
                    verb, count, value = actionParts
                    action = verb, int(value), int(count), self.agentIndex
                    if action in possibleActions:
                        return action
                else: # confirm or deny
                    matchingActions = filter(lambda a: a[0] == actionParts[0], possibleActions)
                    if len(matchingActions) > 0:
                        return matchingActions[0]

            actionString = raw_input('That is not a legal action.\nPlayer %d, Try again: ' % self.agentIndex)

class RandomAgent(Agent):
    """
    Random agent chooses randomly from getLegalActions
    """
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def chooseAction(self, gameState):
        random_action = random.choice(gameState.getLegalActions())
        return random_action

# numDicePerPlayer = [3, 3, 3]
# random_agent = RandomAgent(0)
# igs = InitialGameState(numDicePerPlayer, random_agent.agentIndex)
# print random_agent.chooseAction(igs)

class HonestProbabilisticAgent(Agent):
    """
    Agent chooses actions based on highest probability
    """
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def bidProbability(self, bid, numDice):
        """
        Assign a probability that a bid is true (i.e. |value| >= bid_count)
        """
        def choose(n, k):
            nFact = math.factorial(n)
            kFact = math.factorial(k)
            nMinusKFact = math.factorial(n - k)
            return float(nFact) / (kFact * nMinusKFact)
        n = numDice
        k = bid[2]
        p = float(1)/6
        result = sum([(choose(n, k) * p**i * (1 - p)**(n-i)) for i in range(k, n + 1)])
        return result

    def assignProbablities(self, gameState):
        """
        For each bid in actions
        """
        legalActions = gameState.getLegalActions()
        numDiceActive = sum(gameState.numDicePerPlayer)
        probActionTuples = []
        for action in legalActions:
            if action[0] == "bid":
                probActionTuples.append((self.bidProbability(action, numDiceActive), action))
            elif action[0] == "deny":
                probActionTuples.append((1 - self.bidProbability(action, numDiceActive), action))
            else:
                probActionTuples.append((float(1)/len(legalActions), action))
        return probActionTuples



action = ('bid', 1, 2, 0)
numDicePerPlayer = [2, 2]
honestAgent = HonestProbabilisticAgent(0)
igs = InitialGameState(numDicePerPlayer, honestAgent.agentIndex)
print honestAgent.assignProbablities(igs)