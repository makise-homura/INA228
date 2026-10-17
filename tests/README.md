# Testing the project

This document describes how to test the INA228 package.

## Preparation

First, build the package.

After building the package, create venv for testing (you might need `python3-venv` for this):

```console
python3 -m venv .venv
```

Install the module you've built there:

```console
.venv/bin/pip install dist/ina228-*.whl --force-reinstall
```

## test.py

This test is automated, and it tests the following methods (along with constructor and `configure()`):

* `get_shunt_voltage()`: Read voltage on the shunt resistor.
* `get_vbus_voltage()`: Read voltage on the V+/V- terminals.
* `get_temp()`: Read die temperature.
* `get_current()`: Read current through I+/I- terminals.
* `get_power()`: Read calculated power (a product of voltage and current).
* `get_energy()`: Read integral energy (a product of power and time since last reset).
* `get_charge()`: Read charge spent (a product of current and time since last reset).
* `get_manufacturer_id()`: Read manufacturer ID.
* `get_deviceid()`: Read device ID.

### Manual run

Run the test like this:

```console
.venv/bin/python tests/test.py
```

It will test the module you've just installed in your venv.

#### Test behavior

By default, test will perform 11 iterations (0th till 10th) with a 0.1-second interval on an emulated INA228 (not the real one even if it exists).
Each iteration will read out VBUS voltage, current, power, shunt voltage, die temp, energy, and charge using INA228 module,
and print them out along with iteration number and current time.
If it has not thrown an exception, it always ends successfully.

#### INA228 emulation

Emulation will use supplied `stub_regmap.py` by default.
It is a dump of registers once captured on the live INA228, and used by the test so it will not depend on hardware.

If you want your own stub regmap, generate it by running `./map.sh > stub_regmap.py` on the system with live INA228.
Don't forget to install `i2cget` with something like `apt install i2c-tools` prior to running this.

By default, `map.sh` expects to find INA228 on bus 0, address 0x40.
You may specify different bus number and/or slave address with environment variables, like this:

```console
bus=2 addr=0x42 ./map.sh > stub_regmap.py
```

#### Testing on a live INA228

If you want to use a live INA228 instead of the emulated one, specify bus, address, and shunt resistance in command line like this:

```console
.venv/bin/python tests/test.py 0 0x40 0.002
```

Test will perform 6 iterations (0th till 5th) with a 1-second interval.

When testing the real INA228, it is advised to build a test setup by supplying a constant voltage *V* through a resistor of *R*.
Make sure that your shunt resistance *r* is set correctly when test is invoked, and check you room temperature *T*.

These methods are considered being correctly implemented, if the test displays the following results
(for example, let R be 33Ω, V be 12V, r be 0.002Ω, and T be 25°C):

* `get_shunt_voltage()`: `Shunt voltage` is equal to *V* × *r* / *R* (e.g. 0.727mV).
* `get_vbus_voltage()`: `VBUS voltage` is equal to *V* (e.g. 12.0V).
* `get_temp()`: `Die temp` is equal to *T* (e.g. 25.0°C).
* `get_current()`: `Current` is equal to *V* / *R* (e.g. 0.364A).
* `get_power()`: `Power` is equal to *V*² / *R* (e.g. 4.36W).
* `get_energy()`: At *N*th iteration, `Energy` is equal to (*N* + 1) × *V*² / *R* (e.g. 26.2J at 5th iteration).
* `get_charge()`: At *N*th iteration, `Charge` is equal to (*N* + 1) × *V* / *R* (e.g. 2.18C at 5th iteration).
* `get_manufacturer_id()`: `Manufacturer` is somewhat reasonable for INA228 (e.g. `TI`).
* `get_deviceid()`: `Device ID` and `Revision` is somewhat reasonable for INA228 (e.g.`0x228` and `0x1` correspondingly).

Here, "equal" means approximate euqality. Let measurements have a 5..10% disagreement.

### Automated run

#### pytest

If you want to use pytest, install it into venv:

```console
.venv/bin/pip install pytest
```

And then run:

```console
.venv/bin/python -m pytest
```

It will also test the module installed into your venv.

#### tox

Install tox (somehow like `apt install tox`) and all Python versions you're up to test the project with.
For now, tox can test the project with Python versions 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, and 3.15.

Run it from the root directory of the project:

```console
tox
```

It will automatically build the package for each of the environments,
so you may skip all preparation steps, including building the package.
