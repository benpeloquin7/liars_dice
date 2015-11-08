from liarsdice import *

class Agent:
    def chooseAction(self, gameState):
        raise Exception('abstract')

class HumanAgent:
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def chooseAction(self, gameState):
        possibleActions = gameState.getLegalActions()
        actionString = input('Player %d, Enter your action: ' % self.agentIndex)
        while True:
            # parse the action
            action = tuple(actionString.split()) + (self.agentIndex, )
            if action in possibleActions:
                return action

            actionString = input('That is not a legal action. Player %d, Try again: ' % self.agentIndex)