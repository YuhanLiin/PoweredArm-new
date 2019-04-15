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
        assert features.shape == (self.num_features,)
        features = np.array([1, *features]).reshape(-1, 1)
        result = self.hypothesis @ features
        return np.argmax(result)

    def _transform_y(self, y, m):
        """
        Convert a m * 1 vector y of ints representing class numbers to a
        m * c matrix Y of 0s and 1s, with Y(i, j) representing whether
        y(i) == class j
        """
        return np.equal(np.repeat(np.arange(self.num_classes).reshape(1, -1), m, 0),
                        np.repeat(y, self.num_classes, 1)).astype(int)

    def _check_data_shape(self, X, y):
        """
        Sanity check shape of input data. Assume column of ones has
        already been added to X.
        """
        # X -> m * n+1
        assert X.shape[1] == self.num_features + 1
        # y -> m * 1
        assert y.shape == (X.shape[0], 1)

    def cost(self, X, y):
        self._check_data_shape(X, y)
        m = y.shape[0]
        # Y -> m * c
        Y = self._transform_y(y, m)
        # h -> m * c
        h = sigmoid(X @ self.hypothesis.T)
        # Logistic regression cost fn, produces array of c
        cost = - np.sum(Y * np.log(h) + (1 - Y) * np.log(1 - h), 0) / m
        return cost

    def cost_delta(self, X, y):
        self._check_data_shape(X, y)
        m = y.shape[0]
        # y -> m * c
        Y = self._transform_y(y, m)
        # h -> m * c
        h = sigmoid(X @ self.hypothesis.T)
        # return -> n+1 * c
        return X.T @ (h - Y)

    def train(self, X, y, Xval, yval, Xtest, ytest):
        pass
