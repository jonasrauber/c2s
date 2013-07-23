"""
Averages responses over multiple experiments with different training/validation splits.
"""

import sys

sys.path.append('./code')

from argparse import ArgumentParser
from glob import glob
from numpy import corrcoef, vstack, hstack, std, mean, sqrt
from scipy.io import loadmat, savemat
from tools import Experiment
from cmt.models import GLM, STM

cells = [5, 7, 48, 19, 50, 12, 17, 18, 28]

def main(argv):
	parser = ArgumentParser(argv[0], description=__doc__)
	parser.add_argument('--model', '-m', type=str, default='STM')

	args = parser.parse_args(argv[1:])

	files = glob('results/predictions.*.xpck')

	# load data
	data = loadmat('data/data.mat')['Data'].ravel()

	outputs = []
	outputs_test = []

	for i in range(data.shape[0]):
		outputs.append(data[i][1].reshape(1, -1))

		if i + 1 not in cells:
			outputs_test.append(outputs[-1])

	# load predictions
	predictions = [[] for _ in range(data.shape[0])]
	predictions_test = [[] for _ in range(data.shape[0] - len(cells))]

	model_type = GLM if args.model.upper() == 'GLM' else STM

	for filepath in files:
		results = Experiment(filepath)

		if isinstance(results['model'], model_type):
			for i in range(len(predictions)):
				predictions[i].append(results['predictions'][i])

			for i in range(len(predictions_test)):
				predictions_test[i].append(results['predictions_test'][i])

	corr = []
	corr_test = []

	# average predictions and compute correlations
	for i in range(len(predictions)):
		predictions[i] = mean(vstack(predictions[i]), 0).reshape(1, -1)
		corr.append(corrcoef(outputs[i], predictions[i])[0, 1])

	for i in range(len(predictions_test)):
		predictions_test[i] = mean(vstack(predictions_test[i]), 0).reshape(1, -1)
		corr_test.append(corrcoef(outputs_test[i], predictions_test[i])[0, 1])

	sem      = std(corr) / sqrt(len(corr))
	sem_test = std(corr_test) / sqrt(len(corr_test))

	print 'Correlation of average response:'
	print '\t{0:.5f} (test)'.format(mean(corr_test))
	print '\t{0:.5f} (total)'.format(mean(corr))

	savemat('results/predictions.{0}.mat'.format(args.model.lower()), {'predictions': predictions},
		oned_as='row', do_compression=True)

	return 0



if __name__ == '__main__':
	sys.exit(main(sys.argv))