################################################################################################
################################################################################################
# Unit tests for basic functionality
from liarsdice import *
import random


numDicePerPlayer = [3, 3, 3]
currPlayerIndex = 2

def testIG_InitalGameStateAttributes():
	"""
	general test of InitialGameStateAttributes
	"""
	for _ in range(10):
		numPlayers = NUM_PLAYERS
		numDiceInit = random.randint(1, 3)
		numDicePerPlayer = [numDiceInit for _ in range(numPlayers)]
		currPlayerIndex = random.randint(1, numPlayers)
		igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
		# print("igs.numDicePerPlayer: ", igs.numDicePerPlayer)
		# print("igs.bid: ", igs.bid) 
		# print("igs.currentPlayerIndex: ", igs.currentPlayerIndex)
		# print("igs.numDicePerPlayer: ", igs.numDicePerPlayer)
		assert len(igs.numDicePerPlayer) == numPlayers
		assert igs.bid == None
		assert igs.currentPlayerIndex == currPlayerIndex
		assert igs.numDicePerPlayer == numDicePerPlayer
	print("pass --> IntialGameState attributes")

def testIG_getLegalActions():
	"""
	tests InitialGameState.getLegalACtions() 
	Note: actionTuple contians ('verb', value, count, curr_player_index)
	"""
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	# Check consistency for all legal actions
	assert all([actionTuple[0] == 'bid' and
					(actionTuple[1] > 0 and actionTuple[1] <= 6) and
					(actionTuple[2] > 0 and actionTuple[2] <= (numDicePerPlayer[0] * len(numDicePerPlayer)))
					for actionTuple in igs.getLegalActions()])
	print("pass --> InitialGameState.getLegalACtions()")

def testIG_generateSucc():
	"""
	tests InitialGameState.generateSuccessor(action)
	"""
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	# Index 0 player
	action = ("bid", 2, 2, 0)
	succ = igs.generateSuccessor(action)
	assert isinstance(succ, GameState)
	assert isinstance(succ, MedialGameState)
	assert succ.hands == igs.hands
	# Check that we move to next player
	assert succ.currentPlayerIndex == igs.getNextPlayer()

	# Index final player
	action = ("bid", 4, 1, 2)
	succ = igs.generateSuccessor(action)
	assert isinstance(succ, GameState)
	assert isinstance(succ, MedialGameState)
	assert succ.hands == igs.hands
	# Check that we move to next player
	assert succ.currentPlayerIndex == igs.getNextPlayer()
	try:
		igs.generateSuccessor(("bad", 2, 2, 1))
	except AssertionError:
		pass
		# print "Correctly asserting 'bad' action"
	print("pass --> InitialGameState.generateSuccessor(action)")

def testIG_isLose():
	"""
	tests InitialGameState.isLose(index)
	"""
	numDicePerPlayer = [0, 0, 1]
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	assert igs.isLose(0) == True
	assert igs.isLose(1) == True
	assert igs.isLose(2) == False
	numDicePerPlayer = [0, 0, 0]
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	assert igs.isLose(2) == True
	print("pass --> InitialGameState.isLose(index)")

def testIG_isWin():
	"""
	tests InitialGameState.isWin(index)
	"""
	numDicePerPlayer = [4, 3, 4]
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	assert not all([igs.isWin(player) for player in range(len(numDicePerPlayer))])
	numDicePerPlayer = [0, 1, 0]
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	assert igs.isWin(1) and not (igs.isWin(0) or igs.isWin(2))
	print("pass --> InitialGameState.isWin(index)")

# InitalGamestate tests (IG)
# --------------------------
testIG_InitalGameStateAttributes()
testIG_getLegalActions()
testIG_generateSucc()
testIG_isLose()
testIG_isWin()



# mgs = igs.generateSuccessor(igs.getLegalActions()[0])
# igs.isWin(0)

# print mgs.getLegalActions()[0]
# mgs.generateSuccessor(mgs.getLegalActions()[0]).isWin(2)