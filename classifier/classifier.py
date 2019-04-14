import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

class LinearClassifier:
    def __init__(self, num_classes, num_features, init_hyp=None):
        assert num_classes >= 2

        # let c = num_classes
        self.num_classes = num_classes
        # let n = num_features
        self.num_features = num_features
        # c * n+1 matrix
        self.hypothesis = np.zeros((num_classes, num_features + 1))
        if init_hyp is not None:
            # Dependency injection for testing
            self.hypothesis[:, :] = init_hyp
    
    def predict(self, features):
        features = np.array([1, *features]).reshape(-1, 1)
        result = self.hypothesis @ features
        return np.argmax(result)

    def cost(self, X, y):
        # X -> m * n+1
        assert X.shape[1] == self.num_features + 1
        # y -> m * 1
        assert y.shape == (X.shape[0], 1)
        m = y.shape[0]

        # y -> m * c
        y = np.equal(np.repeat(np.arange(self.num_classes).reshape(1, -1), m, 0),
                     np.repeat(y, self.num_classes, 1)).astype(int)
        # h -> m * c
        h = sigmoid(X @ self.hypothesis.T)
        # Logistic regression cost fn, produces 1 * c vector
        cost = - np.sum(y * np.log(h) + (1 - y) * np.log(1 - h), 0) / m
        return cost

    def train(self, X, y, Xval, yval, Xtest, ytest):
        pass
