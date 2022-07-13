import serial

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


ser = serial.Serial("COM5", 9600, timeout=0.1)

# print(ser.name)
ser.write(b'SVON\r') # servo motor on
print(ser.readline())
ser.write(b'MOT\r')
print(ser.readline())


ser.write(b'SPD S50 A10 B1\r')
print(ser.readline())
#
print('move1')
ser.write(b'MOV X380 Y0200 &AFW\r')
waitmove(ser)
# ser.write(b'MEND ALL')
# print(ser.readline())
# ser.write(b'POS ALL\r')
# print(ser.readline())

print('move2')
ser.write(b'MOV X0580.00 Y0280.00 &AFW\r')
print(readline2(ser))
print(readline2(ser))
# ser.write(b'MEND ALL')
# print(ser.readline())
ser.write(b'POS ALL\r')
print(ser.readline())

ser.write(b'QUIT\r')
# print(ser.readline())
ser.write(b'SVOF\r') # servo motor off
# print(ser.readline())
# print(ser.readline())
