"""
Example usage of tlc5940 library to drive 7-segment displays


7-segment display layout
10 9 8 7 6
 . . . . .
   AAAA
  F    B
  F    B
   GGGG
  E    C
  E    C
   DDDD   DP
 . . . . .
 1 2 3 4 5
segments = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'DP']
pinout   = [  7,   6,   4,   3,   2,   9,  10,    5]
index    = [  0,   1,   2,   3,   4,   5,   6,    7]
Ex. 11111101 -> the number 0. with a decimal point

Segments described by index
   0000
  5    1
  5    1
   6666
  4    2
  4    2
   3333   7
"""

import tlc5940
import time

def symbols_bytearray():
    """Pre-generate dict of bytearrays of all symbols

    Pre-generation is important for fast display updates.
    """

    CHARACTER_TABLE = {
        " ": '00000000',
        "-": '00000010',
        "_": '00010000',
        "|": '00001100', # left aligned line
        "0": '11111100',
        "1": '01100000',
        "2": '11011010',
        "3": '11110010',
        "4": '01100110',
        "5": '10110110',
        "6": '10111110',
        "7": '11100000',
        "8": '11111110',
        "9": '11110110',
        "A": '11101110',
        "b": '00111110',
        "c": '00011010',
        "C": '10011100',
        "d": '01111010',
        "E": '10011110',
        "F": '10001110',
        "G": '10111100',
        "h": '00101110',
        "H": '01101110',
        "I": '01100000',
        "J": '01111000',
        "l": '01100000',
        "n": '00101010',
        "o": '00111010',
        "P": '11001110',
        "q": "11100110",
        "r": '00001010',
        "S": '10110110',
        "T": '10001100',
        "t": '00001110',
        "u": '00111000',
        "Y": '01100110',
        "[": '10011100',
        "]": '11110000',
        "=": '00010010',
        "#": '11000110'} # degree symbol

    symbols = {}
    for sym in CHARACTER_TABLE:
        symbols[sym] = tlc5940.simple_byte_array(CHARACTER_TABLE[sym])
    return symbols

def output(symbols, string):
    """Combine symbols to output bytearray"""

    out = bytearray()
    for i in string:
        out += symbols[i]
    return out

def add_decimal_point(byte_array, position):
    """Activate decimal point at position"""

    offset = position * 12
    output = byte_array
    output[0 + offset] += 255
    output[1 + offset] += 240
    return output

def get_time_offset():
    """Get the time offset between internal clock and timeserver"""

    import untplib
    # Re-try in case of connectivity problems
    for i in range(3):
        try:
            c=untplib.NTPClient()
            resp=c.request('0.uk.pool.ntp.org', version=3, port=123)
            return resp.offset
        except:
            time.sleep_us(500000)

def countdown(tlc, symbols, set_time, flash_message_string):
    """Simple countdown with flashing message

    Due to implementation with time.sleep, the counter will drift.
    """

    offset = get_time_offset()
    # Conversion due to different epochs
    current_time = 3155673600 + time.time() - 2208988800 + offset
    count = (set_time - current_time) * 10
    while True:
        for i in range(120): # 12 seconds
            start = time.ticks_us()
            data = output(symbols, "{:8d}".format(count))
            data_with_decimal_point = add_decimal_point(data, 6) # 7th number
            tlc.set_data(data_with_decimal_point)
            count -= 1
            time.sleep_us(100000 - time.ticks_diff(start, time.ticks_us()))
        for i in range(30): # 3 seconds
            start = time.ticks_us()
            tlc.set_data(output(symbols, flash_message_string))
            count -= 1
            time.sleep_us(100000 - time.ticks_diff(start, time.ticks_us()))

if __name__ == "__main__":

    # Initialize tlc
    tlc = tlc5940.interface('GP23', 'GP1', 'GP7', 'GP2', 'GP14', 'GP16')

    # Pre-generate symbols
    symbols = symbols_bytearray()

    # Start countdown
    # 1482595200 = 2016-12-24CET17:00
    countdown(tlc, symbols, 1482595200, " God Ju|")
