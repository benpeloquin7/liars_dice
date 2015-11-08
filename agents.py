from liarsdice import *

class Agent:
    def chooseAction(self, gameState):
        raise Exception('abstract')

class HumanAgent:
    def __init__(self, agentIndex):
        self.agentIndex = agentIndex

    def chooseAction(self, gameState):
        def validateActionFormat(actionParts):
            if len(actionParts) != 3:
                return False
            if actionParts[0] not in ('bid', 'confirm', 'deny'):
                return False
            if not actionParts[1].isdigit() or not actionParts[2].isdigit():
                return False
            return True

        possibleActions = gameState.getLegalActions()
        actionString = raw_input('Player %d, Enter your action: ' % self.agentIndex)
        while True:
            # parse the action
            actionParts = actionString.split()
            if validateActionFormat(actionParts):
                verb, value, count = actionParts
                action = verb, int(value), int(count), self.agentIndex

                if action in possibleActions:
                    return action

            actionString = raw_input('That is not a legal action. Player %d, Try again: ' % self.agentIndex)