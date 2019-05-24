from os import path
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from poweredarm.classifier import LinearClassifier
from poweredarm.data_processing import (aggregate_csv, create_dataset)
from poweredarm.util import dated_name, Gesture

def visualize_relationships(X):
    for i in range(8):
        for j in range(i+1, 8):
            plt.plot(X[:, i], X[:, j], 'b.')
            plt.title('{} vs {}'.format(i, j))
            plt.show()

def evaluate_linear_classifier(classifier_file, data_files):
    classifier = LinearClassifier.load(classifier_file)
    data = aggregate_csv(data_files)
    X, y = create_dataset(data, [])
    #visualize_relationships(X)

    acc, recalls = classifier.evaluate(X, y)
    return acc, recalls

def train_linear_classifier(data_files, save=False, show_graphs=False):
    data = aggregate_csv(data_files)
    # 80-20 data split
    X, y, Xtest, ytest = create_dataset(data, [0.8])

    classifier = LinearClassifier(num_classes=len(Gesture), num_features=8)

    costs = classifier.train(X, y, rate=0.02, num_iter=1500)

    if show_graphs:
        plt.ioff()

        iters = np.arange(costs.shape[0])
        plt.plot(iters, costs)
        plt.title('Cost fn')
        plt.xlabel('# of iterations')
        plt.ylabel('Value of cost fn')
        plt.legend(['Class {}'.format(n) for n in range(costs.shape[1])])
        plt.show()

    acc, recalls = classifier.evaluate(Xtest, ytest)
    if save:
        cls_file = path.join( 'data', 'classifiers',
                dated_name('lin-cls-{:.5g}'.format(acc * 100)))
        print('Save classifier to {}'.format(cls_file))
        classifier.save(cls_file)

    return acc, recalls
