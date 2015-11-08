################################################################################################
################################################################################################
# Unit tests for basic functionality
from liarsdice import *
from collections import Counter
import random


numDicePerPlayer = [3, 3, 3]
currPlayerIndex = 0

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

def testMG_MedialGameStateAttributes():
	"""
	general MedialGameState attributes
	"""
	# medial state from initial state
	currPlayerIndex = 0
	igs = InitialGameState(numDicePerPlayer, currPlayerIndex)
	mgs = igs.generateSuccessor(igs.getLegalActions()[0])
	assert mgs.hands == igs.hands
	assert mgs.currentPlayerIndex == igs.getNextPlayer()
	assert mgs.numDicePerPlayer == igs.numDicePerPlayer
	assert mgs.bid != None

	# medial state initialzied in isolation
	currPlayerIndex = 2
	hands = [Counter(random.randint(1,DICE_SIDES)\
				for _ in range(numDice))\
					for numDice in numDicePerPlayer]
	mgs = MedialGameState(numDicePerPlayer, hands, currPlayerIndex, "bid")
	assert len(mgs.numDicePerPlayer) > 0
	assert mgs.bid != None
	assert mgs.currentPlayerIndex == currPlayerIndex
	assert len(mgs.hands) ==  len(numDicePerPlayer)
	#numDicePerPlayer, hands, currentPlayerIndex, bid)
	print("pass --> MedialGameState attributes")

def testMG_getLegalActions():
	"""
	general MedialGameState attributes
	Note: actionTuple contians ('verb', value, count, curr_player_index)
	"""
	currPlayerIndex = 2
	hands = [Counter(random.randint(1,DICE_SIDES)\
				for _ in range(numDice))\
					for numDice in numDicePerPlayer]
	mgs = MedialGameState(numDicePerPlayer, hands, \
							currPlayerIndex, ("deny", 2, 3, 1))
	# print mgs.getLegalActions()
	# Check that 'confirms' and 'denys' always match prev 'bid' data
	assert [action[1] == mgs.bid[1] and\
			action[2] == mgs.bid[2] and\
			action[3] == mgs.bid[3]\
			for action in mgs.getLegalActions()\
				if (action[0] == "confirm" or action[0] == "deny")]
	# Check that future bids always involve a count greater than the prev bid
	assert [action[2] > mgs.bid[2] for action in mgs.getLegalActions() if action[0] == "bid"]
	print("pass --> MedialGameState.getLegalActions()")

	
def testMG_generateSuccessor():
	"""
	test MedialGameState.generateSuccesor()
	"""
	currPlayerIndex = 2  	# starting at last player
	hands = [Counter(random.randint(1,DICE_SIDES)\
				for _ in range(numDice))\
					for numDice in numDicePerPlayer]
	
	mgs = MedialGameState(numDicePerPlayer, hands, \
							currPlayerIndex, ("bid", 2, 3, 1))
	print "mgs.currentPlayerIndex:", mgs.currentPlayerIndex
	print "mgs.hands\n", mgs.hands
	print "mgs bid (\"bid\", 3, 3, 2)"
	succ1 = mgs.generateSuccessor(("bid", 3, 3, mgs.currentPlayerIndex))
	print "succ1.currentPlayerIndex:", succ1.currentPlayerIndex
	print "succ1.hands\n", succ1.hands
	print "succ1 bid (\"deny\", 3, 3, 2))"
	succ2 = succ1.generateSuccessor(("deny", 3, 3, succ1.currentPlayerIndex))
	print "succ2.currentPlayerIndex:", succ2.currentPlayerIndex
	print "succ2.hands\n", succ2.hands

	# check we've incremented player
	# print "succ.currentPlayerIndex", succ.currentPlayerIndex
	# print "mgs.currentPlayerIndex", mgs.currentPlayerIndex
	assert succ1.currentPlayerIndex == mgs.getNextPlayer()
	assert succ1.bid[0] == "bid"
	assert succ1.bid == ("bid", 3, 3, mgs.currentPlayerIndex)


# MutualGamestate tests (MG)
# --------------------------
testMG_generateSuccessor()
# testMG_MedialGameStateAttributes()
# testMG_getLegalActions()

# InitalGamestate tests (IG)
# --------------------------
# testIG_InitalGameStateAttributes()
# testIG_getLegalActions()
# testIG_generateSucc()
# testIG_isLose()
# testIG_isWin()

# mgs = igs.generateSuccessor(igs.getLegalActions()[0])
# igs.isWin(0)

# print mgs.getLegalActions()[0]
# mgs.generateSuccessor(mgs.getLegalActions()[0]).isWin(2)