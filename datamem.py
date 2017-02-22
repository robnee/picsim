import array

MAXRAM = 0x1000
MAXSTACK = 0x0010 

class datamem():
    def __init__(self, maxram):
        self.maxram = maxram
        self.sfr = array.array('B')
        self.gpr = array.array('B')
        self.stack = array.array('H')
        self.clear()

    def clear(self):
        # special function registers
        self.sfr = [0 for i in range(0x20 * 0x20)]
        # general purpose ram
        self.gpr = [0 for i in range(self.maxram)]
        # stack
        self.stack = [0 for i in range(0x10)]

    def translate(self, address):
        ''' translate into bank, location, linear using traditional or linear data addressing '''
        if 0 <= address <= 0xFFF:
            bank, location = divmod(address, 0x80)
            if location <= 0x0B:
                return 0, location, 0
            if location >= 0x70:
                return 0, location, location - 0x20
            else:
                return bank, location, 0x10 + bank * 0x50 + (location - 0x20)
        elif 0x2000 <= address <= 0x29AF:
            # convert to a bank, location
            bank, location = divmod(address - 0x2000, 0x50)
            if bank == 0:
                return bank, 0x20 + location, location
            else:
                return bank, 0x20 + location, address - 0x2000 + 0x10
        else:
            raise IndexError()

    def __getitem__(self, address):
        bank, location, linear = self.translate(address)
        #print(hex(bank), hex(location), hex(linear))
        if location < 0x20:
            return self.sfr[bank * 0x20 + location]
        else:
            return self.gpr[linear]

    def __setitem__(self, address, value):
        bank, location, linear = self.translate(address)
        #print(hex(bank), hex(location), hex(linear))
        if location < 0x20:
            self.sfr[bank * 0x20 + location] = value
        else:
            self.gpr[linear] = value
