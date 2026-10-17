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
from enum import Enum

from smbus2 import SMBus

from .testing import mock_SMBus

from .constants import Constants

class Alert(Enum):
    """INA228 ADC alerts signal"""
    MEMSTAT = 0
    CNVRF = 1
    POL = 2
    BUSUL = 3
    BUSOL = 4
    SHNTUL = 5
    SHNTOL = 6
    TMPOL = 7
    MATHOF = 9
    CHARGEOF = 10
    ENERGYOF = 11
    APOL = 12
    SLOWALERT = 13
    CNVR = 14
    ALATCH = 15


class INA228:
    """Main INA228 interface"""

    class Register(Enum):
        CONFIG          = 0x00
        ADC_CONFIG      = 0x01
        SHUNT_CAL       = 0x02
        SHUNT_TEMPCO    = 0x03
        VSHUNT          = 0x04
        VBUS            = 0x05
        DIETEMP         = 0x06
        CURRENT         = 0x07
        POWER           = 0x08
        ENERGY          = 0x09
        CHARGE          = 0x0A
        DIAG_ALRT       = 0x0B
        SOVL            = 0x0C
        SUVL            = 0x0D
        BOVL            = 0x0E
        BUVL            = 0x0F
        TEMP_LIMIT      = 0x10
        PWR_LIMIT       = 0x11
        MANUFACTURER_ID = 0x3E
        DEVICE_ID       = 0x3F


    def __init__(self, busnum = Constants.DEFAULT_PORT, address = Constants.DEFAULT_ADDRESS, shunt_ohms = Constants.DEFAULT_SHUNT_OHMS, tempco = Constants.DEFAULT_SHUNT_TEMPCO_VALUE, stub_regmap = None):
        """Create INA228 instance.

        Args:
            busnum: SMBus bus number INA228 connected to.
            address: SMBus slave address of INA228.
            shunt_ohms: Shunt value for current measurements.
            tempco: Shunt temperature correction value (See part 7.3.6 of the datasheet).
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
        self._tempco = tempco

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


    def __read_register40(self, register):

        result = self._i2c.read_i2c_block_data(self._address, register.value, 5)

        return int.from_bytes(result,'big')


    def __read_register24(self, register):

        result = self._i2c.read_i2c_block_data(self._address, register.value, 3)

        return int.from_bytes(result,'big')


    def __read_register16(self, register):

        result = self._i2c.read_i2c_block_data(self._address, register.value, 2)

        return int.from_bytes(result,'big')


    def __write_register16(self, register, register_value):

        register_bytes = list(register_value.to_bytes(2,'big'))

        self._i2c.write_i2c_block_data(self._address, register.value, register_bytes)


    def __get_current_lsb(self):

        if(Constants.ADCRANGE == 0):
            adc_max_voltage = 163.84e-3   # Table 1 in datasheet
        else:
            adc_max_voltage = 40.96e-3   # Table 1 in datasheet

        current_lsb = (adc_max_voltage / self._shunt_ohms) / 524288   # Equation (2) in datasheet

        return current_lsb


    def __get_shunt_conv_factor(self):

        if(Constants.ADCRANGE == 1):
            conversion_factor = 312.5e-9   # Table 1 in datasheet
        else:
            conversion_factor = 78.125e-9   # Table 1 in datasheet

        return conversion_factor

    def __get_vbus_conv_factor(self):

        return 195.3125e-6   # Table 1 in datasheet


    def __get_temp_conv_factor(self):

        return 7.8125e-3   # Table 1 in datasheet


    def __set_config(self):

        # Write settings to CONFIG register

        config = self.__read_register16(self.Register.CONFIG)

        config = config | (self._conversion_delay << Constants.CONVDLY_NBIT) | (self._temp_comp << Constants.TEMPCOMP_NBIT) | (self._adcrange << Constants.ADCRANGE_NBIT)

        self.__write_register16(self.Register.CONFIG, config)


    def __set_adc_config(self):

        # Write settings to ADC CONFIG register

        config = self.__read_register16(self.Register.ADC_CONFIG)

        config = config | (self._adc_mode << Constants.ADC_MODE_NBIT) | (self._vbus_conv_time << Constants.VBUS_CONV_TIME_NBIT ) | (self._vshct_conv_time << Constants.VSHCT_CONV_TIME_NBIT) | (self._vtct_conv_time << Constants.VTCT_CONV_TIME_NBIT) | (self._adc_avg << Constants.AVG_NBIT)

        self.__write_register16(self.Register.ADC_CONFIG, config)


    def __shunt_calib(self):

        calib_value = int(13107.2e6 * self.__get_current_lsb() * self._shunt_ohms)   # Equation (1) in datasheet

        self.__write_register16(self.Register.SHUNT_CAL, calib_value)


    def __shunt_tempco(self):

        self.__write_register16(self.Register.SHUNT_TEMPCO, self._tempco)


    def __reset_all(self):

        config = self.__read_register16(self.Register.CONFIG)

        data = 1 << Constants.RST_NBIT

        config = config | data

        self.__write_register16(self.Register.CONFIG, config)


    def reset_energy(self):
        """Reset energy and charge counters.

        Args:
            None.

        Returns:
            Nothing.
        """

        config = self.__read_register16(self.Register.CONFIG)

        data = 1 << Constants.RSTACC_NBIT

        config = config | data

        self.__write_register16(self.Register.CONFIG, config)


    def configure(self, conversion_delay = Constants.CONVERSION_DELAY, temp_comp = Constants.TEMP_COMP, adcrange = Constants.ADCRANGE, adc_mode = Constants.ADC_MODE, vbus_conv_time = Constants.VBUS_CONV_TIME, vshct_conv_time = Constants.VSHCT_CONV_TIME, vtct_conv_time = Constants.VTCT_CONV_TIME, adc_avg = Constants.ADC_AVG):
        """Performs INA228 reset and initial configuration.
        Always call this prior to get any data from INA228.
        See detailed description of arguments in Tables 7 and 8 of the datasheet.

        Args:
            conversion_delay: Initial conversion delay.
            temp_comp: Temperature compensation.
            adcrange: ADC shunt full scale range selection.
            adc_mode: ADC mode.
            vbus_conv_time: ADC conversion time of bus voltage measurement.
            vshct_conv_time: ADC conversion time of shunt voltage measurement.
            vtct_conv_time: ADC conversion time of temperatrure measurement.
            adc_avg: ADC sample averaging count.

        Returns:
            Nothing.
        """

        self._conversion_delay = conversion_delay
        self._temp_comp = temp_comp
        self._adcrange = adcrange
        self._adc_mode = adc_mode
        self._vbus_conv_time = vbus_conv_time
        self._vshct_conv_time = vshct_conv_time
        self._vtct_conv_time = vtct_conv_time
        self._adc_avg = adc_avg

        self.__reset_all()

        self.__set_config()
        self.__set_adc_config()

        self.__shunt_calib()

        if self._temp_comp:
            self.__shunt_tempco()

        time.sleep(0.1)


    def get_shunt_voltage(self):
        """Read voltage on the shunt resistor.

        Args:
            None.

        Returns:
            Voltage in volts.
        """

        raw = self.__read_register24(self.Register.VSHUNT)

        vshunt = (self.__convert2comp2float(raw >> 4, 20, self.__get_shunt_conv_factor())) * 10   # Table 11 in datasheet, for *10 see Known Bugs

        return vshunt


    def get_vbus_voltage(self):
        """Read voltage on the V+/V- terminals.

        Args:
            None.

        Returns:
            Voltage in volts.
        """

        raw = self.__read_register24(self.Register.VBUS)

        vbus = self.__convert2comp2float(raw >> 4, 20, self.__get_vbus_conv_factor())   # Table 12 in datasheet

        return vbus


    def get_temp(self):
        """Read die temperature.

        Args:
            None.

        Returns:
            Temperature in Celsius.
        """

        raw = self.__read_register16(self.Register.DIETEMP)

        temp = self.__convert2comp2float(raw, 16, self.__get_temp_conv_factor())   # Table 13 in datasheet

        return temp


    def get_current(self):
        """Read current through I+/I- terminals.

        Args:
            None.

        Returns:
            Current in amperes.
        """

        raw = self.__read_register24(self.Register.CURRENT)

        current = self.__convert2comp2float(raw >> 4, 20, self.__get_current_lsb())   # Equation (3) in datasheet

        return current


    def get_power(self):
        """Read calculated power (a product of voltage and current).

        Args:
            None.

        Returns:
            Power in watts.
        """

        raw = self.__read_register24(self.Register.POWER)

        power = raw * 3.2 * self.__get_current_lsb()   # Equation (4) in datasheet

        return power


    def get_energy(self):
        """Read integral energy (a product of power and time since last reset).

        Args:
            None.

        Returns:
            Energy in joules.
        """

        raw = self.__read_register40(self.Register.ENERGY)

        energy = raw * 3.2 * 16 * self.__get_current_lsb()   # Equation (5) in datasheet

        return energy


    def get_charge(self):
        """Read charge spent (a product of current and time since last reset).

        Args:
            None.

        Returns:
            Charge in coulombs.
        """

        raw = self.__read_register40(self.Register.CHARGE)

        charge = self.__convert2comp2float(raw, 40, self.__get_current_lsb())   # Equation (6) in datasheet

        return charge


    def get_diag_alerts(self):
        """Read alerts.

        Args:
            None.

        Returns:
            List of Alert constants matching all active alert bits in alert register.
        """

        raw = self.__read_register16(self.Register.DIAG_ALRT)

        alerts = []

        for alert in Alert:
            if raw & (1 << alert.value):
                alerts.append(alert)

        return alerts

    def alert_message(self, alert):
        """Get text message for specific alert.

        Args:
            alert: Alert constant to explain.

        Returns:
            String representation of specific alert.
        """

        alert_strings = {
            Alert.MEMSTAT:  'MEMSTAT: Checksum error is detected in the device trim memory space',
            Alert.CNVRF:    'CNVRF: Conversion is completed',
            Alert.BUSUL:    'BUSUL: Bus voltage measurement falls below the threshold limit in the bus under-limit register',
            Alert.BUSOL:    'BUSOL: Bus voltage measurement exceeds the threshold limit in the bus over-limit register',
            Alert.SHNTUL:   'SHNTUL: Shunt voltage measurement falls below the threshold limit in the shunt under-limit register',
            Alert.SHNTOL:   'SHNTOL: Shunt voltage measurement exceeds the threshold limit in the shunt over-limit register',
            Alert.TMPOL:    'TMPOL: Temperature measurement exceeds the threshold limit in the temperature over-limit register',
            Alert.MATHOF:   'MATHOF: Arithmetic operation resulted in an overflow error',
            Alert.CHARGEOF: 'CHARGEOF: 40 bit CHARGE register has overflowed',
            Alert.ENERGYOF: 'ENERGYOF: 40 bit ENERGY register has overflowed',
        }

        return alert_strings[alert]

    def set_alert_bits(self, *args):
        """Set alert configuration.

        Args:
            Alert config constants to set in alert register (Alert.APOL, Alert.SLOWALERT, Alert.CNVR, Alert.ALATCH). All other will be reset.

        Returns:
            None.
        """

        data = self.__read_register16(self.Register.DIAG_ALRT) & 0x0FFF

        for alert in args:
            data |= (1 << alert.value)

        self.__write_register16(self.Register.BOVL, data)


    def set_shunt_overvoltage(self, value):
        """Set high alert threshold of the shunt resistor voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = __convertfloat22comp(value, 16, self.__get_shunt_conv_factor())   # Table 19 in datasheet

        self.__read_register16(self.Register.SOVL)

        self.__write_register16(self.Register.SOVL, data)


    def set_shunt_undervoltage(self, value):
        """Set low alert threshold of the shunt resistor voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = __convertfloat22comp(value, 16, self.__get_shunt_conv_factor())   # Table 20 in datasheet

        self.__read_register16(self.Register.SUVL)

        self.__write_register16(self.Register.SUVL, data)


    def set_bus_overvoltage(self, value):
        """Set high alert threshold of the V+/V- terminals voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = value / self.__get_vbus_conv_factor()   # Table 21 in datasheet

        self.__read_register16(self.Register.BOVL)

        self.__write_register16(self.Register.BOVL, data)


    def set_bus_undervoltage(self, value):
        """Set low alert threshold of the V+/V- terminals voltage.

        Args:
            value: Limit in volts.

        Returns:
            Nothing.
        """

        data = value / self.__get_vbus_conv_factor()   # Table 22 in datasheet

        self.__read_register16(self.Register.BUVL)

        self.__write_register16(self.Register.BUVL, data)


    def set_temp_limit(self, value):
        """Set high alert threshold of the die temperature.

        Args:
            value: Limit in Celsius.

        Returns:
            Nothing.
        """

        data = __convertfloat22comp(value, 16, self.__get_temp_conv_factor())   # Table 23 in datasheet

        self.__read_register16(self.Register.TEMP_LIMIT)

        self.__write_register16(self.Register.TEMP_LIMIT, data)


    def set_power_overlimit(self, value):
        """Set high alert threshold of the load power.

        Args:
            value: Limit in watts.

        Returns:
            Nothing.
        """

        data = value / (3.2 * self.__get_current_lsb())   # Equation (4) and Table 24 in datasheet

        self.__read_register16(self.Register.PWR_LIMIT)

        self.__write_register16(self.Register.PWR_LIMIT, data)


    def get_manufacturer_id(self):
        """Read manufacturer ID.

        Args:
            None.

        Returns:
            A string of 2 characters containing manufacturer ID.
        """

        raw_id = self.__read_register16(self.Register.MANUFACTURER_ID)

        return raw_id.to_bytes(2,'big').decode()


    def get_deviceid(self):
        """Read device ID.

        Args:
            None.

        Returns:
            A tuple of (device ID, device revision).
        """

        raw_id = self.__read_register16(self.Register.DEVICE_ID)

        return (hex(raw_id >> 4), hex(raw_id & 0xF))
