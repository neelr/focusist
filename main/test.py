import torch
from torch import nn
import serial
import requests
import torch.nn.functional as F
test = [
	[776562, 29799, 11917, 28458, 3013, 21218, 4797, 2312], 
	[338759, 36824, 3401, 10572, 19483, 38304, 1835, 1240], 
	[167928, 47582, 9354, 72337, 1531, 49123, 1592, 2883], 
	[70611, 19757, 384, 1404, 4351, 6897, 2726, 1855], 
	[91929, 92444, 9277, 35640, 2687, 29261, 655, 758], 
	[642915, 435756, 14802, 110245, 11255, 59355, 45325, 7356], 
	[624240, 37472, 10811, 11281, 7926, 40668, 1176, 1217], 
	[101811, 17390, 6177, 9043, 5532, 48450, 2038, 628], 
	[1005442, 91052, 15124, 52633, 24024, 151750, 5657, 2974], 
	[131823, 36618, 3422, 36435, 749, 30678, 2427, 1254]
]

url = 'http://192.168.1.86:3000/speak'
myobj = {'text': ''}
x = requests.post(url, json = myobj)
print(x)
print("Loading Model")
class model(nn.Module):
    def __init__(self):
        super().__init__()
        self.dropout = nn.Dropout(0.5)
        self.layer1 = nn.Linear(80, 70)
        self.layer2 = nn.Linear(70, 50)
        self.layer3 = nn.Linear(50, 50)
        self.layer4 = nn.Linear(50, 10)
        self.layer5 = nn.Linear(10, 2)
        self.sigmoid = nn.Sigmoid()
    def forward(self, xb):
        initial = xb.size(0)
        xb = xb.view(initial, 1, -1)
        xb = self.layer1(xb)
        xb = self.layer2(xb)
        xb = self.dropout(xb)
        xb = self.layer3(xb)
        xb = self.dropout(xb)
        xb = self.layer4(xb)
        xb = self.dropout(xb)
        xb = self.layer5(xb)
        xb = self.sigmoid(xb.view(initial,-1))
        return xb.double()
brain = model()
brain.load_state_dict(torch.load("brain.pth"))
brain.eval()
out = brain(F.normalize(torch.tensor([test]).float(),dim=2))
print(f"{int(out[0][0]*100)}% VIDEO and {int(out[0][1]*100)}% STOODY")
ser = serial.Serial('/dev/cu.usbmodem141101', baudrate=9600, timeout=2)
ser.flushInput()
ser.flushOutput()
buff2die = 0
first = 1
buffer = []
print("Starting serial read")
while True:
    if first % 2 == 0:
        first += 1
        data_raw = str(ser.readline())
        data = data_raw.split(",")
        data[10] = data[10][:len(data[10])-5]
        data = data[3:]
        data = list(map(float,data))
        buffer.append([x / 10000 for x in data])
        if len(buffer) == 10:
            out= brain(torch.tensor([buffer]))
            print(f"{int(out[0][0]*100)}% VIDEO and {int(out[0][1]*100)}% STOODY")
            if out[0][0] > out[0][1]:
                print("hi")
                buff2die += 1
            else:
                buff2die = 0
            if buff2die == 4:
                url = 'http://192.168.1.86:3000/speak'
                myobj = {'text': 'get back to work neel, you suck'}
                x = requests.post(url, json = myobj)
                buff2die = 0

            buffer.pop()
    else:
        ser.readline()
        first += 1