import pyvisa
import csv
import re
rm = pyvisa.ResourceManager()
inst = rm.open_resource("GPIB0::6::INSTR")
print(inst)

inst.write('*IDN?\n')
print(inst.read())

FREQ_POINT = '5';
FREQ_START = '1E9';
FREQ_STOP = '21E9';

inst.write(':SENS1:FREQ:STAR '+FREQ_START+';:SENS1:FREQ:STOP '+FREQ_STOP+'\n') # set the frequency
inst.write(':SENSE:SWEEP:POINTS '+FREQ_POINT+'\n') # sets the sweep points
inst.write('CH1;MPH;\n') # trace active, sets to Smith Chart.
inst.write('TRS;WFS;HLD\n') # does a triger sweep and waiats for sweep finish.
inst.write('FMA;OFD\n') # sets output format to ASCII and asks for Final Data.
res = inst.read()
res = res[11:]
data = re.split('[\n,]',res)

print(res)
inst.write('SRT?\n')
print('FREQ_START='+inst.read(),end='')
inst.write('STP?')
print('FREQ_STOP ='+inst.read(),end='')
inst.write('STEPF?')
print('FREQ_STEP ='+inst.read(),end='')

with open('data/sample.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(res)

f = open('data/sample2.csv', 'w')
f.write(res)
