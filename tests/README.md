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

## Testing

### Manual run

Run the test like this:

```console
.venv/bin/python tests/test.py
```

It will test the module you've just installed in your venv.

#### Test behavior

By default, test will perform 10 iterations with a 0.1-second interval on an emulated INA228 (not the real one even if it exists).
Each iteration will read out VBUS voltage, current, power, shunt voltage, die temp, energy, and charge using INA228 module,
and print them out along with iteration number and current time.

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

Test will perform 5 iterations with a 1-second interval.

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
