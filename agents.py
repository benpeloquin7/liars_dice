from liarsdice import *

class Agent:
    def chooseAction(self, gameState):
        raise Exception('abstract')

class HumanAgent:
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