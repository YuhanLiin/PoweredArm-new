from os import path
import glob
import numpy as np
import pytest
from poweredarm.train_classifier import train_linear_classifier, train_quadratic_classifier

@pytest.mark.train
# Run multiple times, since each run uses different training/test data
@pytest.mark.parametrize('execution_num', range(5))
def test_train_classifier_on_data(execution_num):
    # Train classifier on actual data and expect high accuracy
    files = path.join('tests', 'data', 'dataset', '*.csv')
    acc, recalls = train_linear_classifier(glob.glob(files))
    assert acc > 0.98 and (recalls > 0.97).all()

@pytest.mark.train
# Run multiple times, since each run uses different training/test data
@pytest.mark.parametrize('execution_num', range(5))
def test_train_quadratic_classifier_on_data(execution_num):
    # Train classifier on actual data and expect high accuracy
    files = path.join('tests', 'data', 'dataset', '*.csv')
    acc, recalls = train_quadratic_classifier(glob.glob(files))
    assert acc > 0.98 and (recalls > 0.97).all()
