import random
import numpy
import matplotlib.pyplot as plt
from scipy import stats
import collections
from liarsdice import *
from agents import *


def simulateGame(competitors=None):
	"""
	:param agents:  Agent set
	:return:        Boolean if our agent won
	"""
	if competitors is None:
		competitors = [HumanAgent(i) for i in range(NUM_PLAYERS)]

	gameState = InitialGameState([INITIAL_NUM_DICE_PER_PLAYER] * NUM_PLAYERS, random.randint(0, NUM_PLAYERS - 1))
	while not gameState.isGameOver():
		agent = competitors[gameState.getCurrentPlayerIndex()]
		chosenAction = agent.chooseAction(gameState)
		gameState = gameState.generateSuccessor(chosenAction)

	return gameState.isWin(0)

def simulateNGames(numGames=30, competitors=None, verbose=False):
	"""
	Simulate numGames given some competitorSet
	Returns tuple competitor set string and win %
	"""
	gameData = []
	competitorStr, allCompetitors = competitors
	if verbose: print("simulating " + str(numGames) + " games...")

	for i in range(numGames):
		if verbose:
			print i
		gameData.append(simulateGame(allCompetitors))

	return (competitorStr, float(sum(gameData)) / numGames)

def competitorSet(competitors="qhh", featureExtractor=None, exploreProb=None, discount=None, numIters = 2500):
	"""
	:param competitors:         Competitor set string acronym
	:param featureExtractor:    Q-learning feature set
	:param exploreProb:         Q-learning gamma
	:param discount:            Q-learning discount
	:param numIters:            Q-learning training iterations
	:return:                    Competitor set string and agent objects
	"""
	# Populate player set
	agentses = []
	for i, agent in enumerate(competitors.lower()):
		if agent == "q":
			pureQLearnAgent = PureQLearningAgent(i, featureExtractor, exploreProb, discount)
			agentses.append(pureQLearnAgent)
		elif agent == "h":
			agentses.append(HonestProbabilisticAgent(i))
		elif agent == "r":
			agentses.append(RandomAgent(i))
		elif agent == "o":
			agentses.append(OracleAgent(i))
		else:
			return "Error: " + agent + " is not a valid agent"

	# Train Q-learned agents (potentially multiple - this needs to be built out)
	for i, agent in enumerate(agentses):
		if isinstance(agent, PureQLearningAgent):
			opponents = agentses[:i]+agentses[i+1:]
			agent.learn(numIters, opponents)

	return (competitors, agentses)

def collectData(sampleSize=30, numberOfSamples=50, competitors=None, verbose=True):
	"""
	:param sampleSize:          Sample size of win % estimates
	:param numberOfSamples:     Number of samples we want
	:param competitors:         Competitor set
	:return:                    List of tuples [("competitorSet", win%)...]
	"""

	if verbose: print("Collecting " + str(numberOfSamples) + " estimates with sample size " + str(sampleSize))
	data = []
	for _ in range(numberOfSamples):
		data.append(simulateNGames(sampleSize, competitors))
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
					competitorStr="qhh", \
					numIters=100, \
					featureExtractor = featureExtractor1, \
					verbose=True):
	"""

	:param exploreProbRange: 	epsilon range (will be divided by 100)
	:param discountRange:  		gamma range (will be divided by 10)
	:param competitorStr: 		specify competitors
	:param numIters: 			number of Q-learning iterations
	:param featureExtractor: 	feature extractor we're exploring
	:param verbose: 			print stuff
	:return: 					list of tuples [(win%, epsilon, gamma)...]
	"""

	if verbose:
		print "Tuning exploreProb and discount..."

	paramData = []
	for epsilon in exploreProbRange:
		for gamma in discountRange:
			epsilonReal = float(epsilon) / 100
			gammaReal = float(gamma) / 10
			if verbose:
				print("Tuning q with epsilon=" + str(epsilonReal) + " and gamma=" + str(gammaReal) + " for numIters=" + str(numIters) + "...")
			# Get competitor set
			comps = competitorSet("qhh", featureExtractor, exploreProb=epsilonReal, discount=gammaReal, numIters = numIters)
			# Collect data - numberOfSamples (batch size) = 1 to speed things up
			paramData.append((calcMean(extractScores(collectData(competitors=comps, sampleSize=100, numberOfSamples=1))), epsilonReal, gammaReal))
	return paramData

# Generic mean and variance (may need to calc var some other way?)
# ----------------------------------------------------------------
competitors = ["qrr", "qhh", "qoo", "hrr", "hoo", "ohh", "orr"]
means = []
vars = []
for c in competitors:
	comps = competitorSet(c, featureExtractor1, exploreProb=0.05, discount=0.3, numIters=2500)
	data = collectData(competitors = comps, sampleSize=30, numberOfSamples=100)
	scores = extractScores(data)
	mu = calcMean(scores)
	means.append(mu)
	var = calcVariance(scores)
	vars.append(var)
	print "-------------------"
	print c
	print("average win %: " + str(mu) + " variance: " + str(var))


# Plotting
# --------
# plt.hist(extractScores(data), 100, normed=1, facecolor='green', alpha=0.75)
# plt.show()

# bar plots for win %
n_groups = 7
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
# params =  tuneHyperParams(exploreProbRange=range(1, 11), discountRange=range(0, 11))
# print params