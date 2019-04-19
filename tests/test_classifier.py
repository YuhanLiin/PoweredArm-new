import numpy as np
from poweredarm.classifier import LinearClassifier, sigmoid

def test_sigmoid():
    sig1 = 1 / (1 + np.exp(-1))
    sig2 = 1 / (1 + np.exp(-2))
    assert sigmoid(0) == .5
    assert sigmoid(1) == sig1
    assert np.allclose(
        sigmoid(np.array([
            [0, 1],
            [2, 0]])),
        np.array([
            [.5, sig1],
            [sig2, .5]]))

def test_sanity_cost():
    hyp = np.array([[1, 1],
                    [3, 5]])
    classifier = LinearClassifier(num_classes=2, num_features=1, init_hyp=hyp.T)
    X = np.array([[1, 3],
                  [1, 0],
                  [1, -4]])
    y = np.array([1, 0, 1])
    cost = classifier.cost(X, y)
    np.allclose(cost, np.array([1.45999966, 6.68286247]))

def test_sanity_cost_delta():
    hyp = np.array([[1, 1],
                    [3, 5]])
    classifier = LinearClassifier(num_classes=2, num_features=1, init_hyp=hyp.T)
    X = np.array([[1, 3],
                  [1, 0],
                  [1, -4]])
    y = np.array([1, 0, 1])
    delta = classifier.cost_delta(X, y)
    np.allclose(
        delta,
        np.array([[0.76049824, -0.04742585],
                 [2.75633788,  3.99999979]])
    )

def test_gradient_descent():
    def compress(arr):
        return arr.sum(1).T

    hyp = np.array([[1, 3],
                    [0, 43],
                    [8, 10]]).T
    classifier = LinearClassifier(num_classes=3, num_features=1, init_hyp=hyp)
    costs = classifier.gradient_descent(lambda: hyp,
                                        lambda: compress(classifier.weight),
                                        0.1, 5)
    np.allclose(classifier.weight, 0.5 * hyp)
    np.allclose(costs, np.array([compress(hyp * (1 - i*0.1)) for i in range(1, 6)]))

def test_sanity_training():
    X = np.array([[2, 4],
                  [100, 5],
                  [6, 88],
                  [90, 111]])
    y = np.array([0, 1, 2, 3])

    classifier = LinearClassifier(num_classes=4, num_features=2)
    costs = classifier.train(X, y, rate=0.1, num_iter=100)
    assert (costs[-1, :] < costs[0, :]).all()

    # This first batch should be 100% accurate
    Xtest = np.array([[0 ,0],
                      [200, 230],
                      [6, 88],
                      [150, 19]])
    ytest = np.array([0, 3, 2, 1])

    acc, recalls = classifier.evaluate(Xtest, ytest)
    assert np.isclose(acc, 1)
    assert np.allclose(recalls, np.ones(4))

    # 3rd prediction should be wrong
    Xbad = np.array([[0 ,0],
                     [1, 4],
                     [6, 8],
                     [150, 19]])
    ybad = np.array([0, 0, 1, 1])
    acc, recalls = classifier.evaluate(Xbad, ybad)
    assert np.isclose(acc, 0.75)
    assert np.allclose(recalls, [1, .5, -1, -1])
