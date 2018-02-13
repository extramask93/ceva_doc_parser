import re
import pyperclip
import math
class Database:
    def __init__(self):
        file = open('database.txt')
        self.string_ = file.readlines()
        file.close()
    def find(self,tokenName):
        tokenName = re.escape(tokenName)
        for line in self.string_:
            if(re.search(tokenName,line) is not None):
                return line
        return None
    def getVariables(self,tokenName):
        line = self.find(tokenName)
        if(line is None):
            return None
        result = []
        variablesAndValues = line.split('|')[1:]
        for i in range(0,len(variablesAndValues),2):
            result.append((variablesAndValues[i].strip(),variablesAndValues[i+1].strip()))
        return result

class RangeGenerator:
    def __init__(self):
        pass
    def getImmediateRange(self, immediateToken, hexflag):
        result = []
        shiftee = 0
        if(re.search('u',immediateToken) is not None):
            uimmediate = 1
        else:
            uimmediate = 0
        #get nr of bits
        constant = re.search('#-*(0x)*-*[0-9a-fA-F]+',immediateToken)
        if(constant is not None):
            return [constant.group(0)]
        seresult = re.search('\d+',immediateToken)
        if(re.search('uimm',immediateToken) is not None):
            uimmediate=1
        if(seresult is None):
            return result
        else:
            bitnr = int(seresult.group(0))
        for i in range(0,bitnr+uimmediate):
            if(uimmediate):
                if(immediateToken[-1] is ','):
                    result.append('#'+hex(shiftee)+',')
                else:
                    result.append('#'+hex(shiftee))
            else:
                result.append('#'+str(shiftee)+immediateToken[-1])

            shiftee = (shiftee<<1)|1
        if(not hexflag and not uimmediate):
            result[-1] = '#-'+str((shiftee>>1)+1)+immediateToken[-1]
        return result
    def getFlagRange(self, flagToken):
        result = []
        flags = re.search('{(.*)}',flagToken)
        if(flags is not None):
            flags = flags.group(1)
            flags = flags.split('|')
            for flag in flags:
                result.append('{'+flag+'}')
        return result
    def generateFixedRange(self,rangeString):
            return rangeString.split(',')
    def generateFromTo(self, rangeString):
            temp = rangeString.split('~')
            result=[]
            minimal = int(temp[0])
            maximal = int(temp[1])
            bitnr = bin(maximal).count("1")
            for i in range(0,bitnr+1):
                result.append(str((1<<i)-1))
            if(result[-1] == '15'):
                result[-1]='14'
                result.append('15')
            return result
    def getOptionalRegRange(self,rangeString):
        result = ['']
        result=result+self.getRange(rangeString)
        print(result)
        return result
    def getRange(self,rangeString):
        a=[]
        if(re.search('~',rangeString) is not None):
            a=self.generateFromTo(rangeString)
        else:
            a =self.generateFixedRange(rangeString)
        return a
class Token():
    def __init__(self,string):
        self.string = string
        self.r = RangeGenerator()
        self.d = Database()
        self.length = 0
        self.nrOfVariables = 1
        self.variables = [string]
        self.range=[]
        self.defaultValue=''
        self.signed = False
    def getType(self,string):
        if(self.signed==True):
            return string.split(']')[1]
        else:
            temp = re.sub('[\[\]]','', string)
            return temp.split('.')[1]
    def getRegister(self,string):
        return string.split('.')[0]
class ImmediateToken(Token):
    def __init__(self,string):
        Token.__init__(self,string)
        if(re.search('u',self.string) is None):
            self.signed = True
        else:
            self.signed =False
        self.length = int(re.search('\d+',self.string).group(0))
        self.range = self.r.getImmediateRange(self.string,self.signed)
        self.defaultVal = self.range[0]
        
class FlagToken(Token):
    def __init__(self,string):
        Token.__init__(self,string)
        self.range=self.r.getFlagRange(self.string)
        self.defaultVal = self.range[0]
        
