import machine

class interface():
    """Simple interface to set data on the tlc5940"""

    def __init__(self, GSCLK_pin, BLANK_pin, VPRG_pin, XLAT_pin, SCLK_pin, SIN_pin):
        """Initialize all GPIO pins and SPI pins

        Any General Purpose Input/Output pins can be used for:
            GSCLK - Pulse Width Modulation clock (no actual PWM implemented)
            BLANK - Disable all outputs
            VPRG - Set programming mode
            XLAT - Latch values after programming

        Specific SPI (Serial Peripheral Interface) pins must be used for:
            SCLK (GP14) - Serial clock
            SIN (GP16) - Serial data
            (see documentation for specific board implementations)
        """
        self.GSCLK = machine.Pin(GSCLK_pin, machine.Pin.OUT, value=0)
        self.BLANK = machine.Pin(BLANK_pin, machine.Pin.OUT, value=1) # Disable all outputs
        self.VPRG = machine.Pin(VPRG_pin, machine.Pin.OUT, value=0)
        self.XLAT = machine.Pin(XLAT_pin, machine.Pin.OUT, value=0)
        self.SPI = machine.SPI(baudrate=10000000, bits=8, pins=(SCLK_pin, SIN_pin, None))

    def set_data(self, byte_array):
        """Set data from byte_array in tlc5940(s)

        Each tlc5940 accepts 16 x 12-bit (192-bit) data before
        sending any further data to SOUT.

        To be able to send data to multiple tlc5940s,
        connect SOUT to SIN in series.
        """

        self.SPI.write(byte_array) # Send grey scale data on SPI
        self.BLANK.value(1) # Disable all outputs
        self.XLAT.value(1) # Latch data
        self.XLAT.value(0)
        self.BLANK.value(0) # Enable outputs
        self.GSCLK.value(1) # Pulse PWM clock once to activate data
        self.GSCLK.value(0)

def bit_string_to_byte_array(bit_string):
    """Convert tlc5940 bit string to byte array for SPI"""

    byte_array = bytearray()
    byte = ""
    for bit in bit_string:
        byte += bit
        if len(byte) == 8:
            byte_array.append(int("0b{}".format(byte)))
            byte = ""
    return byte_array

def simple_byte_array(outputs):
    """Convert a simple string of outputs to a tlc5940 byte array

    The tlc5940 requires 12-bit grey scale data for each output.
    This function allows on/off inputs instead.

    Tlc5940 grey scale data format is Big-Endian, so the byte array
    is reversed compared to the input.

    Ex. single tlc5940:
        outputs = "1010000000000000"
    activates OUT0 and OUT2 at 100 % brightness

    Ex. 2 x tlc5940 in series:
        outputs = "10100000000000001100000000000000"
    activates OUT0 and OUT2 on the first tlc5940,
    and activates OUT0 and OUT1 on the second tlc5940
    """

    def bit_string_generator(outputs):
        for i in reversed(outputs):
            for bit in range(12):
                yield i

    return bit_string_to_byte_array(bit_string_generator(outputs))
