import math
class Variable:
    def __init__(self, id, rangeString):
        self.id = id
        self.range = []
        self.bitlen = math.ceil(math.log2(len(self.range)))
        self.rangeString = ''
