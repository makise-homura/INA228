from math import isclose
from time import sleep
from ina228 import INA228

class values_test_suite:
    """Perform testing of INA228 module.
    Module to test must be installed into the venv from which test is being ran.
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

    DEFAULT_BUSN = 0
    DEFAULT_SLAVE_ADDR = 0x40
    DEFAULT_SHUNT_OHMS = 0.002
    DEFAULT_SET_VOLTAGE = 12.0
    DEFAULT_SET_CURRENT = 0.364

    TOLERANCE = 0.1 # 10%
    INTEGRATION_TIME = 5
    INIT_TIME = 1

    def __init__(self, busn, addr, shunt, voltage, current):
        self._busn = busn
        self._addr = addr
        self._shunt = shunt
        self._voltage = voltage
        self._current = current
        print(f'Configuring INA228 @ I²C{self._busn}:0x{self._addr:x}, shunt of {self._shunt} Ω; applied {self._voltage} V / {self._current} A.')
        self.ina228 = INA228(self._busn, self._addr, self._shunt)
        self.ina228.configure()
        sleep(self.INIT_TIME)


    def test_voltage(self):
        measured = self.ina228.get_vbus_voltage()
        expected = self._voltage
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Voltage doesn't match: {measured} measured, {expected} expected"
        print(f"Voltage matches: {measured} measured, {expected} expected")


    def test_current(self):
        measured = self.ina228.get_current()
        expected = self._current
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Current doesn't match: {measured} measured, {expected} expected"
        print(f"Current matches: {measured} measured, {expected} expected")


    def test_power(self):
        measured = self.ina228.get_power()
        expected = self._current * self._voltage
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Power doesn't match: {measured} measured, {expected} expected"
        print(f"Power matches: {measured} measured, {expected} expected")


    def test_shunt_voltage(self):
        measured = self.ina228.get_shunt_voltage()
        expected = self._current * self._shunt
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Shunt voltage doesn't match: {measured} measured, {expected} expected"
        print(f"Shunt voltage matches: {measured} measured, {expected} expected")


    def test_charge(self):
        sleep(self.INTEGRATION_TIME - self.INIT_TIME)
        measured = self.ina228.get_charge()
        expected = self._current * self.INTEGRATION_TIME
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Charge doesn't match: {measured} measured, {expected} expected"
        print(f"Charge matches: {measured} measured, {expected} expected")


    def test_energy(self):
        sleep(self.INTEGRATION_TIME - self.INIT_TIME)
        measured = self.ina228.get_energy()
        expected = self._current * self._voltage * self.INTEGRATION_TIME
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Energy doesn't match: {measured} measured, {expected} expected"
        print(f"Energy matches: {measured} measured, {expected} expected")


def test_voltage(busn = values_test_suite.DEFAULT_BUSN, addr = values_test_suite.DEFAULT_SLAVE_ADDR, shunt = values_test_suite.DEFAULT_SHUNT_OHMS, voltage = values_test_suite.DEFAULT_SET_VOLTAGE, current = values_test_suite.DEFAULT_SET_CURRENT):
    values_test_suite(busn, addr, shunt, voltage, current).test_voltage()


def test_current(busn = values_test_suite.DEFAULT_BUSN, addr = values_test_suite.DEFAULT_SLAVE_ADDR, shunt = values_test_suite.DEFAULT_SHUNT_OHMS, voltage = values_test_suite.DEFAULT_SET_VOLTAGE, current = values_test_suite.DEFAULT_SET_CURRENT):
    values_test_suite(busn, addr, shunt, voltage, current).test_current()


def test_power(busn = values_test_suite.DEFAULT_BUSN, addr = values_test_suite.DEFAULT_SLAVE_ADDR, shunt = values_test_suite.DEFAULT_SHUNT_OHMS, voltage = values_test_suite.DEFAULT_SET_VOLTAGE, current = values_test_suite.DEFAULT_SET_CURRENT):
    values_test_suite(busn, addr, shunt, voltage, current).test_power()


def test_shunt_voltage(busn = values_test_suite.DEFAULT_BUSN, addr = values_test_suite.DEFAULT_SLAVE_ADDR, shunt = values_test_suite.DEFAULT_SHUNT_OHMS, voltage = values_test_suite.DEFAULT_SET_VOLTAGE, current = values_test_suite.DEFAULT_SET_CURRENT):
    values_test_suite(busn, addr, shunt, voltage, current).test_shunt_voltage()


def test_charge(busn = values_test_suite.DEFAULT_BUSN, addr = values_test_suite.DEFAULT_SLAVE_ADDR, shunt = values_test_suite.DEFAULT_SHUNT_OHMS, voltage = values_test_suite.DEFAULT_SET_VOLTAGE, current = values_test_suite.DEFAULT_SET_CURRENT):
    values_test_suite(busn, addr, shunt, voltage, current).test_charge()


def test_energy(busn = values_test_suite.DEFAULT_BUSN, addr = values_test_suite.DEFAULT_SLAVE_ADDR, shunt = values_test_suite.DEFAULT_SHUNT_OHMS, voltage = values_test_suite.DEFAULT_SET_VOLTAGE, current = values_test_suite.DEFAULT_SET_CURRENT):
    values_test_suite(busn, addr, shunt, voltage, current).test_energy()


if __name__ =="__main__":
    from sys import argv

    if len(argv) > 5:
        test_voltage(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_current(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_power(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_shunt_voltage(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_charge(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
        test_energy(int(argv[1], 0), int(argv[2], 0), float(argv[3]), float(argv[4]), float(argv[5]))
    else:
        test_voltage()
        test_current()
        test_power()
        test_shunt_voltage()
        test_charge()
        test_energy()
