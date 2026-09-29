from ina228 import INA228
from datetime import datetime

ina228 = INA228()

ina228.configure()

i = 0

print('Manufacturer ID (HEX): {}, (CHAR): {}'.format(*ina228.get_manufacturer_id()))

print('Device ID: {}, Revision: {}'.format(*ina228.get_deviceid()))

while True:    

    print('VBUS voltage: ', ina228.get_vbus_voltage())

    print('Current: ', ina228.get_current())

    print('Power: ', ina228.get_power())

    print('Shunt voltage: ', ina228.get_shunt_voltage())

    print('Die temp: ', ina228.get_temp())

    print('Energy: ', ina228.get_energy())

    print('Charge: ', ina228.get_charge())

    if i < 1000:

        i = i +1
        print(i, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    else:

        exit()
