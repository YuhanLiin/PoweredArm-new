import numpy as np
from classifier.classifier import LinearClassifier, sigmoid

def test_sanity_predict():
    classifier = LinearClassifier(num_classes=6, num_features=4)
    result = classifier.predict(np.array([1., 2., 3., 4.]))
    assert result == 0

def test_sanity_cost():
    classifier = LinearClassifier(num_classes=2, num_features=4)
    X = np.array([[1, 2, 4, 3, 5],
                  [1, 4, 5, 5, 10],
                  [1, 1, 1, 1, 1]])
    y = np.array([1, 0, 1]).reshape(-1, 1)
    classifier.cost(X, y)

def test_sigmoid():
    sig1 = 1 / (1 + np.exp(-1))
    sig2 = 1 / (1 + np.exp(-2))
    assert sigmoid(0) == .5
    assert sigmoid(1) == sig1
    assert (
        sigmoid(np.array([
            [0, 1], 
            [2, 0]])) ==
        np.array([
            [.5, sig1],
            [sig2, .5]])
    ).all()