class OptionalRegToken(Token):
    def __init__(self, string):
        Token.__init__(self,string)
        reg = self.getRegister(self.string)[2:]
        var = self.d.getVariables(reg)
        self.var = var
        self.nrOfVariables = len(var)
        rangesize =0;
        defaultsmag = []
        self.defaultVal = ''
        self.string = re.sub('\[|\]','',self.string)
        for pair in var:
            defaultsmag.append((pair[0],self.r.getRange(pair[1])[0]))
        for pair in var:
            ran = self.r.getRange(pair[1])
            for z in ran:
                temp = self.string
                temp = temp.replace(pair[0],z)
                for default in defaultsmag:
                    temp = temp.replace(default[0],default[1])
                self.range.append(self.getRegister(temp)+'.'+self.getType(temp))
        a= re.search('\d+',self.range[-1]).group(0)
        self.length = int(math.ceil(math.log2(float(a))))
                
class RegisterToken(Token):
    def __init__(self,string):
        Token.__init__(self,string)
        reg = self.getRegister(self.string)
        var = self.d.getVariables(reg)
        self.nrOfVariables = len(var)
        self.var = var
        defaultsmag = []
        self.defaultVal = self.string
        if(var is None):
            self.defaultVal = re.sub('[A-Z]','',self.string)
            self.range.append(self.defaultVal)
            return
            print(var)
        for pair in var:
            self.defaultVal = self.defaultVal.replace(pair[0], self.r.getRange(pair[1])[0])
            self.defaultVal = self.getRegister(self.defaultVal)+'.'+self.getType(self.defaultVal)
            defaultsmag.append((pair[0],self.r.getRange(pair[1])[0]))
        for pair in var:
            ran = self.r.getRange(pair[1])
            for z in ran:
                temp = self.string
                temp = temp.replace(pair[0],z)
                for default in defaultsmag:
                    temp = temp.replace(default[0],default[1])
                self.range.append(self.getRegister(temp)+'.'+self.getType(temp))
        a= re.search('\d+',self.range[-1]).group(0)
        self.length = int(math.ceil(math.log2(float(a))))
class TokenFactory:
    def __init__(self):
        pass
    def getToken(self, tokenString):
        if(tokenString[0]=='#'):
            return ImmediateToken(tokenString)
        elif(tokenString[0]=='{'):
            return FlagToken(tokenString)
        elif(tokenString[0]=='['):
            return OptionalRegToken(tokenString)
        else:
            return RegisterToken(tokenString)
class Instruction:
    def __init__(self, instructionTemplate):
        self.instructionTemplate = self._RemoveWhitespaces(instructionTemplate)
        self.stringTokens = self._Tokenize(self.instructionTemplate)
        if(len(self.stringTokens)<1):
            return
        self.instructionName = self.stringTokens[0]
        self.stringTokens = self.stringTokens[1:]
        self.tokens = []
        factory = TokenFactory()
        for token in self.stringTokens:
            self.tokens.append(factory.getToken(token))
    def _Tokenize(self,string):
        tokens = string.split(' ')
        for token in tokens:
            token.strip()
        return tokens
    def _RemoveWhitespaces(self,string):
        string = string.strip()
        buffer = ''
        if(re.search('{',string) is None):
            return string
        else:
            posopening=string.find('{')
            posclosing=string.find('}')
            fname = string[:posopening].strip()
            flags = re.sub(' ','',string[posopening:posclosing+1]).strip()
            rest=string[posclosing+1:].strip()
            return fname+' '+flags+' '+rest
    def GenerateTests(self):
        string=""
        for i in range(0, len(self.tokens)):
            for ran in self.tokens[i].range:
                instrstring=""
                d = 0
                instrstring =instrstring+self.instructionName+" "
                while(d<i):
                    instrstring = instrstring+self.tokens[d].defaultVal
                    d=d+1
                instrstring = instrstring+ran
                d=i+1
                while(d<len(self.tokens)):
                    instrstring = instrstring+self.tokens[d].defaultVal
                    d=d+1
                string = string+'asm(\"'+instrstring+'\");\n'
        return string

    def GetFlagDefaultValue(self, token):
        if(re.search('^{[.*]}$',token)is not None):
            return ''
        else:
            return token.split('|')[0]
        

        

    
