import numpy as np

class LinearClassifier:
    def __init__(self, num_classes, num_features):
        self.num_classes = num_classes
        self.num_features = num_features
        self.hypothesis = np.zeros((num_features + 1, num_classes))
    
    def predict(self, features):
        features = np.array([1, *features])
        result = self.hypothesis @ features
        return np.argmax(result)

    def train(self, data):
        pass
