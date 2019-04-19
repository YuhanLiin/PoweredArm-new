import numpy as np
import pytest
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
    # Check that cost function computes correctly
    weight = np.array([[1, 1],
                    [3, 5]]).T
    classifier = LinearClassifier(num_classes=2, num_features=1, init_weight=weight)
    X = np.array([[1, 3],
                  [1, 0],
                  [1, -4]])
    y = np.array([1, 0, 1])
    cost = classifier.cost(X, y)
    assert np.allclose(cost, np.array([1.45999966, 6.68286247]))

def test_sanity_cost_delta():
    # Check that cost delta computes correctly
    weight = np.array([[1, 1],
                    [3, 5]]).T
    classifier = LinearClassifier(num_classes=2, num_features=1, init_weight=weight)
    X = np.array([[1, 3],
                  [1, 0],
                  [1, -4]])
    y = np.array([1, 0, 1])
    delta = classifier.cost_delta(X, y)
    assert np.allclose(
        delta,
        np.array([[0.76049824, -0.04742585],
                 [2.75633788,  3.99999979]])
    )

@pytest.mark.parametrize('num_features', [1, 10, 32])
@pytest.mark.parametrize('num_classes', [2, 31, 14])
def test_gradient_descent(num_features, num_classes):
    # Run gradient descent with arbitrary cost and cost delta functions
    # for 5 iterations
    def compress(arr):
        return arr.sum(1).T

    weight = np.array([[1, 3],
                    [0, 43],
                    [8, 10]]).T
    weight = np.random.rand(num_features + 1, num_classes)
    classifier = LinearClassifier(
        num_classes=num_classes,
        num_features=num_features,
        init_weight=weight)
    costs = classifier.gradient_descent(lambda: weight,
                                        lambda: compress(classifier.weight),
                                        0.1, 5)
    # Cost delta function just returns the classifier's weight matrix,
    # so wieght should be halved after 5 iterations at rate of 0.1
    assert np.allclose(classifier.weight, 0.5 * weight)
    assert np.allclose(
        costs,
        np.array([compress(weight * (1 - i*0.1)) for i in range(1, 6)])
    )

@pytest.mark.parametrize('Xtest, ytest, expected_acc, expected_recalls',
    [
        # This first batch should be 100% accurate
        (np.array([[0, 0], [200, 230], [6, 88], [150, 19]]),
         np.array([0, 3, 2, 1]), 1, np.ones(4)),
        # 3rd prediction should be wrong
        (np.array([[0, 0], [1, 4], [6, 8], [150, 19]]),
         np.array([0, 0, 1, 1]), 0.75, [1, .5, -1, -1])
    ]
)
def test_sanity_training(Xtest, ytest, expected_acc, expected_recalls):
    X = np.array([[2, 4],
                  [100, 5],
                  [6, 88],
                  [90, 111]])
    y = np.array([0, 1, 2, 3])

    classifier = LinearClassifier(num_classes=4, num_features=2)
    costs = classifier.train(X, y, rate=0.1, num_iter=100)
    assert (costs[-1, :] < costs[0, :]).all()

    acc, recalls = classifier.evaluate(Xtest, ytest)
    assert np.isclose(acc, expected_acc)
    assert np.allclose(recalls, expected_recalls)

@pytest.mark.parametrize('num_features', [1, 2, 3])
@pytest.mark.parametrize('num_classes', [2, 3, 4])
def test_save_load(num_features, num_classes):
    classifier = LinearClassifier(num_classes=num_classes, num_features=num_features)
    m = 10
    X = np.random.rand(m, num_features)
    y = np.random.randint(0, num_classes, m)
    classifier.train(X, y, rate=0.01, num_iter=20)

    filename = 'tests/data/classifier.npz'
    classifier.save(filename)
    # Save and load classifier and see if it matches the original
    assert LinearClassifier.load(filename) == classifier
