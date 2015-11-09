from liarsdice import *
from agents import *

# Main game play

# while num players is more than one
# Counter of number of players?

def playGame(firstAgentOnly, logFilePath = None):
    agents = [HumanAgent(i) for i in range(NUM_PLAYERS)]
    gameState = InitialGameState([INITIAL_NUM_DICE_PER_PLAYER] * NUM_PLAYERS, 0)
    logFile = open(logFilePath, 'w') if logFilePath is not None else None
    log(logFile, '----------------------------------\nGame 1:')
    while not gameState.isGameOver():
        print '----------------------------------\n'
        print str(gameState)
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
            break


    for i in range(NUM_PLAYERS):
        if gameState.isWin(i):
            print '----------------------------------\n'
            print 'Player %d won!' % i

    if gameState.isWin(0):
        log(logFile, '\nAgent 0 won')

    logFile.close()

def log(logFile, text):
    if logFile is not None:
        print >>logFile, text

playGame(True, 'gameData.txt')