#from tokens import Token
import html
from tokens import Instruction
from system_hotkey import SystemHotkey
import time
import pyperclip
HTML_COLORS = ['','Yellow', 'Green', 'Red', 'Blue', 'Cyan', 'Peru','Fuchsia','Beige','GreenYellow']
class TabGen():
    def __init__(self,string):
        self.string = string
        a=self.Generate()
        b=self.GenerateBit()
        pyperclip.copy(a+'<br>'+b)
    def Generate(self):
        inst  = Instruction(self.string)
        tokens = inst.tokens
        headerRow = ['Signature','Parameter','Description', 'Length']
        t = html.Table(header_row = headerRow)
        i=1
        for token in tokens:
            colored_cell = html.TableCell('p'+str(i),HTML_COLORS[i])
            print(i)
            parameter_cell = html.TableCell(token.string)
            description_cell = html.TableCell(token.range[0]+'-'+token.range[-1])
            t.rows.append([colored_cell,parameter_cell,description_cell,str(token.length)])
            i=i+1
        htmlcode = '<p>'+inst.instructionTemplate+'</p>\n'
        htmlcode = htmlcode + str(t)
        return htmlcode
    def GenerateBit(self):
        colors = ['DarkGray','LightGrey']
        cells = []
        cells2 = []
        cells3 = []
        cells4=[]
        g=0
        f=0
        t=html.Table()
        for i in range(31,-1,-1):
            if(not(g % 4)):
                f=f+1

            cells3.append(html.TableCell('  ',colors[f%2]))

            cells4.append(' ')
            g=g+1
        g=0
        f=0
        for i in range(31,-1,-1):
            if(not(g % 4)):
                f=f+1
            if(i<10):
                cells.append(html.TableCell('0'+str(i),colors[f%2]))
            else:
                cells.append(html.TableCell(str(i),colors[f%2]))
            cells2.append(' ')
            g=g+1
        t.rows.append(cells3)
        t.rows.append(cells4)
        t.rows.append(cells3)
        t.rows.append(cells4)
        t.rows.append(cells3)
        t.rows.append(cells4)
        t.rows.append(cells3)
        t.rows.append(cells4)
        t.rows.append(cells)
        t.rows.append(cells2)
        htmlcode = str(t)
        return htmlcode
a=""
def saveclip(asd):
    global a
    a = pyperclip.paste()
    print("registered: "+a)
def test(asd):
    instruction = Instruction(a)
    pyperclip.copy(instruction.GenerateTests())
    print("tests ready")
def table(asd):
    b = TabGen(a)
    print("table ready")
hk = SystemHotkey()
hk.register(('control','shift','y'),callback = test )
hk.register(('control','shift','t'),callback = table)
hk.register(('control','shift','r'),callback = saveclip)
while(True):
    time.sleep(0.01)

