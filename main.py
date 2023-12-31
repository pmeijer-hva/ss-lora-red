import machine
import time
import pycom
from modules.lora import join_lora, send_lora
import ustruct

from lib.pycoproc_1 import Pycoproc
from lib.SI7006A20 import SI7006A20
from lib.LTR329ALS01 import LTR329ALS01
from lib.MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

class Main:
    py = Pycoproc(Pycoproc.PYSENSE)

    def __init__(self):
        pycom.heartbeat(False)
        print("---- LoRA RED initializing ----")
        self.send_lora_payload()

    def send_lora_payload(self):
        measurements = self.py_sense()

        if len(measurements) == 4:
            print(measurements)
            sckt = join_lora()

            # because device warms up we substract 5, determined by Martin and Pim
            offset_temp = 5;
            temp = int(float(measurements[0] - offset_temp) * 10 ) + 400           # max -40°, use it as offset
            hum = int(float(measurements[1]) * 10)                 # 2 Bytes
            lux = int(float(measurements[2]) * 10)                 # 2 Bytes
            press = int(float(measurements[3]) / 100)              # original value is in pA 
            ht_bytes = ustruct.pack('HHHH', temp, hum, lux, press)

            payload = []  

            #pack 8 bytes
            for index in range(0,8):
                payload.append(ht_bytes[index]) 

            send_lora(sckt, payload)
            pycom.rgbled(0x007f00) #green
        else:
            pycom.rgbled(0x7f0000) # red
        
        time.sleep(1)
        machine.deepsleep(12000)    

    def py_sense(self): 

        mp = MPL3115A2(self.py,mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
        print("MPL3115A2 temperature: " + str(mp.temperature()))

        mpp = MPL3115A2(self.py,mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
        print("Pressure: " + str(mpp.pressure()))

        si = SI7006A20(self.py)
        print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")

        lt = LTR329ALS01(self.py)
        print("Light (channel Blue lux, channel Red lux): " + str(lt.lux()))
              
        #not all measurements from the code above are used in this return
        measurements = [si.temperature(), si.humidity(), lt.lux(), mpp.pressure()]

        return measurements

if __name__ == "__main__":
    Main()