import numpy as np
import pytest
from poweredarm.classifier import QuadraticClassifier, sigmoid

def test_add_quadratic_features():
    classifier = QuadraticClassifier(2, 2)
    data = np.arange(4).reshape([2, 2])
    quad = classifier._add_quadratic_features(data)
    assert np.allclose(quad, np.array([[0, 1, 0, 0, 1], [2, 3, 4, 6, 9]]))
