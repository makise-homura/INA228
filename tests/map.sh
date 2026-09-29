#!/bin/sh

# I2C location of INA228
bus=0
addr=0x40

# Address:length
regmap="0x00:2 0x01:2 0x02:2 0x03:2 0x04:3 0x05:3 0x06:2 0x07:3 0x08:3 0x09:5 0x0a:5 0x0b:2 0x0c:2 0x0d:2 0x0e:2 0x0f:2 0x10:2 0x11:2 0x3e:2 0x3f:2"

if which i2cget 1>/dev/null
then
    echo 'stub_regmap = {'
    for entry in $regmap
    do
        reg=`echo $entry | cut -d: -f1`
        len=`echo $entry | cut -d: -f2`
        echo "    $reg: [`i2cget -y $bus $addr $reg i $len | sed 's/ /, /g'`],"
    done
    echo '}'
else
    echo "Install i2c-tools or supply i2cget binary to the PATH." 1>&2
fi
