"Game playing with incomplete information: Two learning agents for Liar’s Dice" - materials for CS221 submission

code.zip
--------
+ liarsdice.py: Game run functionality (game state description)
+ agents.py: All agent objects -> testing (Dummy, Baseline, Oracle), AI (Q-learners, Bayesian) and feature templates
+ run.py: Specific testing code including weight vector logging
+ performance.py: Performance testing for scenarios described write-up + hyperparameter tuning. Toggle game-play scenarios at the end of this file to output data for plotting in liarsDicePerformance.Rmd
+ liarDicePerformance.Rmd: Game data analysis (output from performance.py) and plotting. Fix file-path (setwd()) at beginning of file and run code blocks to output plots.

data.zip
--------
+ generalPerformance.csv: Performance tests - AI agents trained against true opponent sets (data in fig. 3 and table 2)
+ QsPerformance.csv: Q-learner match-up. Qlearners trained on separate oracles (data in fig.4)
+ oracleTrainedGenPerformance.csv: Additional experimental runs (all agents trained against orcles) - not inlcuded in write-up

Also see our github repo: https://github.com/benpeloquin7/liars_dice