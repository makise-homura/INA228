# INA228

Driver for TI INA228 voltage/current sensor located on SMBus.

## Installation

Module is [available](https://pypi.org/project/ina228/) on PyPi.
So just `pip install ina228` should be enough, if you're not up to contributing.

## Typical usage

```python
    from ina228 import INA228
    ina228 = INA228(bus, addr)
    ina228.configure()
    time.sleep(1)
    print('Voltage: ', ina228.get_vbus_voltage())
    print('Current: ', ina228.get_current())
    print('Power: ', ina228.get_power())
```

To use the module, just import `INA228` class from there.
You probably don't need anything else.

Create the instance of `INA228` class, specifying the device location on SMBus.

Then initialize it by calling `configure()` method, and now it is ready to work.

After configuring, don't forget to leave device some time for the first measurement.
1 second should be enough.

Then you may use every method you want to get measurement results.

## Useful methods

* `reset_all()`: Perform the power-on reset of the chip.
* `reset_energy()`: Reset energy and charge counters.
* `get_shunt_voltage()`: Read voltage on the shunt resistor.
* `get_vbus_voltage()`: Read voltage on the V+/V- terminals.
* `get_temp()`: Read die temperature.
* `get_current()`: Read current through I+/I- terminals.
* `get_power()`: Read calculated power (a product of voltage and current).
* `get_energy()`: Read integral energy (a product of power and time since last reset).
* `get_charge()`: Read charge spent (a product of current and time since last reset).
* `get_diag_alerts()`: Test if specific alert is active.
* `set_shunt_overvoltage()`: Set high alert threshold of the shunt resistor voltage.
* `set_shunt_undervoltage()`: Set low alert threshold of the shunt resistor voltage.
* `set_bus_overvoltage()`: Set high alert threshold of the V+/V- terminals voltage.
* `set_bus_undervoltage()`: Set low alert threshold of the V+/V- terminals voltage.
* `set_temp_limit()`: Set high alert threshold of the die temperature.
* `set_power_overlimit()`: Set high alert threshold of the load power.
* `get_manufacturer_id()`: Read manufacturer ID.
* `get_deviceid()`: Read device ID.

Detailed documentation can be found in the docstrings in [api.py](src/ina228/api.py).

## Building from source

Just run:

```console
python3 -m build
```

It will create `dist` subdirectory and put sdist and bdist (wheel) there.

## Requirements

For now, it relies on `smbus2` module (see [requirements.txt](requirements.txt)).

## Testing

See [corresponding README](tests/README.md).

## Known bugs and TODO list

* Value of VSHUNT is needed to be multiplied by 10 to get correct value.

* All trash should be put out to constants file.
* Alert register read should be redone in a more correct way.

## Credits

Original code by [@megalloid](https://t.me/megalloid).
Python module created and maintained by [@makise_homura](https://t.me/makise_homura).
