class mock_SMBus:
    """A mock of SMBus interface provided by smbus2 module.

    Uses the regmap dict that is a dump of INA228 registers.
    Regmap is a dict of lists representing the register contents.
    Each item in this dict has a key representing the register address,
    and a value that is a list of consecutive bytes one can read from
    this emulated register.

    Example of a regmap element (5-byte register with address of 0x0a):
        0x0a: [0x00, 0x00, 0x04, 0x63, 0xf5]
    """

    def __init__(self, regmap):
        """Create a mock SMBus object.

        Args:
            regmap: A regmap dict to use.

        Returns:
            SMBus-like object able to handle read/write block data calls.
        """
        self._regmap = regmap

    def read_i2c_block_data(self, address, register, length):
        """Emulate a read from some register
        (return corresponding bytes from regmap).

        Args:
            address: Slave address of INA228 (ignored).
            register: Register to emulate read from.
            length: Length of data to be read (must match the register size).

        Returns:
            List of bytes pretending to be read from the register.
        """
        assert(len(self._regmap[register]) == length)
        return self._regmap[register]


    def write_i2c_block_data(self, address, register, bytes):
        """Emulate a write into some register (actually do nothing).

        Args:
            address: Slave address of INA228 (ignored).
            register: Register to emulate write to (ignored).
            bytes: Bytes pretending to be written (ignored).

        Returns:
            Nothing.
        """
        pass
