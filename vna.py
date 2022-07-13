import socket
import csv
import re

vna = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
vna.settimeout(5)
vna.connect(("127.0.0.1", 5001))
print(vna.getpeername())

FREQ_POINT = '401';
FREQ_START = '1E9';
FREQ_STOP = '21E9';

vna.send(str.encode("*IDN?\n"))
reply = vna.recv(2056)
print(reply)
vna.send(str.encode("SENS:FREQ:STAR?\n"))
reply = vna.recv(2056)
print(reply)
vna.send(str.encode("SENS:FREQ:STOP?\n"))
reply = vna.recv(2056)
print(reply)
vna.send(str.encode(':SENS1:FREQ:STAR '+FREQ_START+';:SENS1:FREQ:STOP '+FREQ_STOP+'\n'))
vna.send(str.encode(':SENSE:SWEEP:POINTS '+FREQ_POINT+'\n'))
vna.send(str.encode('CH1;MPH;\n'))
vna.send(str.encode('TRS;WFS;HLD\n'))
vna.send(str.encode('FMA;OFD\n'))

s = vna.recv(11)
print(s) # receive header
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
    res.append(buf)
print(res)

with open('data/sample.csv', 'w', newline="") as f:
    writer = csv.writer(f)
    writer.writerows(res)
