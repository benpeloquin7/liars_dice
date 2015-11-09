from liarsdice import *
import random
import itertools
import math
import pdb

P = float(1)/DICE_SIDES

class Agent:
    def chooseAction(self, gameState):
        raise Exception('abstract')

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

    def choose(self, n, k):
        """
        Binomial coefficient: (n! / (n-k)!k!)
        """
        return float(math.factorial(n)) / (math.factorial(n - k) * math.factorial(k))
        # nFact = math.factorial(n)
        # kFact = math.factorial(k)
        # nMinusKFact = math.factorial(n - k)
        # return float(nFact) / (kFact * nMinusKFact)

    def confirmProbability(self, totalDice, bidCount):
        """
        Assign a probability that a confirmation is true (i.e. |value| == bid_count)
        """
        result = self.choose(totalDice, bidCount) * P**bidCount * (1 - P)**(totalDice-bidCount)
        return result        

    def bidProbability(self, totalDice, bidCount):
        """
        Assign a probability that a bid is true (i.e. |value| >= bid_count)
        """
        result = sum([self.confirmProbability(totalDice, i) for i in range(bidCount, totalDice)])
        return result

    def assignProbablities(self, gameState):
        """
        For each bid in actions 
        """
        legalActions = gameState.getLegalActions()
        numDiceActive = sum(gameState.numDicePerPlayer)
        probActionTuples = []

        for action in legalActions:
            pdb.set_trace()
            currentHand = gameState.hands[self.agentIndex]
            currentAction = action
            remainingTotalDice = gameState.totalNumDice - gameState.numDicePerPlayer[self.agentIndex]
            assert remainingTotalDice > 0
            remainingActionCount = currentAction[2] - currentHand[currentAction[1]]
            if remainingActionCount > 0:
                 # or (action[0] == "confirm" and remainingActionCount == 0)
                if action[0] == "bid":
                    probActionTuples.append((self.bidProbability(remainingTotalDice, remainingActionCount), action))
                elif action[0] == "deny":
                    probActionTuples.append((1 - self.bidProbability(remainingTotalDice, remainingActionCount), action))
                else:
                    probActionTuples.append((self.confirmProbability(remainingTotalDice, remainingActionCount), action))
            elif remainingActionCount == 0:
                if action[0] == "bid":
                    probActionTuples.append((1, action))
                elif action[0] == "deny":
                    probActionTuples.append((0, action))
                else:
                    probActionTuples.append((self.confirmProbability(remainingTotalDice, remainingActionCount), action))
            else:
                if action[0] == "bid":
                    probActionTuples.append((1, action))
                else:
                    probActionTuples.append((0, action))

        return probActionTuples

    def chooseAction(self, gameState):
        """
        Return action with highest probability
        """
        probabilities = self.assignProbablities(gameState)
        print probabilities
        prob, bestProbabilityAction = max(probabilities)
        return bestProbabilityAction

numDicePerPlayer = [2, 2]
honestAgent = HonestProbabilisticAgent(0)
igs = InitialGameState(numDicePerPlayer, honestAgent.agentIndex)
print igs.hands[honestAgent.agentIndex]
print honestAgent.chooseAction(igs)