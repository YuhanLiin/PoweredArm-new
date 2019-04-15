import numpy as np
from classifier.classifier import LinearClassifier, sigmoid

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

def test_sanity_predict():
    hyp = np.array([[5, 1., 2., 3., 4.],
                    [1000, 4., 3., 2., 1.]])
    classifier = LinearClassifier(num_classes=2, num_features=4, init_hyp=hyp)
    result = classifier.predict(np.array([1., 2., 3., 4.]))
    assert result == 1

def test_sanity_cost():
    hyp = np.array([[1, 1],
                    [3, 5]])
    classifier = LinearClassifier(num_classes=2, num_features=1, init_hyp=hyp)
    X = np.array([[1, 3],
                  [1, 0],
                  [1, -4]])
    y = np.array([1, 0, 1]).reshape(-1, 1)
    cost = classifier.cost(X, y)
    assert (np.isclose(cost, np.array([1.45999966, 6.68286247]))).all()

def test_sanity_cost_delta():
    hyp = np.array([[1, 1],
                    [3, 5]])
    classifier = LinearClassifier(num_classes=2, num_features=1, init_hyp=hyp)
    X = np.array([[1, 3],
                  [1, 0],
                  [1, -4]])
    y = np.array([1, 0, 1]).reshape(-1, 1)
    delta = classifier.cost_delta(X, y)
    assert (np.isclose(
        delta,
        np.array([[0.76049824, -0.04742585],
                 [2.75633788,  3.99999979]])
    )).all()
    

