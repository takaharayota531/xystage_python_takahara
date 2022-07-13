import serial
ser = serial.Serial("COM3", 9600)
print(ser.name)
ser.write(b'AGO:A10000\r\n')
# ser.write(b'H:A')
# result = ser.readline()
# print(result)
#print('Res:'+result.encode())
ser.close()
