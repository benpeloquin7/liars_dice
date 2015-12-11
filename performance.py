import random
import numpy
import matplotlib.pyplot as plt
from scipy import stats
import collections
from liarsdice import *
from agents import *
import csv


def simulateGame(allPlayers=None):
	"""
	:param allPlayers:  Agent set
	:return:        	Boolean if our agent won
	"""
	if allPlayers is None:
		allPlayers = [HumanAgent(i) for i in range(NUM_PLAYERS)]

	gameState = InitialGameState([INITIAL_NUM_DICE_PER_PLAYER] * NUM_PLAYERS, random.randint(0, NUM_PLAYERS - 1))
	while not gameState.isGameOver():
		agent = allPlayers[gameState.getCurrentPlayerIndex()]
		chosenAction = agent.chooseAction(gameState)
		gameState = gameState.generateSuccessor(chosenAction)

	return gameState.isWin(0)

def simulateNGames(numGames=30, allPlayers=None, verbose=False):
	"""
	Simulate numGames given some competitorSet
	Returns tuple competitor set string and win %
	"""
	gameData = []
	playerStr, playerObjects = allPlayers
	if verbose: print("simulating " + str(numGames) + " games...")

	for i in range(numGames):
		if verbose:
			print i
		gameData.append(simulateGame(playerObjects))

	return (playerStr, sum(gameData))

def playerSet(allPlayers="qhh", featureExtractors=None, exploreProb=None, discount=None, numIters=100):
	"""
	:rtype: object
	:param allPlayers:         	Player set string acronym
	:param featureExtractors:   List of Q-learning feature set
	:param exploreProb:         Q-learning gamma
	:param discount:            Q-learning discount
	:param numIters:            Q-learning training iterations
	:return:                    Competitor set string and agent objects
	"""
	# Tuned exploreProb and discount
	# index [0] is tuning for feature extractor 1 (exploreProb=0.05, discount=0.5)
	# index [1] is tuning for feature extractor 2 (exploreProb=0.08, discount=0.8)
	tunedExploreProb = [0.05, 0.08]
	tunedDiscount = [0.5, 0.8]

	# Check for feature type in players string
	if "_" in allPlayers:
		extractorNum = int(allPlayers.split("_")[1]) - 1

	# Populate player set
	agentses = []
	for i, agent in enumerate(allPlayers.lower()):
		if agent == "q":
			# If exploreProb and discount are passed in (probably bc we're tuning)
			if exploreProb != None and discount != None:
				pureQLearnAgent = PureQLearningAgent(i, featureExtractors[extractorNum],\
												 exploreProb, discount)
			else:
				# Else used tuned params
				pureQLearnAgent = PureQLearningAgent(i, featureExtractors[extractorNum],\
													 tunedExploreProb[extractorNum], tunedDiscount[extractorNum])
			agentses.append(pureQLearnAgent)
		elif agent == "h":
			agentses.append(HonestProbabilisticAgent(i))
		elif agent == "r":
			agentses.append(RandomAgent(i))
		elif agent == "o":
			agentses.append(OracleAgent(i))
		elif agent == "b":
			bayesAgent = BayesianAgent(i)
			agentses.append(bayesAgent)
		# else:
		# 	return "Error: " + agent + " is not a valid agent"

	# Learn with correct opponent sets
	for i, agent in enumerate(agentses):
		# Q-learned training
		if isinstance(agent, PureQLearningAgent):
			opponents = agentses[:i]+agentses[i+1:]
			agent.learn(numIters, opponents)
		# Bayesian training
		if isinstance(agent, BayesianAgent):
			opponents = agentses[:i]+agentses[i+1:]
			# Bayesian agent observes 3 agents - add appropriate third agent for learning
			if isinstance(opponents[0], RandomAgent):
				opponents.append(RandomAgent(2))
			elif isinstance(opponents[0], HonestProbabilisticAgent):
				opponents.append(HonestProbabilisticAgent(2))
			elif isinstance(opponents[0], OracleAgent):
				opponents.append(OracleAgent(2))

			agent.learn(numIters, opponents)

			# agent.learn(numIters, [OracleAgent(opponents[0].agentIndex),
			#             OracleAgent(opponents[1].agentIndex)])

	return (allPlayers, agentses)

