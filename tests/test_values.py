from sys import argv
from math import isclose
from time import sleep
from ina228 import INA228, Alert

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

    def __preconfigure(self):
        if len(argv) > 5:
            self._busn = int(argv[1], 0)
            self._addr = int(argv[2], 0)
            self._shunt = float(argv[3])
            self._voltage = float(argv[4])
            self._current = float(argv[5])
        else:
            self._busn = self.DEFAULT_BUSN
            self._addr = self.DEFAULT_SLAVE_ADDR
            self._shunt = self.DEFAULT_SHUNT_OHMS
            self._voltage = self.DEFAULT_SET_VOLTAGE
            self._current = self.DEFAULT_SET_CURRENT

        print(f'Running on live INA228 @ I²C{self._busn}:0x{self._addr:x}, shunt of {self._shunt} Ω; applied {self._voltage} V / {self._current} A.')
        self.ina228 = INA228(self._busn, self._addr, self._shunt)
        self.ina228.configure()


    def test_voltage(self):
        self.__preconfigure()
        sleep(1)
        measured = self.ina228.get_vbus_voltage()
        expected = self._voltage
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Voltage doesn't match: {measured} measured, {expected} expected"
        print(f"Voltage matches: {measured} measured, {expected} expected")


    def test_current(self):
        self.__preconfigure()
        sleep(1)
        measured = self.ina228.get_current()
        expected = self._current
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Current doesn't match: {measured} measured, {expected} expected"
        print(f"Current matches: {measured} measured, {expected} expected")


    def test_power(self):
        self.__preconfigure()
        sleep(1)
        measured = self.ina228.get_power()
        expected = self._current * self._voltage
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Power doesn't match: {measured} measured, {expected} expected"
        print(f"Power matches: {measured} measured, {expected} expected")


    def test_shunt_voltage(self):
        self.__preconfigure()
        sleep(1)
        measured = self.ina228.get_shunt_voltage()
        expected = self._current * self._shunt
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Shunt voltage doesn't match: {measured} measured, {expected} expected"
        print(f"Shunt voltage matches: {measured} measured, {expected} expected")


    def test_charge(self):
        self.__preconfigure()
        sleep(self.INTEGRATION_TIME)
        measured = self.ina228.get_charge()
        expected = self._current * self.INTEGRATION_TIME
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Charge doesn't match: {measured} measured, {expected} expected"
        print(f"Charge matches: {measured} measured, {expected} expected")


    def test_energy(self):
        self.__preconfigure()
        sleep(self.INTEGRATION_TIME)
        measured = self.ina228.get_energy()
        expected = self._current * self._voltage * self.INTEGRATION_TIME
        assert isclose(measured, expected, rel_tol=self.TOLERANCE), f"Energy doesn't match: {measured} measured, {expected} expected"
        print(f"Energy matches: {measured} measured, {expected} expected")


def test_voltage():
    values_test_suite().test_voltage()


def test_current():
    values_test_suite().test_current()


def test_power():
    values_test_suite().test_power()


def test_shunt_voltage():
    values_test_suite().test_shunt_voltage()


def test_charge():
    values_test_suite().test_charge()


def test_energy():
    values_test_suite().test_energy()


if __name__ =="__main__":
    test_voltage()
    test_current()
    test_power()
    test_shunt_voltage()
    test_charge()
    test_energy()
