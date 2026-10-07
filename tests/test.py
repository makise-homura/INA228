def test_main():
    from sys import argv
    from time import sleep
    from ina228 import INA228
    from datetime import datetime, UTC

    from stub_regmap import stub_regmap

    if len(argv) > 3:
        print(f'Running on live INA228 @ I²C{argv[1]}:{argv[2]}, shunt of {argv[3]} Ω.')
        ina228 = INA228(int(argv[1], 0), int(argv[2], 0), float(argv[3]))
        iterations = 5
        sleep_sec = 1
    else:
        print('Running on stub regmap.')
        ina228 = INA228(stub_regmap=stub_regmap, shunt_ohms = 0.002)
        iterations = 10
        sleep_sec = 0.1

    ina228.configure()

    i = 0

    print('Manufacturer ID (HEX): {}, (CHAR): {}{}'.format(*ina228.get_manufacturer_id()))

    print('Device ID: {}, Revision: {}'.format(*ina228.get_deviceid()))

    while True:

        sleep(sleep_sec)

        print('VBUS voltage: ', ina228.get_vbus_voltage())

        print('Current: ', ina228.get_current())

        print('Power: ', ina228.get_power())

        print('Shunt voltage: ', ina228.get_shunt_voltage())

        print('Die temp: ', ina228.get_temp())

        print('Energy: ', ina228.get_energy())

        print('Charge: ', ina228.get_charge())

        if i < iterations:

            i = i +1
            print(i, datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

        else:

            break

if __name__ =="__main__":
    test_main()
