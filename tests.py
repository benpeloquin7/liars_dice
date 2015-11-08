################################################################################################
################################################################################################
# Unit tests for basic functionality
from liarsdice import *

igs = InitialGameState([2, 2, 2], 0)
assert igs.hands == 
mgs = igs.generateSuccessor(igs.getLegalActions()[0])
igs.isWin(0)

print mgs.getLegalActions()[0]
mgs.generateSuccessor(mgs.getLegalActions()[0]).isWin(2)