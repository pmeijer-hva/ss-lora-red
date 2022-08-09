# main.py -- put your code here!
import time
from machine import I2C, Pin, ADC
import pycom

from bme280 import BME280, BME280_OSAMPLE_16
from anemometer import Anemometer
from lora_pycom import join_lora, send_lora
import ustruct


def measure_sensor():
    global payload
    temp = bme.temperature
    hum = bme.humidity
    press = bme.pressure
    print(" [+] Temp: " + temp + ", Pressure: " + press + ", Humidity: " + hum)
    #print(type(hum))
    #print(" [+] Temp: " + bme.temperature + ", Pressure: " + bme.pressure + ", Humidity: " + bme.humidity)
    hum = int(float(hum) * 10)                 # 2 Bytes
    temp = int(float(temp)*10) + 400           # max -40°, use it as offset
    press = int(float(press) * 10)            # 300 to 1100 hPa with 2 digits after the point
    light = apin_lightsensor()               # read the analog light sensor
    windspeed = sensor_anemometer.get_windspeed()
    windspeed = int(windspeed * 10)           # convert into a int with multiplying by 10
    winddirection = sensor_anemometer.get_dir()
    winddirection = int(winddirection)

    print(" [***] temp: ", temp, "hum: ", hum, "press: ", press, "light:", light, "windspeed:", windspeed, "winddirection: ", winddirection)

    ht_bytes = ustruct.pack('HHHHHH', hum, temp, press, light, windspeed, winddirection)
    print("ht_bytes:", ht_bytes)
    for i in range(len(ht_bytes)):
        payload.append(ht_bytes[i])
    # payload.append(ht_bytes[0])
    # payload.append(ht_bytes[1])
    # payload.append(ht_bytes[2])
    # payload.append(ht_bytes[3])
    # payload.append(ht_bytes[4])
    # payload.append(ht_bytes[5])
    # payload.append(ht_bytes[6])
    # payload.append(ht_bytes[7])



# mind the pinout of the LOPY and MAKR Module 2.0
i2c = I2C(0, pins=('P9','P10'))     # create and use non-default PIN assignments (P10=SDA, P11=SCL)
i2c.init(I2C.MASTER, baudrate=20000) # init as a master
i2c = I2C(0, I2C.MASTER, baudrate=400000)
#print(i2c.scan())
bme = BME280(i2c=i2c, mode=BME280_OSAMPLE_16)

# light sensor init
adc = ADC()             # create an ADC object for the light sensor
apin_lightsensor = adc.channel(pin='P13', attn = ADC.ATTN_11DB)   # create an analog pin on P13, 3.3V reference, 12bit

# anemometer init
sensor_anemometer = Anemometer()


print("starting main")
period = 3

print("start lora")
sckt = join_lora()
time.sleep(2)

payload = []

while True:
    #print("On")
    #p_out.value(1)

    #print(" [+] Temp: " + bme.temperature + ", Pressure: " + bme.pressure + ", Humidity: " + bme.humidity)

    #time.sleep(0.2)
    #p_out.value(0)
    #print("Off")
    measure_sensor()
    time.sleep(3)
    #payload = [0x01, 0x02, 0x03]

    print("LORA:", payload)
    if len(payload) != 0:
        send_lora(sckt, payload)
        payload = []
        #confirm with LED
        #pycom.rgbled(0x0000FF)  # Blue
        #time.sleep(0.1)
        #pycom.rgbled(0x000000)  # Off
        #time.sleep(1.9)
    time.sleep(period)
