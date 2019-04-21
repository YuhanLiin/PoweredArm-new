import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--train",
        action="store_true",
        help="run tests on actual tranining data")

def pytest_runtest_setup(item):
    if 'train' in item.keywords:
        if not item.config.getoption("--train"):
            pytest.skip('Skip training test')
