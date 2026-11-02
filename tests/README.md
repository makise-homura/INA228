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

## Test suites

### test_measurements.py

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

#### Test behavior

Test will perform (in the case of real INA228, see below) 6 iterations (0th till 5th) with a 1-second interval.
Each iteration will read out VBUS voltage, current, power, shunt voltage, die temp, energy, and charge using INA228 module,
and print them out along with iteration number and current time.
If it has not thrown an exception, it always ends successfully.

By default, test will use INA228 at bus 0, address 0x40, and shunt resistance 0.002 Ohms.
If you have different values, specify bus, address, and/or shunt resistance in command line like this:

```console
.venv/bin/python tests/test_measurements.py --busn 0 --addr 0x40 --shunt 0.002
```

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

Here, "equal" means approximate equality. Let measurements have a 5..10% disagreement.

#### INA228 emulation

To use emulated INA228, specify `--stub` when invoking test.
In this case, it will perform 11 iterations (0th till 10th) with a 0.1-second interval.

Emulation will use supplied `stub_regmap.py` by default.
It is a dump of registers once captured on the live INA228, and used by the test so it will not depend on hardware.

If you want your own stub regmap, generate it by running `./map.sh > stub_regmap.py` on the system with live INA228.
Don't forget to install `i2cget` with something like `apt install i2c-tools` prior to running this.

By default, `map.sh` expects to find INA228 on bus 0, address 0x40.
You may specify different bus number and/or slave address with environment variables, like this:

```console
bus=2 addr=0x42 ./map.sh > stub_regmap.py
```

### test_values.py

This test does require actual INA228, and it tests the following methods (along with constructor and `configure()`):

* `get_shunt_voltage()`: Read voltage on the shunt resistor.
* `get_vbus_voltage()`: Read voltage on the V+/V- terminals.
* `get_current()`: Read current through I+/I- terminals.
* `get_power()`: Read calculated power (a product of voltage and current).
* `get_energy()`: Read integral energy (a product of power and time since last reset).
* `get_charge()`: Read charge spent (a product of current and time since last reset).

#### Test behavior

Test will read out one by one:
* VBUS voltage,
* current,
* power,
* shunt voltage,
* energy after 5-second pause,
* and charge after another 5-second pause.
Then, it will compare these values with calculated ones.
If they does not match, test will fail an assertion.

For measurements to match, current and voltage applied to INA228 must be known to the test.
By default, it's 12.0V and 0.364A.
If you have different setup, specify your values like that (in volts and amperes, respectively):

```console
.venv/bin/python tests/test_measurements.py --voltage 5.1 --current 0.51
```

By default, test will use INA228 at bus 0, address 0x40, and shunt resistance 0.002 Ohms.
If you have different values, specify bus, address, and/or shunt resistance in command line like this:

```console
.venv/bin/python tests/test_measurements.py --busn 0 --addr 0x40 --shunt 0.002
```

Of course, you may pass any combination of the arguments above to the test.

*Note 1*: test does not support `--stub`, and skipped while ran by pytest or tox with `--stub`.

*Note 2*: Before each read INA228 will be reinitailized and let settle for 1 second.
It is required due to integral measurements that is accumulated since that reset.
These measurements have an additional delay of 5 seconds for value to accumulate.

Approximate equality tolerance for this test is assumed to be 10%.

### test_reset.py

This test does require actual INA228, and it tests the `reset_energy()` method (along with constructor and `configure()`).

#### Test behavior

Test will do the following:
* initialize INA228,
* wait for specific time `INTEGRATION_TIME_1`,
* read energy and charge, and compare them to estimations,
* reset energy and charge counters by calling `reset_energy()`,
* wait for specific time `INTEGRATION_TIME_2`,
* read energy and charge again, and compare them to estimations for the new time,
* reset energy and charge agian.
If on each comparison measurements do not match the estimations, test will fail.

For measurements to match, current and voltage applied to INA228 is measured by the test in the beginning.

By default, test will use INA228 at bus 0, address 0x40, and shunt resistance 0.002 Ohms.
If you have different values, specify bus, address, and/or shunt resistance in command line like this:

```console
.venv/bin/python tests/test_measurements.py --busn 0 --addr 0x40 --shunt 0.002
```

Of course, you may pass any combination of the arguments above to the test.

*Note 1*: test does not support `--stub`, and skipped while ran by pytest or tox with `--stub`.

Approximate equality tolerance for this test is assumed to be 10%.

### test_alerts.py

This test does require actual INA228, and it tests the following methods (along with constructor and `configure()`):
* `get_diag_alerts()`: Read alerts.
* `alert_message()`: Get text message for specific alert.
* `set_alert_bits()`: Set alert configuration.
* `set_shunt_overvoltage()`: Set high alert threshold of the shunt resistor voltage.
* `set_shunt_undervoltage()`: Set low alert threshold of the shunt resistor voltage.
* `set_bus_overvoltage()`: Set high alert threshold of the V+/V- terminals voltage.
* `set_bus_undervoltage()`: Set low alert threshold of the V+/V- terminals voltage.
* `set_temp_limit()`: Set high alert threshold of the die temperature.
* `set_power_overlimit()`: Set high alert threshold of the load power.

