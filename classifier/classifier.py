import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

class LinearClassifier:
    def __init__(self, num_classes, num_features, scaling_params=None, init_hyp=None):
        assert num_classes >= 2

        # let c = num_classes
        self.num_classes = num_classes
        # let n = num_features
        self.num_features = num_features
        # n+1 * c matrix
        self.hypothesis = np.zeros((num_features + 1, num_classes))
        # c length vector, defaults to all 1s (no feature scaling)
        self.scaling_params = np.ones(num_features)

        if init_hyp is not None:
            # Dependency injection for testing
            self.hypothesis[:, :] = init_hyp
        if scaling_params is not None:
            self.scaling_params[:] = scaling_params

    def _transform_y(self, y, m):
        """
        Convert a m * 1 vector y of ints representing class numbers to a
        m * c matrix Y of 0s and 1s, with Y(i, j) representing whether
        y(i) == class j
        """
        return (np.arange(self.num_classes)[None, :] == y).astype(int)

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
        h = sigmoid(X @ self.hypothesis)
        # Logistic regression cost fn, produces array of c
        cost = - np.sum(Y * np.log(h) + (1 - Y) * np.log(1 - h), 0) / m
        return cost

    def cost_delta(self, X, y):
        self._check_data_shape(X, y)
        m = y.shape[0]
        # Y -> m * c
        Y = self._transform_y(y, m)
        # h -> m * c
        h = sigmoid(X @ self.hypothesis)
        # return -> n+1 * c
        return X.T @ (h - Y)

    def gradient_descent(self, cost_delta, cost_fn, rate, num_iter):
        """
        Run gradient descent on the hypothesis matrix.

        :param cost_delta: Function taking no input and returning matrix matching
        dimensions of hypothesis matrix.
        :param cost_fn: Function taking no input and returning 1 * c matrix
        :param rate: Learning rate. Should be a number.
        :param num_iter: Number of iterations to use.
        :returns: List of cost function results from each iteration.
        """
        costs = []
        for i in range(num_iter):
            self.hypothesis -= rate * cost_delta()
            costs.append(cost_fn())
        # return num_iter * c matrix of costs for each class
        return np.array(costs)

    def scale_features(self, X):
        return X / self.scaling_params[None, :]

    def train(self, X, y):
        X = np.c_[ np.ones(X.shape[0]), self.scale_features(X) ]

        rate = 0.1
        num_iter = 100
        costs = self.gradient_descent(lambda: self.cost_delta(X, y),
                                      lambda: self.cost(X, y),
                                      rate, num_iter)
        return costs

    def predict(self, X):
        # X -> m * n
        assert X.shape[1] == self.num_features
        # Add column to X, so X -> m * n+1
        X = np.c_[ np.ones(X.shape[0]), self.scale_features(X) ]
        # result -> m * c
        result = X @ self.hypothesis
        # returns -> m array, where the ith sample is the predicted class for sample i
        return np.argmax(result, 1)

    def evaluate(self, X, y):
        def count(unique, counts):
            class_counts = np.zeros(self.num_classes)
            for cls, cnt in zip(unique, counts):
                class_counts[cls] = cnt
            return class_counts

        results = self.predict(X).flatten()
        y = y.flatten()
        # bool array indicating whether each prediction was accurate
        correct = results == y
        # array of length c that tallies the # of samples from each class
        class_counts = count(*np.unique(y, return_counts=True))
        # array of that tallies the # of samples from each class predicted correctly
        correct_counts = count(*np.unique(np.extract(correct, y), return_counts=True))

        # recall values for each class (samples predicted correctly / total sample set)
        # if class doesn't exist in data set, return -1
        recall_arr = np.divide(
            correct_counts, class_counts,
            out=np.full_like(class_counts, -1), where=class_counts!=0)
        # number representing overall accuracy of all samples
        accuracy = np.sum(correct) / len(y)
        return (accuracy, recall_arr)
        return accuracy, recalls
