from os import path
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from poweredarm.classifier import LinearClassifier, QuadraticClassifier
from poweredarm.data_processing import (aggregate_csv, create_dataset)
from poweredarm.util import dated_name, NUM_CLASSES, NUM_FEATURES

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

def plot_learning_curves(data_files):
    data = aggregate_csv(data_files)
    # 80-20 data split
    X, y, Xtest, ytest = create_dataset(data, [0.8])

    classifier = LinearClassifier(num_classes=NUM_CLASSES, num_features=NUM_FEATURES)

    accs = []
    for i in range(5, 2000):
        print("Learning curve data point {}".format(i))
        Xtrain = X[:i+1, :]
        ytrain = y[:i+1]
        classifier.train(Xtrain, ytrain, rate=0.001, num_iter=100)
        acc_train, _ = classifier.evaluate(Xtrain, ytrain)
        acc_test, _ = classifier.evaluate(Xtest, ytest)
        accs.append([acc_train, acc_test])

    plt.plot(np.arange(len(accs)), np.array(accs))
    plt.title('Learning curve')
    plt.xlabel('Size of training set')
    plt.ylabel('Accuracy')
    plt.legend(['Training set', 'Test set'])
    plt.show()

def train_classifier(data_files, cls, rate, num_iter, save=False, show_graphs=False):
    data = aggregate_csv(data_files)
    # 80-20 data split
    X, y, Xtest, ytest = create_dataset(data, [0.8])

    classifier = cls(num_classes=NUM_CLASSES, num_features=NUM_FEATURES)

    costs = classifier.train(X, y, rate=rate, num_iter=num_iter)

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

def train_linear_classifier(data_files, save=False, show_graphs=False):
    return train_classifier(data_files, LinearClassifier, 0.005, 2000, save, show_graphs)

def train_quadratic_classifier(data_files, save=False, show_graphs=False):
    return train_classifier(data_files, QuadraticClassifier, 0.005, 2000, save, show_graphs)
