import machine
from modules import dht_module
import time
import pycom
import _thread
from modules.lora_module import join_lora, send_lora
import ustruct
#import random

# global variables
period = 0              # update periode in seconds for measuring a sending

hum = None
temp = None

def measure_dht():
    #print("function measure")
    global d
    global hum, temp
    # measure DHT temp and hum values
    if d.trigger() == True:
        hum = d.humidity
        temp = d.temperature
        print(hum, temp)
    else:
        print(d.status)
        print(None, None)
    time.sleep(5)
    #return(hum, temp)


def measure():
    hum = 0
    temp = -40

    global payload
    global d
    # measure DHT temp and hum values
    if d.trigger() == True:
        hum = d.humidity
        temp = d.temperature
        #temp = random.randrange(10, 40, 0.1)
        #hum = random.randrange(0, 100, 0.1)
    
        # encode
        hum = int(hum * 10)                 # 2 Bytes
        temp = int(temp*10) + 400           # max -40°, use it as offset
        #print("temp: ", temp, "hum: ", hum)

        ht_bytes = ustruct.pack('HH', hum, temp)
        payload.append(ht_bytes[0])
        payload.append(ht_bytes[1])
        payload.append(ht_bytes[2])
        payload.append(ht_bytes[3])
    
        #print("payload written", payload)
    # confirm with LED
    # pycom.rgbled(0x0000FF)  # Blue
    # time.sleep(0.1)
    # pycom.rgbled(0x000000)  # Off
    # time.sleep(1.9)
    else:
        print(d.status)
        payload = []


# def mock_measure():
#     print("mock_measure starting")
#     global payload
#     mm = []
#     mm_temp = (random.randrange(300, 400, 1)/10)
#     mm_hum = (random.randrange(0, 1000, 1)/10)
#     print("mock hum temp:", mm_hum, mm_temp)
#     print("mock ohum otemp:", int(mm_hum*10), int(mm_temp*10))
#     ht_bytes = struct.pack('HH', int(mm_hum*10), int(mm_temp*10))
#     payload.append(ht_bytes[0])
#     payload.append(ht_bytes[1])
#     payload.append(ht_bytes[2])
#     payload.append(ht_bytes[3])
#     print(payload)

def create_payload(data):
    pass


print("starting main")

if __name__ == "__main__":
    sckt = join_lora()
    time.sleep(2)
    # global data buffer
    payload = []            # common data buffer to collect and send
    d = dht_module.device(machine.Pin.exp_board.G22)
    while True:
        measure_dht()
        print("global:", hum, temp)
        print(hum, temp)
        #mock_measure()     

        if hum != None and temp != None:
            # encode
            hum = int(hum * 10)                 # 2 Bytes
            temp = int(temp*10) + 400           # max -40°, use it as offset
            #print("temp: ", temp, "hum: ", hum)

            ht_bytes = ustruct.pack('HH', hum, temp)
            payload.append(ht_bytes[0])
            payload.append(ht_bytes[1])
            payload.append(ht_bytes[2])
            payload.append(ht_bytes[3])
            hum = None
            temp = None

        print("LORA:", payload)
        # payload = [0x01, 0x02, 0x03]
        if len(payload) != 0:
            send_lora(sckt, payload)
            payload = []
            # confirm with LED
            # pycom.rgbled(0x0000FF)  # Blue
            # time.sleep(0.1)
            # pycom.rgbled(0x000000)  # Off
            #time.sleep(1.9)
        time.sleep(period)


  