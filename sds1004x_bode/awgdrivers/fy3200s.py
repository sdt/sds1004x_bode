'''
Created on April 2, 2019

@author: Kai Gemlau

Driver for FeelTech FY3200s AWG.
Based on FY6600 driver
'''

import feeltech
import time
from base_awg import BaseAWG
import constants
from exceptions import UnknownChannelError

# Port settings constants
BAUD_RATE = 9600

# FY320 End of line character (\n)
# Channels validation tuple
CHANNELS = (0, 1, 2)
CHANNELS_ERROR = "Channel can be 1 or 2."

# Output impedance of the AWG
R_IN = 50.0

TIMEOUT=5

class FY3200S(BaseAWG):
    '''
    FY3200s function generator driver.
    '''
    SHORT_NAME = "fy3200s"

    def __init__(self, port, baud_rate=BAUD_RATE, timeout=TIMEOUT):
        """baud_rate parameter is ignored."""
        """timeout parameter is ignored."""
        self.port = port
        self.feeltech = None
        self.r_load = [50, 50]
        self.v_out_coeff = [1, 1]

    def connect(self):
        self.feeltech = feeltech.FeelTech(self.port)

    def disconnect(self):
        self.feeltech.close()
        self.feeltech = None

    def _channel(self, channel):
        channels = self.feeltech.channels()
        return channels[channel-1]

    def _channels(self, channel):
        if channel is None:
            raise UnknownChannelError(CHANNELS_ERROR)
        if channel == 0:
            return self.feeltech.channels()
        return [ self.feeltech.channels()[channel-1] ]

    def initialize(self):
        self.channel_on = [False, False]
        self.connect()
        self.enable_output()

    def get_id(self):
        return self.feeltech.type()

    def enable_output(self, channel=0, on=False):
        """
        Turns channels output on or off.
        The channel is defined by channel variable. If channel is 0, both channels are set.
        """
        for ch in self._channels(channel):
            ch.enable_output(on)

    def set_frequency(self, channel, freq):
        """
        Sets frequency on the selected channel. Frequency is in centiHz

        Command examples:
            bf0000000100 equals 1 Hz on channel 1
            df0000100000 equals 1 kHz on channel 2
        """
        for ch in self._channels(channel):
            ch.frequency(freq)

    def set_phase(self, phase):
        """
        Sends the phase setting command to the generator.
        The phase is set on channel 2 only.
        """
        while phase < 0:
            phase += 360

        self.feeltech.phase(phase)

    def set_wave_type(self, channel, wave_type):
        """
        Sets wave type of the selected channel.
       """
        for ch in self._channels(channel):
            ch.waveform(feeltech.SINE)

    def set_amplitue(self, channel, amplitude):
        """
        Sets amplitude of the selected channel.

        Commands:
            ba0.44 for 0.44 volts Channel 1
            da9.87 for 9.87 volts Channel 2
        """
        amplitude = amplitude / self.v_out_coeff[channel-1]
        for ch in self._channels(channel):
            ch.amplitude(amplitude)

    def set_offset(self, channel, offset):
        """
        Sets DC offset of the selected channel.

        Command examples:
        bo0.33 sets channel 1 offset to 0.33 volts
        do-3.33sets channel 2 offset to -3.33 volts
        """
        # Adjust the offset to the defined load impedance
        offset = offset / self.v_out_coeff[channel-1]
        for ch in self._channels(channel):
            ch.offset(offset)

    def set_load_impedance(self, channel, z):
        """
        Sets load impedance connected to each channel. Default value is 50 Ohm.
        """
        if channel is not None and channel not in CHANNELS:
            raise UnknownChannelError(CHANNELS_ERROR)

        self.r_load[channel-1] = z

        """
        Vout coefficient defines how the requestd amplitude must be increased
        in order to obtain the requested amplitude on the defined load.
        If the load is Hi-Z, the amplitude must not be increased.
        If the load is 50 Ohm, the amplitude has to be double of the requested
        value, because of the voltage divider between the output impedance
        and the load impedance.
        """
        if z == constants.HI_Z:
            v_out_coeff = 1
        else:
            v_out_coeff = z / (z + R_IN)
        self.v_out_coeff[channel-1] = v_out_coeff

if __name__ == '__main__':
    print ("This module shouldn't be run. Run awg_tests.py instead.")
