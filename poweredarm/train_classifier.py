from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from poweredarm.classifier import LinearClassifier
from poweredarm.data_processing import (aggregate_csv, create_dataset)

def evaluate_linear_classifier(classifer_file, data_files):
    classifier = LinearClassifier.load(classifer_file)
    data = aggregate_csv(data_files)
    X, y = create_dataset(data, [])

    acc, recalls = classifier.evaluate(X, y)
    return acc, recalls

def train_linear_classifier(data_files, save=False, show_graphs=False):
    data = aggregate_csv(data_files)
    # 80-20 data split
    X, y, Xtest, ytest = create_dataset(data, [0.8])

    classifier = LinearClassifier(num_classes=4, num_features=8)

    costs = classifier.train(X, y, rate=0.02, num_iter=1200)

    if show_graphs:
        plt.ioff()

        iters = np.arange(costs.shape[0])
        plt.plot(iters, costs)
        plt.title('Cost fn')
        plt.xlabel('# of iterations')
        plt.ylabel('Value of cost fn')
        plt.show()

    acc, recalls = classifier.evaluate(Xtest, ytest)
    if save:
        cls_file = 'data/classifiers/lin-cls-{:%Y-%m-%d-%H:%m:%s}-{:.5g}'\
            .format(datetime.today(), acc * 100)
        print('Save classifier to {}'.format(cls_file))
        classifier.save(cls_file)

    return acc, recalls
