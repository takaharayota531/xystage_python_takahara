import socket
import csv
import re
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt

vna = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vna.settimeout(5)
vna.connect(("127.0.0.1", 5001))
print(vna.getpeername())

FREQ_POINT = '201';
FREQ_START = '1E9';
FREQ_STOP = '11E9';

vna.send(str.encode("*IDN?\n"))
reply = vna.recv(2056)
# print(reply)
vna.send(str.encode("SENS:FREQ:STAR?\n"))
reply = vna.recv(2056)
# print(reply)
vna.send(str.encode("SENS:FREQ:STOP?\n"))
reply = vna.recv(2056)
# print(reply)
vna.send(str.encode(':SENS1:FREQ:STAR '+FREQ_START+';:SENS1:FREQ:STOP '+FREQ_STOP+'\n'))
vna.send(str.encode(':SENSE:SWEEP:POINTS '+FREQ_POINT+'\n'))
vna.send(str.encode('CH1;MPH;\n'))

csv_file = open('antenna.csv','r', encoding="utf-8-sig")
antenna = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\n", skipinitialspace=True)
# print(type(antenna))
f = next(antenna)
f = list(map(float,f[0:401:2]))
amp = next(antenna)
amp = list(map(float,amp[0:401:2]))
amp = list(map(lambda x: 10**(x/10), amp))
df = f[1]-f[0]
Nh = int(f[0]/df)
print(Nh)
data_f = np.array([complex(0)]*(Nh+len(f)))
T = 1/df
Nfft = 1024
dt = T/Nfft
t = np.linspace(0.0,T,Nfft)
l = t*3e8
data_t = [0]*Nfft
plt.ion()
figure1, ax1 = plt.subplots(figsize=(8,6))
line1, = ax1.plot(t, data_t)
plt.xlabel("Time[t]",fontsize=18)
plt.ylabel("Amplitude",fontsize=18)
# print(np.power(list(map(lambda x: x/1e9, f)),4))
# print(amp)
while(1):
    vna.send(str.encode('TRS;WFS;HLD\n'))
    vna.send(str.encode('FMA;OFD\n'))

    s = vna.recv(11)
    # print(s) # receive header
    # print(vna.recv(2048))
    res = []
    for i in range(int(FREQ_POINT)):
        s = vna.recv(1)
        buf = b''
        while s!=b'\n':
            buf = buf+s
            s = vna.recv(1)
        buf = buf.decode()
        buf = buf.split(',')
        data = 10**(float(buf[0])/10)*np.exp(1j*float(buf[1])/180*math.pi)
        res.append(data)
    data = np.array(res)/amp
    data = data*list(np.power(list(map(lambda x: x/1e9, f)),2))
    data_f[Nh:]=data
    data_t = np.fft.ifft(data_f,Nfft)
    data_y = abs(data_t)
    # data_y = abs(data_f[Nh:])
    data_x = t
    # print(len(data_x))
    # print(len(data_y))
    plt.ylim(min(data_y),max(data_y))
    plt.xlim(min(data_x),max(data_x))
    line1.set_xdata(data_x)
    line1.set_ydata(data_y)
    figure1.canvas.flush_events()
    figure1.canvas.draw()