def collectData(sampleSize=30, numberOfSamples=50, allPlayers=None, verbose=True):
	"""
	:param sampleSize:          Sample size of win % estimates
	:param numberOfSamples:     Number of samples we want
	:param allPlayers:         	Player set
	:return:                    List of tuples [("competitorSet", win%)...]
	"""

	if verbose: print("Collecting " + str(numberOfSamples) + " estimates with sample size " + str(sampleSize))
	data = []
	for _ in range(numberOfSamples):
		data.append(simulateNGames(sampleSize, allPlayers))
	return data

def calcMean(data):
	"""
	:param data:    List of tuples [("compStr", winPercentage)...]
	:return:        sample mean
	"""
	return numpy.mean(data)

def calcVariance(data):
	"""
	:param data:    List of win %'s
	:return:        sample variance
	"""
	return numpy.var(data)

def extractScores(data):
	"""
	:param data:    List of competitor win% tuples [('competitorSet', win%)...]
	:return:        list of win%'s
	"""
	d = [obs[1] for obs in data]
	return d

def tuneHyperParams(exploreProbRange=range(1, 10), \
					discountRange=range(0, 11), \
					allPlayers="qhh", \
					numIters=100, \
					extractorNum = 1, \
					verbose=True):
	"""

	:param exploreProbRange: 		epsilon range (will be divided by 100)
	:param discountRange:  			gamma range (will be divided by 10)
	:param competitorStr: 			specify competitors
	:param numIters: 				number of Q-learning iterations
	:param featureExtractorIndex: 	feature extractor to use (1 or 2)
	:param verbose: 				print stuff
	:return: 						list of tuples [(win%, epsilon, gamma)...]
	"""
	if verbose:
		print "Tuning exploreProb and discount..."
	featureExtractors = [featureExtractor1, featureExtractor2]
	paramData = []
	for epsilon in exploreProbRange:
		for gamma in discountRange:
			epsilonReal = float(epsilon) / 100
			gammaReal = float(gamma) / 10
			if verbose:
				print("Tuning q with epsilon=" + str(epsilonReal) + " and gamma=" + str(gammaReal) + " for numIters=" + str(numIters) + "...")
			# Get competitor set
			players = playerSet(allPlayers, featureExtractors=featureExtractors, exploreProb=epsilonReal, discount=gammaReal, numIters=numIters)
			# Collect data - numberOfSamples (batch size) = 1 to speed things up
			paramData.append((calcMean(extractScores(collectData(allPlayers=players, sampleSize=100, numberOfSamples=1))), epsilonReal, gammaReal))
	return paramData


# General performance data
# ------------------------
# games= ['hrr', 'hhh', 'hoo', 'qrr', 'qhh', 'qoo', 'brr', 'bhh', 'boo']
# games = ["brr", "bhh", "boo"]
runGeneralPerformance = False
if runGeneralPerformance:
	games = ["qrr_1", "qhh_1", "qoo_1", "qrr_2", "qhh_2", "qoo_2", "brr", "bhh", "boo"]
	featureExtractors = [featureExtractor1, featureExtractor2]
	data = []
	for i, game in enumerate(games):
		print "game #" + str(i + 1) + " out of " + str(len(games))
		allPlayers = playerSet(game, featureExtractors=featureExtractors, exploreProb=None, discount=None, numIters=2500)
		data.extend(collectData(allPlayers=allPlayers, sampleSize=100, numberOfSamples=100))
	# Output to .csv
	with open('generalPerformance.csv','w') as out:
			csv_out = csv.writer(out)
			csv_out.writerow(['game','wins'])
			for row in data:
				csv_out.writerow(row)


# Specific tests - Q-learners
# Q1 trained on Oracle vs Q2 trained on oracle
# Note: Need to set NUM_Players = 2 in in liarsdice.py !!!!
# ---------------------------------------------------------
runQLearnerMatchUp = False
if runQLearnerMatchUp:
	# NUM_PLAYERS = 2
	# Learn
	Q1 = PureQLearningAgent(0, featureExtractor1, exploreProb=0.05, discount=0.5)
	opponents1 = [OracleAgent(1)]
	Q1.learn(2500, opponents1 )
	Q2 = PureQLearningAgent(0, featureExtractor2, exploreProb=0.08, discount=0.8)
	opponents2 = [OracleAgent(1)]
	Q2.learn(2500, opponents2)

	# Q1 gets index 0
	Q2.agentIndex = 1
	allPlayers = ("q1q2", [Q1, Q2])
	data=[]
	data.extend(collectData(allPlayers=allPlayers, sampleSize=100, numberOfSamples=100))
	# Q2 gets index 0
	Q1.agentIndex = 1
	Q2.agentIndex = 0
	allPlayers = ("q2q1", [Q2, Q1])
	data.extend(collectData(allPlayers=allPlayers, sampleSize=100, numberOfSamples=100))
	# Output to .csv
	with open('QsPerformance.csv','w') as out:
			csv_out = csv.writer(out)
			csv_out.writerow(['game','wins'])
			for row in data:
				csv_out.writerow(row)

