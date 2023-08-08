import machine
# from modules import dht_module, lightsensor, anemometer
import time
import pycom

import _thread
from modules.lora import join_lora, send_lora
import ustruct

from lib.pycoproc_2 import Pycoproc
from lib.LIS2HH12 import LIS2HH12
from lib.SI7006A20 import SI7006A20
from lib.LTR329ALS01 import LTR329ALS01
from lib.MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

print("lora red")

# global variables
period = 10             # update periode in seconds for measuring a sending

# if __name__ == "__main__":
#     sckt = join_lora()
#     time.sleep(2)
#     # global data buffer
#     payload = []            # common data buffer to collect and send
#     # d = dht_module.device(machine.Pin.exp_board.G22)
#     while True:
#         # measure_dht()
#         #print("Humidity:", hum, "Temperature: ",temp)
#         #print(hum, temp)
#         #mock_measure()     
#         # measure_light()

#         # if hum != None and temp != None:
#         #     # encode
#         #     hum = int(hum * 10)                 # 2 Bytes
#         #     temp = int(temp*10) + 400           # max -40°, use it as offset
#         #     light = int(light)
#         #     #windspeed = int(windspeed * 10)           # convert into a int with multiplying by 10
#         #     #print("temp: ", temp, "hum: ", hum)

#         #     ht_bytes = ustruct.pack('HHH', hum, temp, light)
#         #     payload.append(ht_bytes[0])
#         #     payload.append(ht_bytes[1])
#         #     payload.append(ht_bytes[2])
#         #     payload.append(ht_bytes[3])
#         #     payload.append(ht_bytes[4])


#         #     hum = None
#         #     temp = None
#         #     light = None
#         #     windspeed = None

#         # payload.append(1)

#         print("LORA:", payload)
#         # payload = [0x01, 0x02, 0x03]
#         if len(payload) != 0:
#             send_lora(sckt, payload)
#             payload = []
#             # confirm with LED
#             # pycom.rgbled(0x0000FF)  # Blue
#             # time.sleep(0.1)
#             # pycom.rgbled(0x000000)  # Off
#             #time.sleep(1.9)
#         time.sleep(period)

def py_sense(): 
    pycom.heartbeat(False)
    pycom.rgbled(0x0A0A08) # white

    py = Pycoproc()
    if py.read_product_id() != Pycoproc.USB_PID_PYSENSE:
        raise Exception('Not a Pysense')

    pybytes_enabled = False
    if 'pybytes' in globals():
        if(pybytes.isconnected()):
            print('Pybytes is connected, sending signals to Pybytes')
            pybytes_enabled = True

    mp = MPL3115A2(py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
    print("MPL3115A2 temperature: " + str(mp.temperature()))
    print("Altitude: " + str(mp.altitude()))
    mpp = MPL3115A2(py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    print("Pressure: " + str(mpp.pressure()))


    si = SI7006A20(py)
    print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")
    print("Dew point: "+ str(si.dew_point()) + " deg C")
    t_ambient = 24.4
    print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(si.humid_ambient(t_ambient)) + "%RH")


    lt = LTR329ALS01(py)
    print("Light (channel Blue, channel Red): " + str(lt.light())," Lux: ", str(lt.lux()), "lx")

    li = LIS2HH12(py)
    print("Acceleration: " + str(li.acceleration()))
    print("Roll: " + str(li.roll()))
    print("Pitch: " + str(li.pitch()))

    print("Battery voltage: " + str(py.read_battery_voltage()))

    # set your battery voltage limits here
    vmax = 4.2
    vmin = 3.3
    battery_voltage = py.read_battery_voltage()
    battery_percentage = (battery_voltage - vmin / (vmax - vmin))*100
    print("Battery voltage: " + str(py.read_battery_voltage()), " percentage: ", battery_percentage)
    if(pybytes_enabled):
        pybytes.send_signal(1, mpp.pressure())
        pybytes.send_signal(2, si.temperature())
        pybytes.send_signal(3, lt.light())
        pybytes.send_signal(4, li.acceleration())
        pybytes.send_battery_level(int(battery_percentage))
        print("Sent data to pybytes")


py_sense();