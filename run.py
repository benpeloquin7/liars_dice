from liarsdice import *
from agents import *
import random
import os
from os import path

# Main game play

# while num players is more than one
# Counter of number of players?

def playGame(firstAgentOnly, agents = None, logFilePath = None, shouldPrint = True):
    def printOutput(text):
        if shouldPrint:
            print text

    if agents is None:
        agents = [HumanAgent(i) for i in range(NUM_PLAYERS)]
    # start with a random player
    gameState = InitialGameState([INITIAL_NUM_DICE_PER_PLAYER] * NUM_PLAYERS, random.randint(0, NUM_PLAYERS - 1))
    logFile = open(logFilePath, 'w') if logFilePath is not None else None
    log(logFile, '----------------------------------\nGame 1:')
    while not gameState.isGameOver():
        printOutput('----------------------------------\n')
        printOutput(str(gameState))
        # only log hand for initial game state
        if isinstance(gameState, InitialGameState):
            log(logFile, '\n' + gameState.getHandsString())

        agent = agents[gameState.getCurrentPlayerIndex()]
        chosenAction = agent.chooseAction(gameState)
        verb, value, count, _ = chosenAction
        playerIndex = gameState.getCurrentPlayerIndex()
        log(logFile, '%s(%d) = %d %d' % (verb, playerIndex, count, value))

        gameState = gameState.generateSuccessor(chosenAction)

        # we may only care about the first agent
        if firstAgentOnly and gameState.isLose(0):
            log(logFile, '\nAgent 0 lost')
            #print '----------------------------------\n'
            #print 'Player 0 lost...'
            break


    for i in range(NUM_PLAYERS):
        if gameState.isWin(i):
            printOutput('----------------------------------\n')
            printOutput('Player %d won!' % i)

    if gameState.isWin(0):
        log(logFile, '\nAgent 0 won')

    if logFile is not None:
        logFile.close()

    return gameState.isWin(0)

def log(logFile, text):
    if logFile is not None:
        print >>logFile, text

def simulateGames(numGames):

    d = {}

    agentses = []
    names = []
    # agentses.append([HonestProbabilisticAgent(0), RandomAgent(1), RandomAgent(2)])
    # names.append('hrr')
    #
    # agentses.append([OracleAgent(0), RandomAgent(1), RandomAgent(2)])
    # names.append('orr')
    #
    # agentses.append([OracleAgent(0), HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)])
    # names.append('ohh')
    #
    # agentses.append([HonestProbabilisticAgent(0), HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)])
    # names.append('hhh')

    # pureQLearnAgent = PureQLearningAgent(0, featureExtractor1, 0.05, 0.3)
    # pureQLearnAgentOpponents = [HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)]
    # pureQLearnAgent.learn(2500, pureQLearnAgentOpponents)
    # agentses.append([pureQLearnAgent] + pureQLearnAgentOpponents)
    # names.append("qhh")

    # pureQLearnAgent = PureQLearningAgent(0, featureExtractor1, 0.05, 0.3)
    # pureQLearnAgentOpponents = [RandomAgent(1), RandomAgent(2)]
    # pureQLearnAgent.learn(2500, pureQLearnAgentOpponents)
    # agentses.append([pureQLearnAgent] + pureQLearnAgentOpponents)
    # names.append("qrr")

    bayesAgent = BayesianAgent(0)
    bayesAgentOpponents = [HonestProbabilisticAgent(0), HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)]
    bayesAgent.learn(2500, bayesAgentOpponents)
    agentses.append([bayesAgent, bayesAgentOpponents[1], bayesAgentOpponents[2]])
    names.append("bhh")

    # weightsFile = open('weights', 'w')
    # printWeights(weightsFile, pureQLearnAgent.weights)
    # weightsFile.close()

    probabilitiesFile = open('probabilities', 'w')
    printProbabilities(probabilitiesFile, bayesAgent.localConditionalProbabilities)
    probabilitiesFile.close()

    for i, agents in enumerate(agentses):
        name = names[i]

        d[name] = 0.0
        if not path.exists(path.join('data', name)):
            os.makedirs(path.join('data', name))

        for j in range(numGames):
            victory = playGame(True, agents, 'data/'+name+'/gameData'+str(j), False)
            if victory:
                d[name] += 1

        d[name] = d[name]/numGames

    return d

def printWeights(weightsFile, weights):
    for k, v in weights.iteritems():
        print >>weightsFile, str(k) + ' --> ' + str(v)

def printProbabilities(file, probabilities):
    for maxBidCount, nestedArray in enumerate(probabilities):
        for handCount, counter in enumerate(nestedArray):
            for (verb, actionCount), prob in counter.iteritems():
                print >>file, 'maxBidCount: %d, handCount: %d, verb: %s, actionCount: %d, probability: %f' % (
                    maxBidCount, handCount, verb, actionCount, prob
                )

#playGame(True, 'data/gameData.txt')
#print playGame(True, [HonestProbabilisticAgent(0), HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)])

# d = simulateGames(5000)
# print d
simulateGames(1)