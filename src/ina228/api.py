"""Driver for TI INA228 voltage/current sensor located on SMBus.

Original code by @megalloid.
Python module created and maintained by @makise_homura.

Typical usage:
    from ina228 import INA228
    ina228 = INA228(bus, addr)
    ina228.configure()
    print('Voltage: ', ina228.get_vbus_voltage())
    print('Current: ', ina228.get_current())
    print('Power: ', ina228.get_power())

Need to fix:
    1) Value of VSHUNT is needed to be multiplied by 10 to get correct value.
"""

import time

from smbus2 import SMBus

from .testing import mock_SMBus

# INA228 Address
INA228_PORT = 1
INA228_ADDRESS = 0x45
INA228_SHUNT_OHMS = 0.025
INA228_SHUNT_TEMPCO_VALUE = 0

#############################################################
# INA228 Reset bytes for CONFIG [15] / [14]
# Description:
# RST - Generates a system reset that is the same as power-on reset.
# RSTACC - Resets the contents of accumulation registers ENERGY and CHARGE to 0
#############################################################
INA228_RST_NBIT = 15
INA228_RSTACC_NBIT = 14

#############################################################
# INA228 Initial conversion delay CONFIG [13:6]
# Description: Delay for initial ADC conversion in steps of 2 ms
# Values:
# 0x0 - 0 seconds (default)
# 0x1 - 2 ms
# 0xFF - 510ms
#############################################################
INA228_CONVERSION_DELAY = 0
INA228_CONVDLY_NBIT = 6

#############################################################
# INA228 Temperature compensation CONFIG [5]
# Description: Enables temperature compensation of an external shunt
# Values:
# 0x0 - disabled (default)
# 0x1 - enabled
#############################################################
INA228_TEMP_COMP = 0
INA228_TEMPCOMP_NBIT = 5

#############################################################
# INA228 ADC Shunt full scale range selection CONFIG [4]
# Description: Shunt full scale range selection across IN+ and IN–.
# Values:
# 0x0 - ±163.84 mV (default)
# 0x1 - ±40.96 mV
#############################################################
INA228_ADCRANGE = 0
INA228_ADCRANGE_NBIT = 4

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
INA228_ADC_MODE = 0xB
INA228_ADC_MODE_NBIT = 12

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
INA228_VBUS_CONV_TIME = 0x05
INA228_VBUS_CONV_TIME_NBIT = 0x09

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
INA228_VSHCT_CONV_TIME = 0x05
INA228_VSHCT_CONV_TIME_NBIT = 0x06

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
INA228_VTCT_CONV_TIME = 0x05
INA228_VTCT_CONV_TIME_NBIT = 0x03


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
INA228_ADC_AVG = 3
INA228_AVG_NBIT = 0


#############################################################
# INA228 ADC alerts signal
#############################################################
INA228_ALERT_MEMSTAT = 0
INA228_ALERT_CNVRF = 1
INA228_ALERT_POL = 2
INA228_ALERT_BUSUL = 3
INA228_ALERT_BUSOL = 4
INA228_ALERT_SHNTUL = 5
INA228_ALERT_SHNTOL = 6
INA228_ALERT_TMPOL = 7
INA228_ALERT_MATHOF = 9
INA228_ALERT_CHARGEOF = 10
INA228_ALERT_ENERGYOF = 11
INA228_ALERT_APOL = 12
INA228_ALERT_SLOWALERT = 13
INA228_ALERT_CNVR = 14
INA228_ALERT_ALATCH = 15


