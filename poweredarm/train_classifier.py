import numpy as np
from poweredarm.classifier import LinearClassifier
from poweredarm.data_processing import (aggregate_csv, create_dataset)

def train_linear_classifier(data_files):
    data = aggregate_csv(data_files)
    # 80-20 data split
    (X, y), (Xtest, ytest) = create_dataset(data, [0.8])

    classifier = LinearClassifier(num_classes=4, num_features=8)
    
    costs = classifier.train(X, y, rate=0.01, num_iter=1000)
    print(costs)
    acc, recalls = classifier.evaluate(Xtest, ytest)
    print(recalls)
    print(acc)

import glob
train_linear_classifier(glob.glob('tests/data/*.csv'))
