class mock_SMBus:

    def __init__(self, regmap):
        self._regmap = regmap

    def read_i2c_block_data(self, address, register, length):
        assert(len(self._regmap[register]) == length)
        return self._regmap[register]


    def write_i2c_block_data(self, address, register, bytes):
        pass
