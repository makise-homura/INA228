"""Perform testing of INA228 module by running some measurements and displaying the result.

Module to test must be installed into the venv from which test is being ran.
Performs 5 iterations with 1 second delay before each one on a live INA228,
or 10 iterations with 0.1 second delay in case of `--stub` is supplied.

Options:
  -h, --help         show this help message and exit
  --busn BUSN        I²C bus number of INA228 (may be given in hex)
  --addr ADDR        Slave address of INA228 (may be given in hex)
  --shunt SHUNT      Shunt resistance of INA228 in ohms
  --stub             Run with stub regmap instead of live INA228
"""

def test_main(busn, addr, shunt, stub):
    """Perform testing of INA228 module by running some measurements and displaying the result.

    Args:
        busn: I²C bus number of INA228
        addr: Slave address of INA228
        shunt: Shunt resistance of INA228 in ohms
        stub: True to run with stub regmap instead of live INA228, otherwise False

    Returns:
        Nothing.
    """
    from time import sleep
    from ina228 import INA228, Alert
    from datetime import datetime, UTC

    from stub_regmap import stub_regmap


    if stub:
        print('Running on stub regmap.')
        ina228 = INA228(stub_regmap=stub_regmap, shunt_ohms = shunt)
        iterations = 10
        sleep_sec = 0.1
    else:
        print(f'Running on live INA228 @ I²C{busn}:0x{addr:x}, shunt of {shunt} Ω.')
        ina228 = INA228(busn, addr, shunt)
        iterations = 5
        sleep_sec = 1

    ina228.configure()
    ina228.set_alert_bits(Alert.ALATCH)

    i = 0

    print(f'Manufacturer: {ina228.get_manufacturer_id()}')

    print('Device ID: {}, Revision: {}'.format(*ina228.get_deviceid()))

    while True:

        sleep(sleep_sec)

        print('---------------------------------------')
        print(f'Iteration:     {i}')
        print(f'Time:          {datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}')
        print(f'VBUS voltage:  {ina228.get_vbus_voltage():7.3f}  V')
        print(f'Current:       {ina228.get_current():7.3f}  A')
        print(f'Power:         {ina228.get_power():7.3f}  W')
        print(f'Shunt voltage: {ina228.get_shunt_voltage() * 1000:7.3f} mV')
        print(f'Die temp:      {ina228.get_temp():7.3f} °C')
        print(f'Energy:        {ina228.get_energy():7.3f}  J')
        print(f'Charge:        {ina228.get_charge():7.3f}  C')

        if i < iterations:
            i = i +1
        else:
            print('---------------------------------------')
            print('Alerts list in the end:')
            for alert in ina228.get_diag_alerts():
                print(f'  {ina228.alert_message(alert)}')
            break

if __name__ =="__main__":
    import argparse
    from conftest import cmdline_args
    del cmdline_args['voltage']
    del cmdline_args['current']
    parser = argparse.ArgumentParser(description=test_main.__doc__.splitlines()[0])
    for arg in cmdline_args:
        parser.add_argument('--' + arg, **cmdline_args[arg])
    args = parser.parse_args()
    test_main(args.busn, args.addr, args.shunt, args.stub)
