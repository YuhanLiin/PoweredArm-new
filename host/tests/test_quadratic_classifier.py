import numpy as np
import pytest
from poweredarm.classifier import QuadraticClassifier, sigmoid

def test_add_quadratic_features():
    classifier = QuadraticClassifier(2, 2)
    data = np.arange(4).reshape([2, 2])
    quad = classifier._add_quadratic_features(data)
    assert np.allclose(quad, np.array([[0, 1, 0, 0, 1], [2, 3, 4, 6, 9]]))
    assert classifier.num_features == 5

    classifier = QuadraticClassifier(4, 4)
    data = np.arange(4).reshape([1, 4])
    quad = classifier._add_quadratic_features(data)
    assert np.allclose(quad, np.array([[0, 1, 2, 3, 0, 0, 0, 0, 1, 2, 3, 4, 6, 9]]))
    assert classifier.num_features == 14

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

    classifier = QuadraticClassifier(num_classes=4, num_features=2)
    costs = classifier.train(X, y, rate=0.1, num_iter=100)
    assert (costs[-1, :] < costs[0, :]).all()

    acc, recalls = classifier.evaluate(Xtest, ytest)
    assert np.isclose(acc, expected_acc)
    assert np.allclose(recalls, expected_recalls)
