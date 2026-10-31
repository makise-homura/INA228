from math import isclose
from time import sleep
from ina228 import INA228

class values_test_suite:
    """Perform testing of INA228 module."""

    TOLERANCE = 0.1 # 10%
    INTEGRATION_TIME = 5
    INIT_TIME = 1

    def __init__(self, busn, addr, shunt, voltage, current):
        self._voltage = voltage
        self._current = current
        self._shunt = shunt
        print(f'Configuring INA228 @ I²C{busn}:0x{addr:x}, shunt of {shunt} Ω; applied {self._voltage} V / {self._current} A.')
        self.ina228 = INA228(busn, addr, shunt)
        self.ina228.configure()
        sleep(self.INIT_TIME)

    def __create_test_func(self, name, measure_func, expect_func, pause = False):
        def func(self):
            if pause:
                sleep(self.INTEGRATION_TIME - self.INIT_TIME)
            measured = measure_func()
            expected = expect_func()
            assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"{name} doesn't match: {measured} measured, {expected} expected"
            print(f"{name} matches: {measured} measured, {expected} expected")
        return func

    test_voltage = self.__create_test_func("Voltage", self.ina228.get_vbus_voltage, lambda: self._voltage)
    test_current = self.__create_test_func("Current", self.ina228.get_current, lambda: self._current)
    test_power = self.__create_test_func("Power", self.ina228.get_power, lambda: self._current * self._voltage)
    test_shunt_voltage = self.__create_test_func("Shunt voltage", self.ina228.get_shunt_voltage, lambda: self._current * self._shunt)
    test_charge = self.__create_test_func("Charge", self.ina228.get_charge, lambda: self._current * self.INTEGRATION_TIME, pause = True)
    test_energy = self.__create_test_func("Energy", self.ina228.get_energy, lambda: self._current * self._voltage * self.INTEGRATION_TIME, pause = True)


def test_voltage(busn, addr, shunt, voltage, current):
    values_test_suite(busn, addr, shunt, voltage, current).test_voltage()


def test_current(busn, addr, shunt, voltage, current):
    values_test_suite(busn, addr, shunt, voltage, current).test_current()


def test_power(busn, addr, shunt, voltage, current):
    values_test_suite(busn, addr, shunt, voltage, current).test_power()


def test_shunt_voltage(busn, addr, shunt, voltage, current):
    values_test_suite(busn, addr, shunt, voltage, current).test_shunt_voltage()


def test_charge(busn, addr, shunt, voltage, current):
    values_test_suite(busn, addr, shunt, voltage, current).test_charge()


def test_energy(busn, addr, shunt, voltage, current):
    values_test_suite(busn, addr, shunt, voltage, current).test_energy()


if __name__ =="__main__":
    """Module to test must be installed into the venv from which test is being ran.
    Requires INA228 with 12V supplied to V+/V-, and 364 mA fed through I+/I-.
    Accepts no less than 5 command-line arguments. If not given, uses default
    values, otherwise treats these arguments as parameters of a real INA228
    to be used in testing.
    Bus number and slave address may be given in hex, like 0xa or 0x40.

    Command-line args:
        argv[1]: Bus number where INA228 is located.
        argv[2]: Slave address of INA228.
        argv[3]: Shunt resistance in ohms.
        argv[4]: Applied voltage in volts.
        argv[5]: Applied current in amperes.
    """
    from sys import argv

    DEFAULT_BUSN = 0
    DEFAULT_SLAVE_ADDR = 0x40
    DEFAULT_SHUNT_OHMS = 0.002
    DEFAULT_SET_VOLTAGE = 12.0
    DEFAULT_SET_CURRENT = 0.364

    if len(argv) > 5:
        test_voltage(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_current(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_power(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_shunt_voltage(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_charge(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_energy(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
    else:
        test_voltage(DEFAULT_BUSN, DEFAULT_SLAVE_ADDR, DEFAULT_SHUNT_OHMS, DEFAULT_SET_VOLTAGE, DEFAULT_SET_CURRENT)
        test_current(DEFAULT_BUSN, DEFAULT_SLAVE_ADDR, DEFAULT_SHUNT_OHMS, DEFAULT_SET_VOLTAGE, DEFAULT_SET_CURRENT)
        test_power(DEFAULT_BUSN, DEFAULT_SLAVE_ADDR, DEFAULT_SHUNT_OHMS, DEFAULT_SET_VOLTAGE, DEFAULT_SET_CURRENT)
        test_shunt_voltage(DEFAULT_BUSN, DEFAULT_SLAVE_ADDR, DEFAULT_SHUNT_OHMS, DEFAULT_SET_VOLTAGE, DEFAULT_SET_CURRENT)
        test_charge(DEFAULT_BUSN, DEFAULT_SLAVE_ADDR, DEFAULT_SHUNT_OHMS, DEFAULT_SET_VOLTAGE, DEFAULT_SET_CURRENT)
        test_energy(DEFAULT_BUSN, DEFAULT_SLAVE_ADDR, DEFAULT_SHUNT_OHMS, DEFAULT_SET_VOLTAGE, DEFAULT_SET_CURRENT)
