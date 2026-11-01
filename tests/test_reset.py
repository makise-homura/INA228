"""Perform testing of INA228 module by running integrated values reset sequence on live INA228.

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

import pytest
@pytest.mark.skipif('config.getoption("stub")', reason='not supported with stub regmap')
def test_reset(busn, addr, shunt, voltage, current):
    """Perform testing of ability to reset of INA228 module."""

    TOLERANCE = 0.1 # 10%
    INTEGRATION_TIME_1 = 3
    INTEGRATION_TIME_2 = 5

    print(f'Configuring INA228 @ I²C{busn}:0x{addr:x}, shunt of {shunt} Ω; applied {voltage:.3f} V / {current:.3f} A.')
    ina228 = INA228(busn, addr, shunt)
    ina228.configure()

    for t in [INTEGRATION_TIME_1, INTEGRATION_TIME_2]:
        print(f'Accumulating for {t} seconds...')
        sleep(t)
        measured_q = ina228.get_charge()
        measured_w = ina228.get_energy()
        expected_q = current * t
        expected_w = current * voltage * t
        assert isclose(measured_q, expected_q, rel_tol=TOLERANCE), f"Charge doesn't match: {measured_q:.3f} measured, {expected_q:.3f} expected"
        assert isclose(measured_w, expected_w, rel_tol=TOLERANCE), f"Energy doesn't match: {measured_w:.3f} measured, {expected_w:.3f} expected"
        print(f"Measurements match estimations successfully: Q is {measured_q:.3f}≈{expected_q:.3f}, W is {measured_w:.3f}≈{expected_w:.3f}.")
        print('Resetting Q and W.')
        ina228.reset_energy()

if __name__ =="__main__":
    import argparse
    from conftest import cmdline_args
    del cmdline_args['stub']
    parser = argparse.ArgumentParser(description=test_reset.__doc__)
    for arg in cmdline_args:
        parser.add_argument('--' + arg, **cmdline_args[arg])
    args = parser.parse_args()
    test_reset(args.busn, args.addr, args.shunt, args.voltage, args.current)
