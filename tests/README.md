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

#### Test behavior

Test will use supplied `stub_regmap.py` by default, not the real INA228.
It is a dump of registers once performed on the live INA228, and used by test so it will not depend on hardware.

If you want your own stub regmap, generate it by running `./map.sh > stub_regmap.py` on the system with live INA228.
You may need to edit bus number and slave address in `map.sh`,
and don't forget to install `i2cget` with something like `apt install i2c-tools` prior to running this.

#### Testing on live INA228

If you want to use live INA228 instead, specify bus, address, and shunt resistance in command line like this:

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
