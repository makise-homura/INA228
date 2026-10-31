import pytest

cmdline_args = {
    'busn':    {'default': 0,           'help': "I²C bus number of INA228 (may be given in hex)", 'type': lambda x: int(x, 0)},
    'addr':    {'default': 0x40,        'help': "Slave address of INA228 (may be given in hex)",  'type': lambda x: int(x, 0)},
    'shunt':   {'default': 0.002,       'help': "Shunt resistance of INA228 in ohms",             'type': float},
    'voltage': {'default': 12.0,        'help': "Voltage applied to INA228 in volts",             'type': float},
    'current': {'default': 0.364,       'help': "Current through INA228 in amperes",              'type': float},
    'stub':    {'action': 'store_true', 'help': "Run with stub regmap instead of live INA228"}
}

def pytest_addoption(parser):
    for arg in cmdline_args:
        parser.addoption('--' + arg, **cmdline_args[arg])

@pytest.fixture
def busn(request): return request.config.getoption("busn")

@pytest.fixture
def addr(request): return request.config.getoption("addr")

@pytest.fixture
def shunt(request): return request.config.getoption("shunt")

@pytest.fixture
def voltage(request): return request.config.getoption("voltage")

@pytest.fixture
def current(request): return request.config.getoption("current")

@pytest.fixture
def stub(request): return request.config.getoption("stub")
