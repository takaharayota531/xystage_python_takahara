import socket
import csv
import re
import serial
import time
import numpy as np

def readline2(ser):
    res = b''
    s = ser.read()
    while s!=b'\r':
        res = res+s
        s = ser.read()
    return res

def waitmove(ser):
    while ser.read()!=b'\r':
        pass
    while ser.read()!=b'\r':
        pass

X_POINT = 3
Y_POINT = 3
int = 5
POS_STR = [400,350]
FREQ_STR = 1E9
FREQ_STP = 11E9
FREQ_POINT = 201
filename = 'sample.csv'

freq_int = (FREQ_STP-FREQ_STR)/(FREQ_POINT-1)
freq = [FREQ_STR+i*freq_int for i in range(FREQ_POINT)]*X_POINT*Y_POINT
ind = [i for i in range(FREQ_POINT)]*X_POINT*Y_POINT
pos = [[i+j*0 for i in range(X_POINT) for j in range(FREQ_POINT)]*Y_POINT,\
[i+j*0 for i in range(Y_POINT) for j in range(FREQ_POINT*X_POINT)]]
freq = np.array(freq)
ind = np.array(ind)
pos = np.array(pos)
pos = pos.T


robot = serial.Serial("COM3", 9600, timeout=0.1) # connect to robot module
robot.write(b'SVON\r') # servo motor on
robot.readline() # need time interval for secure operation
robot.write(b'MOT\r') # remote control mode
robot.readline()
robot.write(b'SPD S10 A10 B1\r') # set speed
robot.readline()
ORD = b'MOV X'+str(POS_STR[0]).encode()+b' Y'+str(POS_STR[1]).encode()+b' S50 &AFW\r'
robot.write(ORD)
waitmove(robot)

vna = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # connect to vna
vna.settimeout(5)
vna.connect(("127.0.0.1", 5001))
vna.send(str.encode(':SENS1:FREQ:STAR '+str(FREQ_STR)+';:SENS1:FREQ:STOP '+str(FREQ_STP)+'\n'))
vna.send(str.encode(':SENSE:SWEEP:POINTS '+str(FREQ_POINT)+'\n'))
vna.send(str.encode('CH1;MPH;\n'))
data = []

for xi in range(X_POINT):
    for yi in range(Y_POINT):
        POS_NEXT = [x+y for (x,y) in zip(POS_STR,[xi*int,yi*int])]
        print(POS_NEXT)
        ORD = b'MOV X'+str(POS_NEXT[0]).encode()+b' Y'+str(POS_NEXT[1]).encode()+b' &AFW\r'
        print(ORD)
        robot.write(ORD)

        waitmove(robot)
        time.sleep(1) # wait for setteling
        vna.send(str.encode('TRS;WFS;HLD\n'))
        vna.send(str.encode('FMA;OFD\n'))

        s = vna.recv(11) # receive header
        for i in range(FREQ_POINT):
            s = vna.recv(1)
            buf = b''
            while s!=b'\n':
                buf = buf+s
                s = vna.recv(1)
            buf = buf.decode()
            buf = buf.split(',')
            data.append(buf)

data = np.array(data)

data = np.concatenate((ind.reshape(-1,1), freq.reshape(-1,1), data, pos),axis=1)

with open('data/'+filename, 'w', newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

robot.write(b'QUIT\r')
robot.write(b'SVOF\r')
