import glob
import numpy as np
import pytest
from poweredarm.train_classifier import train_linear_classifier

@pytest.mark.train
def test_train_classifier_on_data():
    # Train classifier on actual data and expect high accuracy
    acc, recalls = train_linear_classifier(glob.glob('tests/data/*.csv'))
    assert acc > 0.992 and (recalls > 0.98).all()
