import csv
import time
import serial
from matplotlib import pyplot as plt
from poweredarm.util import NUM_FEATURES
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

def graph_csv(filename):
    fdata = np.loadtxt(filename, delimiter=',', dtype=np.float32)
    fdata = fdata[:, :8]
    plt.plot(np.arange(np.shape(fdata)[0]), fdata)
    plt.title('EMG Data for {}'.format(filename))
    plt.xlabel('Time')
    plt.ylabel('Magnitude')
    plt.show()

def collect_from_serial(filename, label):
    """
    Reads output data from USB serial port for some time and puts it
    into CSV data file along with the supplied label. Used to create
    labelled training data.
    """
    with serial.Serial('/dev/ttyUSB0', 115200, xonxoff=True) as ser:
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)

            timeout = time.time() + 15
            while time.time() < timeout:
                line = ser.readline().decode('utf-8')

                if line.startswith("_DATA_"):
                    data = line.split()[1:NUM_FEATURES + 1]
                    # Type check the values
                    data = [int(i) for i in data] + [label]
                    print(data)
                    writer.writerow(data)
