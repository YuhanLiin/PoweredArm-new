import numpy as np
from classifier.classifier import LinearClassifier

def test_sanity_predict():
    classifier = LinearClassifier(num_classes=6, num_features=4)
    result = classifier.predict(np.array([1., 2., 3., 4.]))
    assert result == 0
