'''
implement a Pic's data memory. this includes the quirks of the non-linear address space and 
common ram regions as well as the special function registers that map to multiple locations.

there are 32 banks of 128 bytes in the traditional addressing scheme. the lower 32 bytes of
each bank is dedicated to special function registers. the first 12 SFR locations in every
bank all map back to the first 12 bytes of bank zero.  locations in each bank above the SFR
region is mapped to general purpose registers (RAM). this is implemented as a contiguous
vector.  these gpr locations are spread over the first n banks. typically the first 3 or 4.
the top 16 locations of gpr in all banks map to bank zero called common ram. 

the gpr memory may be accessed as a continuous vector (excluding common ram) using addresses
starting at 0x2000

translate function resolves addresses into a bank, location and linear gpr address.  it also
accepts addresses as register names which it looks up in a dictionary. 

__setitem__ and __getitem__ use the translation function to resolve addresses and then set
or get a value from the correct region (sfr, gpr)
'''

import array

MAXRAM = 0x1000

class DataMem():
    def __init__(self, maxram, reg):
        self.maxram = maxram
        self.sfr = array.array('B')
        self.gpr = array.array('B')
        
        # register names
        self.reg = reg
        
        self.clear()

    def clear(self):
        # special function registers
        self.sfr = [0 for i in range(0x20 * 0x20)]
        # general purpose ram
        self.gpr = [0 for i in range(self.maxram)]

    def translate(self, address):
        ''' translate into bank, location, linear using traditional or linear data addressing '''
        
        # allow location to be a register name or int address 
        address = self.reg[address] if isinstance(address, str) else address
        
        # determine if this is a traditional (0x1000) or linear (0x2000) address
        if 0 <= address <= 0xFFF:
            bank, location = divmod(address, 0x80)
            if location <= 0x0B:
                return 0, location, None
            elif location < 0x20:
                return bank, location, None
            elif bank == 0 or location >= 0x70:
                return 0, location, location - 0x20
            # stack and shadow registers are annoyingly not in SFR space.  As a kludge move them
            # there or they will be mapped to gpr
            elif bank == 31 and location >= 0x60:
                return bank, location - 0x50, location
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
        #print(address, hex(bank), hex(location), hex(linear))
        if location < 0x20:
            return self.sfr[bank * 0x20 + location]
        else:
            return self.gpr[linear]

    def __setitem__(self, address, value):
        bank, location, linear = self.translate(address)
        #print(hex(bank), hex(location), hex(linear))
        if location < 0x20:
            self.sfr[bank * 0x20 + location] = value & 0xFF
        else:
            self.gpr[linear] = value & 0xFF
