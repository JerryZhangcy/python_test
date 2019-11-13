from serial import *
import serial.tools.list_ports
import time
import threading


def config_and_open_serial():
    global ser
    ser.port = 'COM11'
    ser.baudrate = 921600
    ser.bytesize = EIGHTBITS
    ser.stopbits = STOPBITS_ONE
    ser.parity = PARITY_NONE
    try:
        ser.open()
    except:
        print("open error!")


def close_serial():
    ser.close()
    print("[close_serial]")


def receive_data():
    while True:
        try:
            num = ser.inWaiting()
        except:
            close_serial()
        if num > 0:
            data = ser.read(num)
            num = len(data)
            print("[receive_data] " + str(data))


Com_Dict = {}
ser = serial.Serial()
port_list = list(serial.tools.list_ports.comports())
for port in port_list:
    print(str(port[0]) + "  " + str(port[1]))
    Com_Dict["%s" % port[0]] = "%s" % port[1]
config_and_open_serial()
time.sleep(1)
receive_thread = threading.Thread(target=receive_data)
receive_thread.start()
