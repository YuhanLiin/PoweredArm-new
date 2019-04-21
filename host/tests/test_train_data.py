import glob
import numpy as np
import pytest
from poweredarm.train_classifier import train_linear_classifier

@pytest.mark.train
# Run multiple times, since each run uses different training/test data
@pytest.mark.parametrize('execution_num', range(5))
def test_train_classifier_on_data(execution_num):
    # Train classifier on actual data and expect high accuracy
    acc, recalls = train_linear_classifier(glob.glob('tests/data/*.csv'))
    assert acc > 0.992 and (recalls > 0.975).all()
