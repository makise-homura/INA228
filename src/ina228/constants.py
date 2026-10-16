class Constants:

    # Default parameters
    DEFAULT_PORT = 1
    DEFAULT_ADDRESS = 0x45
    DEFAULT_SHUNT_OHMS = 0.025
    DEFAULT_SHUNT_TEMPCO_VALUE = 0

    #############################################################
    # INA228 Reset bytes for CONFIG [15] / [14]
    # Description:
    # RST - Generates a system reset that is the same as power-on reset.
    # RSTACC - Resets the contents of accumulation registers ENERGY and CHARGE to 0
    #############################################################
    RST_NBIT = 15
    RSTACC_NBIT = 14

    #############################################################
    # INA228 Initial conversion delay CONFIG [13:6]
    # Description: Delay for initial ADC conversion in steps of 2 ms
    # Values:
    # 0x0 - 0 seconds (default)
    # 0x1 - 2 ms
    # 0xFF - 510ms
    #############################################################
    CONVERSION_DELAY = 0
    CONVDLY_NBIT = 6

    #############################################################
    # INA228 Temperature compensation CONFIG [5]
    # Description: Enables temperature compensation of an external shunt
    # Values:
    # 0x0 - disabled (default)
    # 0x1 - enabled
    #############################################################
    TEMP_COMP = 0
    TEMPCOMP_NBIT = 5

    #############################################################
    # INA228 ADC Shunt full scale range selection CONFIG [4]
    # Description: Shunt full scale range selection across IN+ and IN–.
    # Values:
    # 0x0 - ±163.84 mV (default)
    # 0x1 - ±40.96 mV
    #############################################################
    ADCRANGE = 0
    ADCRANGE_NBIT = 4

    #############################################################
    # INA228 ADC Mode
    # Description: The user can set the MODE bits for continuous or
    # triggered mode on bus voltage, shunt voltage or temperature measurement.
    #
    # Values:
    # 0x0h = Shutdown
    # 0x1h = Triggered bus voltage, single shot
    # 0x2h = Triggered shunt voltage, single shot
    # 0x3h = Triggered shunt voltage and bus voltage, single shot
    # 0x4h = Triggered temperature, single shot
    # 0x5h = Triggered temperature and bus voltage, single shot
    # 0x6h = Triggered temperature and shunt voltage, single shot
    # 0x7h = Triggered bus voltage, shunt voltage and temperature, single shot
    # 0x8h = Shutdown
    # 0x9h = Continuous bus voltage only
    # 0xAh = Continuous shunt voltage only
    # 0xBh = Continuous shunt and bus voltage
    # 0xCh = Continuous temperature only
    # 0xDh = Continuous bus voltage and temperature
    # 0xEh = Continuous temperature and shunt voltage
    # 0xFh = Continuous bus voltage, shunt voltage and temperature (default)
    #############################################################
    ADC_MODE = 0xB
    ADC_MODE_NBIT = 12

    #############################################################
    # INA228 ADC conversion time of bus voltage measurement.
    # Description: Sets the conversion time of the bus voltage measurement
    #
    # Values:
    # 0x00h = 50 μs
    # 0x01h = 84 μs
    # 0x02h = 150 μs
    # 0x03h = 280 μs
    # 0x04h = 540 μs
    # 0x05h = 1052 μs
    # 0x06h = 2074 μs
    # 0x07h = 4120 μs
    #############################################################
    VBUS_CONV_TIME = 0x05
    VBUS_CONV_TIME_NBIT = 0x09

    #############################################################
    # INA228 ADC conversion time of shunt voltage measurement.
    # Description: Sets the conversion time of the shunt voltage measurement
    #
    # Values:
    # 0x00h = 50 μs
    # 0x01h = 84 μs
    # 0x02h = 150 μs
    # 0x03h = 280 μs
    # 0x04h = 540 μs
    # 0x05h = 1052 μs
    # 0x06h = 2074 μs
    # 0x07h = 4120 μs
    #############################################################
    VSHCT_CONV_TIME = 0x05
    VSHCT_CONV_TIME_NBIT = 0x06

    #############################################################
    # INA228 ADC conversion time of temperatrure measurement.
    # Description: Sets the conversion time of the temperature measurement
    #
    # Values:
    # 0x00h = 50 μs
    # 0x01h = 84 μs
    # 0x02h = 150 μs
    # 0x03h = 280 μs
    # 0x04h = 540 μs
    # 0x05h = 1052 μs
    # 0x06h = 2074 μs
    # 0x07h = 4120 μs
    #############################################################
    VTCT_CONV_TIME = 0x05
    VTCT_CONV_TIME_NBIT = 0x03


    #############################################################
    # INA228 ADC sample averaging count.
    #
    # Values:
    # 0x0h = 1
    # 0x1h = 4
    # 0x2h = 16
    # 0x3h = 64
    # 0x4h = 128
    # 0x5h = 256
    # 0x6h = 512
    # 0x7h = 1024
    #############################################################
    ADC_AVG = 3
    AVG_NBIT = 0
