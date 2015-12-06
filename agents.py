from liarsdice import *
import random
import itertools
import math
import pdb

P = float(1)/DICE_SIDES

class Agent:
    def chooseAction(self, gameState):
        raise Exception('abstract')

    def initializeGame(self):
        return InitialGameState([INITIAL_NUM_DICE_PER_PLAYER] * NUM_PLAYERS, random.randint(0, NUM_PLAYERS - 1))

class OracleAgent:
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def chooseAction(self, gameState):
        legalActions = gameState.getLegalActions()
        goodActions = []
        def checkTrue(bid):
            #If no bid has been placed, bid.
            try:
                (bidstr, value, count, agentIndex) = bid
            except TypeError:
                return 1

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

        ev = checkTrue(gameState.bid)
        if ev != 1:
            bid = gameState.bid
            if ev == 0:
                return ('deny', bid[1], bid[2], bid[3])
            elif ev == 2:
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
        result = sum([self.confirmProbability(totalDice, i) for i in range(bidCount, totalDice + 1)])
        return result

    def assignProbablities(self, gameState):
        """
        For each bid in actions
        """
        legalActions = gameState.getLegalActions()
        numDiceActive = sum(gameState.numDicePerPlayer)
        probActionTuples = []

        for action in legalActions:
            currentHand = gameState.hands[self.agentIndex]
            currentAction = action
            remainingTotalDice = gameState.totalNumDice - gameState.numDicePerPlayer[self.agentIndex]
            assert remainingTotalDice > 0
            remainingActionCount = currentAction[2] - currentHand[currentAction[1]]
            if remainingActionCount > remainingTotalDice:
                if action[0] == 'deny':
                    probActionTuples.append((1, action))
                else:
                    probActionTuples.append((0, action))
            elif remainingActionCount > 0:
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
        #print probabilities
        prob, bestProbabilityAction = max(probabilities)
        return bestProbabilityAction

#numDicePerPlayer = [2, 2]
#honestAgent = HonestProbabilisticAgent(0)
#igs = InitialGameState(numDicePerPlayer, honestAgent.agentIndex)
#print igs.hands[honestAgent.agentIndex]
#print honestAgent.chooseAction(igs)

class PureQLearningAgent(Agent):
    def __init__(self, agentIndex, featureExtractor, exploreProb, discount):
        self.featureExtractor = featureExtractor
        self.weights = Counter()
        self.exploreProb = exploreProb
        self.discount = discount
        self.numIters = 0
        self.agentIndex = agentIndex


    def learn(self, numGames, trainingOpponents):
        players = [self] + trainingOpponents
        assert len(trainingOpponents) == NUM_PLAYERS - 1

        for _ in range(numGames):
            state = self.initializeGame()
            oldState = None
            oldAction = None
            while not state.isGameOver(self.agentIndex):
                # agent or any opponent chooses action
                currentPlayerIndex = state.getCurrentPlayerIndex()
                action = players[currentPlayerIndex].chooseAction(state)
                newState = state.generateSuccessor(action)

                if newState.getCurrentPlayerIndex() == self.agentIndex:
                    if oldState is not None:
                        assert oldAction is not None
                        # consider computing the rewards for dice lost between rounds
                        self.incorporateFeedback(oldState, oldAction, newState)

                if currentPlayerIndex == self.agentIndex:
                    oldState = state
                    oldAction = action

                state = newState

            if oldState is not None:
                assert oldAction is not None
                self.incorporateFeedback(oldState, oldAction, state, self.computeReward(newState))

    def incorporateFeedback(self, oldState, action, newState, reward = 0):
        prediction = self.getQ(oldState, action)
        actualUtility = reward if newState.isGameOver(self.agentIndex) else \
            reward + self.discount * max(self.getQ(newState, a) for a in newState.getLegalActions())
        coefficient = self.getStepSize() * (prediction - actualUtility)
        for name, featureValue in self.featureExtractor(oldState, action, self.agentIndex):
            self.weights[name] -= coefficient * float(featureValue)

    def chooseAction(self, gameState):
        self.numIters += 1
        if random.random() < self.exploreProb:
            return random.choice(gameState.getLegalActions())
        else:
            return max((self.getQ(gameState, action), action) for action in gameState.getLegalActions())[1]

    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action, self.agentIndex):
            score += self.weights[f] * v
        return score

    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    def computeReward(self, state):
        return 1000 if state.isWin(self.agentIndex) else -1000

def featureExtractor1(state, action, agentIndex):
    features = []
    verb, value, count, _ = action
    numDicePerPlayer = state.numDicePerPlayer
    handSize = numDicePerPlayer[agentIndex]
    totalNumDice = state.totalNumDice
    hand = state.hands[agentIndex]
    bid = state.bid

    # pure state features
    features.append((('numDice', handSize), 1))
    features.append((('numDiceDifference', totalNumDice - handSize), 1))

    features.append((('totalDice-verb-count', (totalNumDice, verb, count)), 1)) # magnitude of action given number of dice
    features.append((('handSize-verb-count', (handSize, verb, count)), 1)) # magnitude of action given our hand size
    # features.append((('', (hand[value] > 0, verb)), 1)) # doing this verb given existence of corresponding value in your hand
    features.append((('handValue-verb-count', (hand[value], verb, count)), 1)) # magnitude of action given how many in hand
    features.append((('bidIsNone-verb-count', (bid is None, verb, count)), 1)) # magnitude of an initial state action

    if bid is not None:
        _, bidValue, bidCount, _ = bid
        features.append((('count-Minus-BidCount', (verb, count - bidCount)), 1)) # how much you raise the bid by

    return features

class BayesianAgent(Agent):
    def __init__(self):
        # Matrix of probabilities given the number of relevant dice in the player's current
        # hand, and the max count of a previous bid for that die (which needs to go from 0 to
        # the total number of dice, inclusive)
        self.localConditionalProbabilities = [[Counter() for _ in range(INITIAL_NUM_DICE_PER_PLAYER)]
                                              for _ in range(INITIAL_NUM_DICE_PER_PLAYER * NUM_PLAYERS + 1)]

    def learn(self, numGames, trainingPlayers):
        assert len(trainingPlayers) == NUM_PLAYERS
        maxCountsPerValueInPreviousBids = dict()

        for _ in range(numGames):
            state = self.initializeGame()
            # Don't play, just watch the opponents play each other, and observe
            # their behaviors given their hands
            while not state.isGameOver():
                # An opponent chooses an action
                currentPlayerIndex = state.getCurrentPlayerIndex()
                currentPlayerHand = state.hands[currentPlayerIndex]
                verb, value, count, _ = trainingPlayers[currentPlayerIndex].chooseAction(state)


                if isinstance(state, InitialGameState):
                    maxCountsPerValueInPreviousBids.clear()

                # Use maximum likelihood to track the probability that the player made that action,
                # given their hand and the max count that particular value in the bid history
                self.localConditionalProbabilities \
                    [maxCountsPerValueInPreviousBids[value]] \
                    [currentPlayerHand[value]][(verb, count)] += 1

                # Since the game requires that bids be strictly increasing,
                # the current count is the max for this value
                maxCountsPerValueInPreviousBids[value] = count

        self.normalize()

    def normalize(self):
        for row in self.localConditionalProbabilities:
            for counter in row:
                # Make it a float so that we will get well formed probabilities
                denominator = float(sum(counter.itervalues()))
                for key in counter.iterkeys():
                    counter[key] /= denominator