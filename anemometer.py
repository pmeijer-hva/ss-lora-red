from utime import time, sleep
from machine import Pin, ADC

class Anemometer(object):
    'sparkfun anemometer kit sensor'
    # Constants
    ADC_MAX = 4095
    ADC_MIN = 0
    PIN_SPEED = 'P11'
    #PIN_DIR = 'G3'
    PIN_DIR = 'P15'

    rotations = 0
    timeout = None
    adc = None

    # Pins
    pin_speed = None
    pin_dir = None

    def __init__(self):
        self.timeout = time()

        try:
            # Intialize the Speed IO
            self.pin_speed = Pin(self.PIN_SPEED, mode = Pin.IN, pull = Pin.PULL_UP)
            self.pin_speed.callback(Pin.IRQ_RISING, self.rotations_handler)

            # Initialize the Direction ADC
            self.adc = ADC()
            self.pin_dir = self.adc.channel(pin = self.PIN_DIR, attn = ADC.ATTN_11DB)
        except Exception as e:
            # Should throw exception to stop execution
            pass

    def rotations_handler(self, arg):
        self.rotations = self.rotations + 1

    def mph_to_ms(self, mph):
        return mph * 0.447

    def mph_to_kmh(self, mph):
        return mph * 1.60934

    def dir_to_deg(self, dir):
        #pc2 = (dir - self.ADC_MIN) / ((self.ADC_MAX - self.ADC_MIN) / 360)
        pc = (dir - self.ADC_MIN) / (self.ADC_MAX - self.ADC_MIN)
        return int(round(pc * 360))

    def dir_to_dir(self, dir):
        if dir < 333:
            return 0
        elif dir < 760:
            return 45
        elif dir < 1190:
            return 90
        elif dir < 1490:
            return 135
        elif dir < 1930:
            return 180
        elif dir < 2330:
            return 225
        elif dir < 3020:
            return 270
        elif dir < 3780:
            return 315
        else:
            return 0

    def get_windspeed(self):
        delta_time = (time() - self.timeout)
        try:
            mph = self.rotations * (2.25 / delta_time)
        except Exception as e:
            mph = 0
        self.rotations = 0
        self.timeout = time()

        return round(self.mph_to_ms(mph), 1)

    def get_dir(self):
        try:
            dir = self.pin_dir.value()
        except Exception as e:
            dir = 0
        return self.dir_to_deg(dir)
        #return dir

if __name__ == "__main__":
    sensor_anemometer = Anemometer()
    while True:
        windspeed = sensor_anemometer.get_windspeed()
        winddirection = sensor_anemometer.get_dir()
        print(windspeed, winddirection)
        sleep(1)
