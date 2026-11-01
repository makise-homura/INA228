"""Perform testing of alert subsystem of the INA228 module.

Module to test must be installed into the venv from which test is being ran.
Requires INA228 with some nonzero voltage supplied to V+/V-, some nonzero
current fed through I+/I-, and some positive ambient temperature.
Default values are given in `conftest.py`.

Options:
  -h, --help         show this help message and exit
  --busn BUSN        I²C bus number of INA228 (may be given in hex)
  --addr ADDR        Slave address of INA228 (may be given in hex)
  --shunt SHUNT      Shunt resistance of INA228 in ohms
"""

from time import sleep
from ina228 import INA228, Alert

class alerts_test_suite:
    """Perform testing of alert subsystem of the INA228 module."""

    THRESHOLD = 0.2 # 20%
    SETTLE_TIME = 0.5 # seconds

    func_names = ['test_CNVRF', 'test_BUSUL', 'test_BUSOL', 'test_SHNTUL', 'test_SHNTOL', 'test_TMPOL', 'test_POL']

    def __create_test_func(self, alert, measure_func, set_func, is_over):
        def func():
            print(f'Testing {alert.name}.')
            self.ina228.configure()
            sleep(self.SETTLE_TIME)
            measured = measure_func()
            lesser = measured * (1 - self.THRESHOLD)
            greater = measured * (1 + self.THRESHOLD)
            print(f'- Current value is {measured:.6f}, will use {lesser:.6f} as lesser value and {greater:.6f} as greater one.')

            self.ina228.set_alert_bits(Alert.ALATCH)
            sleep(self.SETTLE_TIME)
            set_func(lesser if is_over else greater)
            sleep(self.SETTLE_TIME)
            assert alert in self.ina228.get_diag_alerts(), 'Latch mode: alert not fired on condition'
            print('- Latch mode: alert fired on condition')
            sleep(self.SETTLE_TIME)
            set_func(greater if is_over else lesser)
            sleep(self.SETTLE_TIME)
            assert alert in self.ina228.get_diag_alerts(), 'Latch mode: alert not latched after condition'
            print('- Latch mode: alert latched after condition')
            sleep(self.SETTLE_TIME)
            assert alert not in self.ina228.get_diag_alerts(), 'Latch mode: alert not cleared after second read'
            print('- Latch mode: alert cleared after second read')

            self.ina228.set_alert_bits()
            sleep(self.SETTLE_TIME)
            set_func(lesser if is_over else greater)
            sleep(self.SETTLE_TIME)
            assert alert in self.ina228.get_diag_alerts(), 'Transparent mode: alert not fired on condition'
            print('- Transparent mode: alert fired on condition')
            sleep(self.SETTLE_TIME)
            set_func(greater if is_over else lesser)
            sleep(self.SETTLE_TIME)
            assert alert not in self.ina228.get_diag_alerts(), 'Transparent mode: alert not cleared after condition'
            print('- Transparent mode: alert cleared after condition')

            print(f'{self.ina228.alert_message(alert)} - behaves correctly.')
        return func

    def generate_test_methods(self):
        self.test_BUSUL = self.__create_test_func(Alert.BUSUL, self.ina228.get_vbus_voltage, self.ina228.set_bus_undervoltage, is_over=False)
        self.test_BUSOL = self.__create_test_func(Alert.BUSOL, self.ina228.get_vbus_voltage, self.ina228.set_bus_overvoltage, is_over=True)
        self.test_SHNTUL = self.__create_test_func(Alert.SHNTUL, self.ina228.get_shunt_voltage, self.ina228.set_shunt_undervoltage, is_over=False)
        self.test_SHNTOL = self.__create_test_func(Alert.SHNTOL, self.ina228.get_shunt_voltage, self.ina228.set_shunt_overvoltage, is_over=True)
        self.test_TMPOL = self.__create_test_func(Alert.TMPOL, self.ina228.get_temp, self.ina228.set_temp_limit, is_over=True)
        self.test_POL = self.__create_test_func(Alert.POL, self.ina228.get_power, self.ina228.set_power_overlimit, is_over=True)

    def __init__(self, busn, addr, shunt):
        print(f'Configuring INA228 @ I²C{busn}:0x{addr:x}, shunt of {shunt} Ω.')
        self.ina228 = INA228(busn, addr, shunt)
        self.generate_test_methods()

    def test_CNVRF(self):
        print(f'Testing CNVRF.')
        self.ina228.configure()
        assert Alert.CNVRF not in self.ina228.get_diag_alerts(), 'Got alert immediately after initialization'
        print('- Did not got alert immediately after initialization')
        sleep(self.SETTLE_TIME)
        assert Alert.CNVRF in self.ina228.get_diag_alerts(), 'Did not get alert after 1 second'
        print('- Got alert after 1 second')
        print(f'{self.ina228.alert_message(Alert.CNVRF)} - behaves correctly.')

import pytest

@pytest.mark.skipif('config.getoption("stub")', reason='not supported with stub regmap')
@pytest.mark.parametrize('func', alerts_test_suite.func_names)
def test_function(func, busn, addr, shunt):
    getattr(alerts_test_suite(busn, addr, shunt), func)()

if __name__ =="__main__":
    import argparse
    from conftest import cmdline_args
    del cmdline_args['stub']
    del cmdline_args['voltage']
    del cmdline_args['current']
    parser = argparse.ArgumentParser(description=alerts_test_suite.__doc__)
    for arg in cmdline_args:
        parser.add_argument('--' + arg, **cmdline_args[arg])
    args = parser.parse_args()

    for func in alerts_test_suite.func_names:
        test_function(func, args.busn, args.addr, args.shunt)
