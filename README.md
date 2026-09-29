# INA228
Driver for TI INA228 with SMBUS

## Building

Just run:

```
python3 -m build
```

## Requirements

For mow, it relies on `smbus2` module.

## Testing

After building the package, create venv:

```
python3 -m venv .venv
```

Install the module:

```
.venv/bin/pip install dist/ina228-0.0.1-py3-none-any.whl --force-reinstall
```

Run the test:

```
.venv/bin/python tests/test.py
```

Test will use supplied `stub_regmap.py`, not the real INA228.
If you want your own one, generate it by running `./map.sh > stub_regmap.py` on the system with live INA228.
You may need to edit bus number and slave address in `map.sh` though.
And remember to install `i2cget` with something like `apt install i2c-tools` prior to running this.

If you want to use pytest, install it into venv:

```
.venv/bin/pip install pytest
```

And then run:

```
.venv/bin/python -m pytest
```