# Specific tests - Gen test but with TRAINING ON ORACLES
# ------------------------------------------------------
runGenTrainOnOracles = False
if runGenTrainOnOracles:
	# Training
	# --------
	data = []

	# Q1
	Q1 = PureQLearningAgent(0, featureExtractor1, exploreProb=0.05, discount=0.5)
	opponents = [OracleAgent(1), OracleAgent(2)]
	Q1.learn(2500, opponents)
	data.extend(collectData(allPlayers=("qrr_1", [Q1, RandomAgent(1), RandomAgent(2)]), sampleSize=100, numberOfSamples=100))
	data.extend(collectData(allPlayers=("qhh_1", [Q1, HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)]), sampleSize=100, numberOfSamples=100))
	data.extend(collectData(allPlayers=("qoo_1", [Q1, OracleAgent(1), OracleAgent(2)]), sampleSize=100, numberOfSamples=100))

	# Q2
	Q2 = PureQLearningAgent(0, featureExtractor1, exploreProb=0.08, discount=0.8)
	Q2.learn(2500, opponents)
	data.extend(collectData(allPlayers=("qrr_2", [Q2, RandomAgent(1), RandomAgent(2)]), sampleSize=100, numberOfSamples=100))
	data.extend(collectData(allPlayers=("qhh_2", [Q2, HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)]), sampleSize=100, numberOfSamples=100))
	data.extend(collectData(allPlayers=("qoo_2", [Q2, OracleAgent(1), OracleAgent(2)]), sampleSize=100, numberOfSamples=100))

	# Bayesian
	B_agent = BayesianAgent(0)
	opponents.append(OracleAgent(0)) # Add another oracle (because Bayesian observes three)
	B_agent.learn(2500, opponents)
	data.extend(collectData(allPlayers=("brr", [B_agent, RandomAgent(1), RandomAgent(2)]), sampleSize=100, numberOfSamples=100))
	data.extend(collectData(allPlayers=("bhh", [B_agent, HonestProbabilisticAgent(1), HonestProbabilisticAgent(2)]), sampleSize=100, numberOfSamples=100))
	data.extend(collectData(allPlayers=("boo", [B_agent, OracleAgent(1), OracleAgent(2)]), sampleSize=100, numberOfSamples=100))

	# Output to .csv
	with open('oracleTrainedGenPerformance.csv','w') as out:
			csv_out = csv.writer(out)
			csv_out.writerow(['game','wins'])
			for row in data:
				csv_out.writerow(row)




# # Output to .csv - GENERIC CODE
# # ------------------------------
# write_to_csv = True
# if write_to_csv:
# 	with open('generalPerformance.csv','w') as out:
# 		csv_out = csv.writer(out)
# 		csv_out.writerow(['game','wins'])
# 		for row in data:
# 			csv_out.writerow(row)



# Plotting
# --------
# plt.hist(extractScores(data), 100, normed=1, facecolor='green', alpha=0.75)
# plt.show()

# bar plots for win %
plot = False
if plot:
	n_groups = len(games)
	bar_width = 0.4
	opacity = 0.4
	index = numpy.arange(n_groups)
	rects1 = plt.bar(index, means, bar_width, \
					 alpha=opacity, \
					 color='b', \
					 yerr=vars)
	plt.xticks(index + bar_width, competitors)
	plt.show()

# Tune hyperparameters
# ---------------------
shouldTune = False
if shouldTune:
	params =  tuneHyperParams(allPlayers="qhh_2", exploreProbRange=range(1, 11), discountRange=range(0, 11), numIters=1000)
	print params
	print max(params)