class INA228:
    """Main INA228 interface"""

    __INA228_CONFIG         = 0x00
    __INA228_ADC_CONFIG     = 0x01
    __INA228_SHUNT_CAL      = 0x02
    __INA228_SHUNT_TEMPCO   = 0x03
    __INA228_VSHUNT         = 0x04
    __INA228_VBUS           = 0x05
    __INA228_DIETEMP        = 0x06
    __INA228_CURRENT        = 0x07
    __INA228_POWER          = 0x08
    __INA228_ENERGY         = 0x09
    __INA228_CHARGE         = 0x0A
    __INA228_DIAG_ALRT      = 0x0B
    __INA228_SOVL           = 0x0C
    __INA228_SUVL           = 0x0D
    __INA228_BOVL           = 0x0E
    __INA228_BUVL               = 0x0F
    __INA228_TEMP_LIMIT         = 0x10
    __INA228_PWR_LIMIT          = 0x11
    __INA228_MANUFACTURER_ID    = 0x3E
    __INA228_DEVICE_ID          = 0x3F

    def __init__(self, busnum = INA228_PORT, address = INA228_ADDRESS, shunt_ohms = INA228_SHUNT_OHMS, stub_regmap = None):
        """Create INA228 instance.

        Args:
            busnum: SMBus bus number INA228 connected to.
            address: SMBus slave address of INA228.
            shunt_ohms: Shunt value for current measurements.
            stub_regmap: Used in tests to emulate real INA228.

        Returns:
            Uninitialized INA228 instance linked to specific SMBus location.

        Raises:
            Any exception smbus2.SMBus() may raise.
        """

        self._address = address
        self._i2c = mock_SMBus(stub_regmap) if stub_regmap else SMBus(busnum)
        self._shunt_ohms = shunt_ohms
        self._stub_regmap = stub_regmap

    def __convert2comp2float(self, twocompdata, nrofbit, factor):

        negative = (1 << (nrofbit - 1))

        value = twocompdata

        if(value > negative):
            value = (value - (2*negative)) * factor
        else:
            value = value * factor

        return value

    def __convertfloat22comp(self, value, nrofbit, factor):

        if (value >= 0):
            twocompdata = int(value / factor)

        else:
            twocompdata = int(value * (-1) / factor)
            twocompdata = ~twocompdata
            twocompdata = twocompdata + 1

        return twocompdata & ((1 << nrofbit) - 1)


    def read_register40(self, register):

        result = self._i2c.read_i2c_block_data(self._address, register, 5)

        return int.from_bytes(result,'big')


    def read_register24(self, register):

        result = self._i2c.read_i2c_block_data(self._address, register, 3)

        return int.from_bytes(result,'big')


    def read_register16(self, register):

        result = self._i2c.read_i2c_block_data(self._address, register, 2)

        return int.from_bytes(result,'big')


    def write_register16(self, register, register_value):

        register_bytes = list(register_value.to_bytes(2,'big'))

        self._i2c.write_i2c_block_data(self._address, register, register_bytes)


    def get_current_lsb(self):

        if(INA228_ADCRANGE == 0):
            adc_max_voltage = 163.84e-3   # Table 1 in datasheet
        else:
            adc_max_voltage = 40.96e-3   # Table 1 in datasheet

        current_lsb = (adc_max_voltage / self._shunt_ohms) / 524288   # Equation (2) in datasheet

        return current_lsb


    def __get_shunt_conv_factor(self):

        if(INA228_ADCRANGE == 1):
            conversion_factor = 312.5e-9   # Table 1 in datasheet
        else:
            conversion_factor = 78.125e-9   # Table 1 in datasheet

        return conversion_factor

    def __get_vbus_conv_factor(self):

        return 195.3125e-6   # Table 1 in datasheet


    def __get_temp_conv_factor(self):

        return 7.8125e-3   # Table 1 in datasheet


    def reset_all(self):
        """Perform the power-on reset of the chip.

        Args:
            None.

        Returns:
            Nothing.
        """

        config = self.read_register16(self.__INA228_CONFIG)

        data = 1 << INA228_RST_NBIT

        config = config | data

        self.write_register16(self.__INA228_CONFIG, config)


    def reset_energy(self):
        """Reset energy and charge counters.

        Args:
            None.

        Returns:
            Nothing.
        """

        config = self.read_register16(self.__INA228_CONFIG)

        data = 1 << INA228_RSTACC_NBIT

        config = config | data

        self.write_register16(self.__INA228_CONFIG, config)


    def set_config(self):

        # Write settings to CONFIG register

        config = self.read_register16(self. __INA228_CONFIG)

        config = config | (INA228_CONVERSION_DELAY << INA228_CONVDLY_NBIT) | (INA228_TEMP_COMP << INA228_TEMPCOMP_NBIT) | (INA228_ADCRANGE << INA228_ADCRANGE_NBIT)

        self.write_register16(self.__INA228_CONFIG, config)


    def set_adc_config(self):

        # Write settings to ADC CONFIG register

        config = self.read_register16(self. __INA228_ADC_CONFIG)

        config = config | (INA228_ADC_MODE << INA228_ADC_MODE_NBIT) | (INA228_VBUS_CONV_TIME << INA228_VBUS_CONV_TIME_NBIT ) | (INA228_VSHCT_CONV_TIME << INA228_VSHCT_CONV_TIME_NBIT) | (INA228_VTCT_CONV_TIME << INA228_VTCT_CONV_TIME_NBIT) | (INA228_ADC_AVG << INA228_AVG_NBIT)

        self.write_register16(self.__INA228_ADC_CONFIG, config)


    def shunt_calib(self):

        calib_value = int(13107.2e6 * self.get_current_lsb() * self._shunt_ohms)   # Equation (1) in datasheet

        self.write_register16(self.__INA228_SHUNT_CAL, calib_value)


    def shunt_tempco(self):

        self.write_register16(self.__INA228_SHUNT_TEMPCO, INA228_SHUNT_TEMPCO_VALUE)


    def configure(self):
        """Performs initial INA228 configuration.
        Always call this prior to get any data from INA228.

        Args:
            None.

        Returns:
            Nothing.
        """

        self.reset_all()

        self.set_config()
        self.set_adc_config()

        self.shunt_calib()

        if INA228_TEMP_COMP:
            self.shunt_tempco()

        time.sleep(0.1)


    def get_shunt_voltage(self):
        """Read voltage on the shunt resistor.

        Args:
            None.

        Returns:
            Voltage in volts.
        """

        raw = self.read_register24(self.__INA228_VSHUNT)

        vshunt = (self.__convert2comp2float(raw >> 4, 20, self.__get_shunt_conv_factor())) * 10   # Table 11 in datasheet, for *10 see Known Bugs

        return vshunt


    def get_vbus_voltage(self):
        """Read voltage on the V+/V- terminals.

        Args:
            None.

        Returns:
            Voltage in volts.
        """

        raw = self.read_register24(self.__INA228_VBUS)

        vbus = self.__convert2comp2float(raw >> 4, 20, self.__get_vbus_conv_factor())   # Table 12 in datasheet

        return vbus


    def get_temp(self):
        """Read die temperature.

        Args:
            None.

        Returns:
            Temperature in Celsius.
        """

        raw = self.read_register16(self.__INA228_DIETEMP)

        temp = self.__convert2comp2float(raw, 16, self.__get_temp_conv_factor())   # Table 13 in datasheet

        return temp


    def get_current(self):
        """Read current through I+/I- terminals.

        Args:
            None.

        Returns:
            Current in amperes.
        """

        raw = self.read_register24(self.__INA228_CURRENT)

        current = self.__convert2comp2float(raw >> 4, 20, self.get_current_lsb())   # Equation (3) in datasheet

        return current


    def get_power(self):
        """Read calculated power (a product of voltage and current).

        Args:
            None.

        Returns:
            Power in watts.
        """

        raw = self.read_register24(self.__INA228_POWER)

        power = raw * 3.2 * self.get_current_lsb()   # Equation (4) in datasheet

        return power


    def get_energy(self):
        """Read integral energy (a product of power and time since last reset).

        Args:
            None.

        Returns:
            Energy in joules.
        """

        raw = self.read_register40(self.__INA228_ENERGY)

        energy = raw * 3.2 * 16 * self.get_current_lsb()   # Equation (5) in datasheet

        return energy


    def get_charge(self):
        """Read charge spent (a product of current and time since last reset).

        Args:
            None.

        Returns:
            Charge in coulombs.
        """

        raw = self.read_register40(self.__INA228_CHARGE)

        charge = self.__convert2comp2float(raw, 40, self.get_current_lsb())   # Equation (6) in datasheet

        return charge


    def get_diag_alerts(self, alert):
        """Test if specific alert is active.

        Args:
            alert: Alert to read (any of INA228_ALERT_* constants).

        Returns:
            String representation of specific alert, or empty string if nothing to tell (e.g. no chosen alert).
        """

        raw = self.read_register16(self.__INA228_DIAG_ALRT)

        if(alert == INA228_ALERT_ALATCH):
            if (raw & 0x1) == 0x0:
                return 'MEMSTAT: Checksum error is detected in the device trim memory space'

        elif(alert == INA228_ALERT_CNVRF):
            if (raw & 0x2) == 0x1:
                return 'CNVRF: Conversion is completed'

        elif(alert == INA228_ALERT_BUSUL):
            if (raw & 0x4) == 0x1:
                return 'BUSUL: Bus voltage measurement falls below the threshold limit in the bus under-limit register'

        elif(alert == INA228_ALERT_BUSOL):
            if (raw & 0x8) == 0x1:
                return 'BUSOL: Bus voltage measurement exceeds the threshold limit in the bus over-limit register'

        elif(alert == INA228_ALERT_SHNTUL):
            if (raw & 0x10) == 0x1:
                return 'SHNTUL: Shunt voltage measurement falls below the threshold limit in the shunt under-limit register'

        elif(alert == INA228_ALERT_SHNTOL):
            if (raw & 0x40) == 0x1:
                return 'SHNTOL: Shunt voltage measurement exceeds the threshold limit in the shunt over-limit register'

        elif(alert == INA228_ALERT_TMPOL):
            if (raw & 0x80) == 0x1:
                return 'TMPOL: Temperature measurement exceeds the threshold limit in the temperature over-limit register'

        elif(alert == INA228_ALERT_MATHOF):
            if (raw & 0x100) == 0x1:
                return 'MATHOF: Arithmetic operation resulted in an overflow error'

        elif(alert == INA228_ALERT_CHARGEOF):
            if (raw & 0x200) == 0x1:
                return 'CHARGEOF: 40 bit CHARGE register has overflowed'

        elif(alert == INA228_ALERT_ENERGYOF):
            if (raw & 0x400) == 0x1:
                return 'ENERGYOF: 40 bit ENERGY register has overflowed'

        elif(alert == INA228_ALERT_APOL):
            if (raw & 0x800) == 0x1:
                return 'APOL: Alert pin polarity inverted (active-high, open-drain)'
            else:
                return 'APOL: Alert pin polarity normale (active-low, open-drain)'

        elif(alert == INA228_ALERT_SLOWALERT):
            if (raw & 0x2000) == 0x1:
                return 'SLOWALERT: ALERT function is asserted on the completed averaged value. ALERT comparison on averaged value'
            else:
                return 'SLOWALERT: ALERT comparison on non-averaged (ADC) value'

        elif(alert == INA228_ALERT_CNVR):
            if (raw & 0x4000) == 0x1:
                return 'CNVR: Alert pin to be asserted when the Conversion Ready Flag (bit 1) is asserted, indicating that a conversion cycle has completed. Enables conversion ready flag on ALERT pin'
            else:
                return 'CNVR: Disable conversion ready flag on ALERT pin'

        elif(alert == INA228_ALERT_ALATCH):
            if (raw & 0x8000) == 0x1:
                return 'ALATCH: Latched'
            else:
                return 'ALATCH: Transparent'

        return ''


    def set_shunt_overvoltage(self, value):
        """Set high alert threshold of the shunt resistor voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = __convertfloat22comp(value, 16, self.__get_shunt_conv_factor())   # Table 19 in datasheet

        self.read_register16(self.__INA228_SOVL)

        self.write_register16(self.__INA228_SOVL, data)


    def set_shunt_undervoltage(self, value):
        """Set low alert threshold of the shunt resistor voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = __convertfloat22comp(value, 16, self.__get_shunt_conv_factor())   # Table 20 in datasheet

        self.read_register16(self.__INA228_SUVL)

        self.write_register16(self.__INA228_SUVL, data)


    def set_bus_overvoltage(self, value):
        """Set high alert threshold of the V+/V- terminals voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = value / self.__get_vbus_conv_factor()   # Table 21 in datasheet

        self.read_register16(self.__INA228_BOVL)

        self.write_register16(self.__INA228_BOVL, data)


    def set_bus_undervoltage(self, value):
        """Set low alert threshold of the V+/V- terminals voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = value / self.__get_vbus_conv_factor()   # Table 22 in datasheet

        self.read_register16(self.__INA228_BUVL)

        self.write_register16(self.__INA228_BUVL, data)


    def set_temp_limit(self, value):
        """Set high alert threshold of the die temperature.

        Args:
            value: Limit in Celsius.

        Returns:
            Nothing.
        """

        data = __convertfloat22comp(value, 16, self.__get_temp_conv_factor())   # Table 23 in datasheet

        self.read_register16(self.__INA228_TEMP_LIMIT)

        self.write_register16(self.__INA228_TEMP_LIMIT, data)


    def set_power_overlimit(self, value):
        """Set high alert threshold of the load power.

        Args:
            value: Limit in watts.

        Returns:
            Nothing.
        """

        data = value / (3.2 * self.get_current_lsb())   # Equation (4) and Table 24 in datasheet

        self.read_register16(self.__INA228_PWR_LIMIT)

        self.write_register16(self.__INA228_PWR_LIMIT, data)


    def get_manufacturer_id(self):
        """Read manufacturer ID.

        Args:
            None.

        Returns:
            A string of 2 characters containing manufacturer ID.
        """

        raw_id = self.read_register16(self.__INA228_MANUFACTURER_ID)

        return raw_id.to_bytes(2,'big').decode()


    def get_deviceid(self):
        """Read device ID.

        Args:
            None.

        Returns:
            A tuple of (device ID, device revision).
        """

        raw_id = self.read_register16(self.__INA228_DEVICE_ID)

        return (hex(raw_id >> 4), hex(raw_id & 0xF))
