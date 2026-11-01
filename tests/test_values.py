"""Perform testing of INA228 module by running value assertions on live INA228.

Module to test must be installed into the venv from which test is being ran.
Requires INA228 with a certain voltage supplied to V+/V-,
and a certain current fed through I+/I-.
Default values are given in `conftest.py`.

options:
  -h, --help         show this help message and exit
  --busn BUSN        I²C bus number of INA228 (may be given in hex)
  --addr ADDR        Slave address of INA228 (may be given in hex)
  --shunt SHUNT      Shunt resistance of INA228 in ohms
  --voltage VOLTAGE  Voltage applied to INA228 in volts
  --current CURRENT  Current through INA228 in amperes
"""

from math import isclose
from time import sleep
from ina228 import INA228

class values_test_suite:
    """Perform testing of INA228 module."""

    TOLERANCE = 0.1 # 10%
    INTEGRATION_TIME = 5
    INIT_TIME = 1

    func_names = ['test_voltage', 'test_current', 'test_power', 'test_shunt_voltage', 'test_charge', 'test_energy']

    def __create_test_func(self, name, measure_func, expect_func, pause = False):
        def func():
            if pause:
                sleep(self.INTEGRATION_TIME - self.INIT_TIME)
            measured = measure_func()
            expected = expect_func()
            assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"{name} doesn't match: {measured:.6f} measured, {expected:.6f} expected"
            print(f"{name} matches: {measured:.6f} measured, {expected:.6f} expected")
        return func

    def generate_test_methods(self):
        self.test_voltage = self.__create_test_func("Voltage", self.ina228.get_vbus_voltage, lambda: self._voltage)
        self.test_current = self.__create_test_func("Current", self.ina228.get_current, lambda: self._current)
        self.test_power = self.__create_test_func("Power", self.ina228.get_power, lambda: self._current * self._voltage)
        self.test_shunt_voltage = self.__create_test_func("Shunt voltage", self.ina228.get_shunt_voltage, lambda: self._current * self._shunt)
        self.test_charge = self.__create_test_func("Charge", self.ina228.get_charge, lambda: self._current * self.INTEGRATION_TIME, pause = True)
        self.test_energy = self.__create_test_func("Energy", self.ina228.get_energy, lambda: self._current * self._voltage * self.INTEGRATION_TIME, pause = True)

    def __init__(self, busn, addr, shunt, voltage, current):
        self._voltage = voltage
        self._current = current
        self._shunt = shunt
        print(f'Configuring INA228 @ I²C{busn}:0x{addr:x}, shunt of {shunt} Ω; applied {self._voltage:.3f} V / {self._current:.3f} A.')
        self.ina228 = INA228(busn, addr, shunt)
        self.generate_test_methods()
        self.ina228.configure()
        sleep(self.INIT_TIME)

import pytest

@pytest.mark.skipif('config.getoption("stub")', reason='not supported with stub regmap')
@pytest.mark.parametrize('func', values_test_suite.func_names)
def test_function(func, busn, addr, shunt, voltage, current):
    getattr(values_test_suite(busn, addr, shunt, voltage, current), func)()

if __name__ =="__main__":
    import argparse
    from conftest import cmdline_args
    del cmdline_args['stub']
    parser = argparse.ArgumentParser(description=values_test_suite.__doc__)
    for arg in cmdline_args:
        parser.add_argument('--' + arg, **cmdline_args[arg])
    args = parser.parse_args()

    for func in values_test_suite.func_names:
        test_function(func, args.busn, args.addr, args.shunt, args.voltage, args.current)
