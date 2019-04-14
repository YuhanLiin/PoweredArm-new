import numpy as np

class LinearClassifier:
    def __init__(self, num_classes, num_features):
        self.num_classes = num_classes
        self.num_features = num_features
        # features * classes matrix
        self.hypothesis = np.zeros((num_classes, num_features + 1))
    
    def predict(self, features):
        features = np.array([1, *features]).reshape(-1, 1)
        result = self.hypothesis @ features
        return np.argmax(result)

    def train(self, data):
        pass
