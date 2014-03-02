import sys


def pytest_configure(config):
    sys._pytest_is_running = True

def pytest_unconfigure(config):
    del sys._pytest_is_running
