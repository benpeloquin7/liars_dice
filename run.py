from liarsdice import *
from agents import *

# Main game play

# while num players is more than one
# Counter of number of players?

def playGame():
    agents = [HumanAgent(i) for i in range(NUM_PLAYERS)]
    gameState = InitialGameState([INITIAL_NUM_DICE_PER_PLAYER] * NUM_PLAYERS, 0)
    while not gameState.isGameOver():
        print '----------------------------------\n'
        print str(gameState)

        agent = agents[gameState.getCurrentPlayerIndex()]
        chosenAction = agent.chooseAction(gameState)
        gameState = gameState.generateSuccessor(chosenAction)

    for i in range(NUM_PLAYERS):
        if gameState.isWin(i):
            print '----------------------------------\n'
            print 'Player %d won!'

playGame()