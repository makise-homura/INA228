from ina228 import INA228
from datetime import datetime

ina228 = INA228()

ina228.configure()

i = 0

while True:    

    print('VBUS voltage: ', ina228.get_vbus_voltage())

    print('Current: ', ina228.get_current())

    print('Power: ', ina228.get_power())

    if i < 1000:

        i = i +1
        print(i, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])

    else:

        exit()
