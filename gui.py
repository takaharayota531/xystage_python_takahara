import PySimpleGUI as sg
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

def measurement(values,window):

    X_POINT = int(values[1])
    Y_POINT = int(values[2])
    interval = int(values[3])
    POS_STR = [int(values[4]),int(values[5])]
    FREQ_STR = int(values[6])*1e9
    FREQ_STP = int(values[7])*1e9
    FREQ_POINT = int(values[8])

    layout = [
    [sg.Text("ファイル"), sg.InputText(), sg.FileBrowse(key="file1")],
    [sg.Submit(), sg.Cancel()],
    ]

    windowf = sg.Window("ファイル選択", layout)
    event, valuesf = windowf.read()
    windowf.close()
    # print(valuesf)
    filename = valuesf[0]

    freq_int = (FREQ_STP-FREQ_STR)/(FREQ_POINT-1)
    freq = [FREQ_STR+i*freq_int for i in range(FREQ_POINT)]*X_POINT*Y_POINT
    ind = [i for i in range(FREQ_POINT)]*X_POINT*Y_POINT
    pos = [[i+j*0 for i in range(X_POINT) for j in range(FREQ_POINT)]*Y_POINT,\
    [i+j*0 for i in range(Y_POINT) for j in range(FREQ_POINT*X_POINT)]]
    freq = np.array(freq)
    ind = np.array(ind)
    pos = np.array(pos)
    pos = pos.T


    robot = serial.Serial('COM'+values[0], 9600, timeout=0.1) # connect to robot module
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
            POS_NEXT = [x+y for (x,y) in zip(POS_STR,[xi*interval,yi*interval])]
            # print(POS_NEXT)
            ORD = b'MOV X'+str(POS_NEXT[0]).encode()+b' Y'+str(POS_NEXT[1]).encode()+b' &AFW\r'
            # print(ORD)
            robot.write(ORD)

            waitmove(robot)

            window['xpos'].update(xi)
            window['ypos'].update(yi)
            window.refresh()

            # event, values = window.read()
            # if event == 'INTERRUPT':
            #     print('Interrupted')
            #     break
            # window['progress'].print((yi+xi/X_POINT)/Y_POINT*100)

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
        # if event == 'INTERRUPT':
        #     print('Interrupted')
        #     break

    data = np.array(data)

    # print(ind.shape)
    # print(freq.shape)
    # print(data.shape)
    # print(pos.shape)
    # print(ind)
    data = np.concatenate((ind.reshape(-1,1), freq.reshape(-1,1), data, pos),axis=1)

    with open(filename, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    robot.write(b'QUIT\r')
    robot.write(b'SVOF\r')

    print('finished')

# ここからメインプログラム
sg.theme('DarkAmber')   # デザインテーマの設定

# ウィンドウに配置するコンポーネント
layout = [  [sg.Text('Set parameters')],
            [sg.Text('COM port No.: '), sg.Input(default_text='3',size=(10,1))],
            [sg.Text('X_POINT：'), sg.Input(default_text='60',size=(10,1)),
            sg.Text('Y_POINT'), sg.Input(default_text='60',size=(10,1))],
            [sg.Text('Interval: '), sg.Input(default_text='5',size=(10,1)), sg.Text('mm')],
            [sg.Text('START_POINT x: '), sg.Input(default_text='400',size=(10,1)), sg.Text('y: '),sg.InputText(default_text='300',size=(10,1))],
            [sg.Text('START FREQUENCY: '), sg.Input(default_text='1',size=(10,1)), sg.Text('GHZ')],
            [sg.Text('STOP FREQUENCY: '), sg.Input(default_text='11',size=(10,1)), sg.Text('GHZ')],
            [sg.Text('FREAUENCY POINT: '), sg.Input(default_text='201',size=(10,1))],
            [sg.Button('START'), sg.Button('INTERRUPT'), sg.Button('FINISH')],
            [sg.Text('Current Pos.: '), sg.Text(0,key='xpos'), sg.Text(0,key='ypos')]]
            # [sg.Text('Progress: '), sg.Multiline(key='progress'),sg.Text('%')] ]

# ウィンドウの生成
window = sg.Window('XY measurement', layout)

# イベントループ
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'FINISH':
        break
    elif event == 'START':
        measurement(values,window)

window.close()
