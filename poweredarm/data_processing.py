import numpy as np

def aggregate_csv(data_files):
    """
    Load training data from a list of CSV files, concatenate them by the column,
    and returns them after shuffling.
    """
    data = np.array([])

    for fname in data_files:
        fdata = np.loadtxt(fname, delimiter=',', dtype=np.float32)
        data = np.vstack([data, fdata]) if data.size else fdata

    np.random.shuffle(data)
    return data

def create_dataset(data, proportions):
    """
    Split data into chunks according to a list of proportions. The last chunk is
    the portion of the data not covered by the proportions. Output is also split
    into X and y sets, since the y vector is the last column of the data.

    Yields each pair of (X, y) sets.
    """
    m = data.shape[0] 
    pos = 0

    for p in proportions:
        assert p < 1
        end = int(pos + p*m)
        chunk = data[pos:end, :]
        pos = end

        X, y = chunk[:, :-1], chunk[:, -1]
        yield X
        yield y

    chunk = data[pos:, :]
    X, y = chunk[:, :-1], chunk[:, -1]
    yield X
    yield y
