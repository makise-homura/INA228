import pytest

def pytest_addoption(parser):
    parser.addoption("--busn", default=0, help="I²C bus number of INA228", type=int)
    parser.addoption("--addr", default=0x40, help="Slave address of INA228", type=int)
    parser.addoption("--shunt", default=0.002, help="Shunt resistance of INA228 in ohms", type=float)
    parser.addoption("--voltage", default=12.0, help="Voltage applied to INA228 in volts", type=float)
    parser.addoption("--current", default=0.364, help="Current through INA228 in amperes", type=float)

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