It tests these alerts:
* `Alert.CNVRF`: Conversion is completed.
* `Alert.BUSUL`: Bus voltage measurement falls below the threshold limit in the bus under-limit register.
* `Alert.BUSOL`: Bus voltage measurement exceeds the threshold limit in the bus over-limit register.
* `Alert.SHNTUL`: Shunt voltage measurement falls below the threshold limit in the shunt under-limit register.
* `Alert.SHNTOL`: Shunt voltage measurement exceeds the threshold limit in the shunt over-limit register.
* `Alert.TMPOL`: Temperature measurement exceeds the threshold limit in the temperature over-limit register.
* `Alert.POL`: Power measurement exceeds the threshold limit in the power over-limit register.

These alerts may not be tested in live environment, so no test (including this) can test it:
* `Alert.MEMSTAT`: Checksum error is detected in the device trim memory space.
* `Alert.MATHOF`: Arithmetic operation resulted in an overflow error.
* `Alert.CHARGEOF`: 40 bit CHARGE register has overflowed.
* `Alert.ENERGYOF`: 40 bit ENERGY register has overflowed.

Test these alert control bits:
* `Alert.ALATCH`: Alert Latch Enable. When set to 0 (Transparent mode), the alert flag (and pin) resets when the fault has been cleared. When set to 1 (Latch mode), the alert flag (and pin) remain active following a fault until the `get_diag_alerts()` called. Default: 0.

These alert control bits may not be tested in live environment, so no test (including this) can test it:
* `Alert.APOL`: Alert Polarity bit. Sets the Alert pin polarity. 0h = Normal (Active-low open-drain), 1h = Inverted (active-high). Default: 0.
* `Alert.SLOWALERT`: Generate alert on the average value. If set to 1, ALERT is asserted on the completed averaged value, otherwise on non-averaged (ADC) value. Default: 0.
* `Alert.CNVR`: Conversion ready. If set to 1, the Alert pin to be asserted on Alert.CNVRF. Default: 0.

#### Test behavior

Test will test `Alert.CNVRF` by checking it immediately after reset, and then every one of these alerts in both latched (`Alert.ALATCH`) and unlatched mode:
* `Alert.BUSUL`: Bus voltage measurement falls below the threshold limit in the bus under-limit register.
* `Alert.BUSOL`: Bus voltage measurement exceeds the threshold limit in the bus over-limit register.
* `Alert.SHNTUL`: Shunt voltage measurement falls below the threshold limit in the shunt under-limit register.
* `Alert.SHNTOL`: Shunt voltage measurement exceeds the threshold limit in the shunt over-limit register.
* `Alert.TMPOL`: Temperature measurement exceeds the threshold limit in the temperature over-limit register.
* `Alert.POL`: Power measurement exceeds the threshold limit in the power over-limit register.
If any of the alerts does not fire, latch, or disappear when they have to, test will fail an assertion.

Approximate threshold tolerance for this test is assumed to be 20%.
So, to trigger alert, it sets 80% of measured value to test value over-limit, and 120% to test value under-limit.
To test alert being cleared, values are being set the opposite way.

For alerts to work correctly, some non-zero current and voltage must be applied to INA228 before to the test,
and it must be presented to positive temperature noticeably above 0°C.
Consider at least 2V, 0.1A and 10°C as minimum values, but higher (not exceeding AMR of INA228) is better.

By default, test will use INA228 at bus 0, address 0x40, and shunt resistance 0.002 Ohms.
If you have different values, specify bus, address, and/or shunt resistance in command line like this:

```console
.venv/bin/python tests/test_measurements.py --busn 0 --addr 0x40 --shunt 0.002
```

Of course, you may pass any combination of the arguments above to the test.

*Note*: test does not support `--stub`, and skipped while ran by pytest or tox with `--stub`.

## Manual run

Run the test you want like this:

```console
.venv/bin/python tests/test_measurements.py
```

It will test the module you've just installed in your venv.

Use `--help` to see allowed arguments, or pass arguments that you want when invoking.

## Automated run

### pytest

If you want to use pytest, install it into venv:

```console
.venv/bin/pip install pytest
```

And then run:

```console
.venv/bin/python -m pytest
```

It will also test the module installed into your venv.

You may pass `--busn`, `--addr`, `--shunt`, `--stub`, `--voltage`, `--current` to pytest.

### tox

Install tox (somehow like `apt install tox`) and all Python versions you're up to test the project with.
For now, tox can test the project with Python versions 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, and 3.15.

Run it from the root directory of the project:

```console
tox
```

It will automatically build the package for each of the environments,
so you may skip all preparation steps, including building the package.

To pass arguments to pytest, specify them after `--`:

```console
tox -- --busn 1 --addr 0x40
```
