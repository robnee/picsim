class sfrmem():
    def __init__(self:
        self.maxram = 0x20 * 0x20
        self.sfr = array.array('B')
        self.clear()

    def clear(self):
        # general purpose ram
        self.sfr = [0 for i in range(self.maxram)]

    def translate(self, address):
        ''' translate banked address into a linear data address '''
        if 0 <= address <= MAXRAM:
            bank, location = divmod(address, 0x80)
            if location <= 0x20:
                raise IndexError(address, location)
            elif location >= 0x70:
                bank = 0
            # bank 0 has the extra 0x10 bytes of common ram
            if bank == 0:
                return location - 0x20
            else:
                return 0x10 + bank * 0x60 + (location - 0x20)
        elif 0x2000 <= address <= 0x29AF:
            # convert to a bank, location
            bank, location = divmod(address - 0x2000, 0x50)
            # the common ram in bank 0 is not included
            if bank == 0:
                return location
            else:
                return 0x10 + bank * 0x50 + location

        raise IndexError()



class gprmem():
    def __init__(self, maxram):
        self.maxram = maxram
        self.gpr = array.array('B')
        self.clear()

    def clear(self):
        # general purpose ram
        self.gpr = [0 for i in range(self.maxram)]

    def translate(self, address):
        ''' translate banked address into a linear data address '''
        if 0 <= address <= MAXRAM:
            bank, location = divmod(address, 0x80)
            if location <= 0x20:
                raise IndexError(address, location)
            elif location >= 0x70:
                bank = 0
            # bank 0 has the extra 0x10 bytes of common ram
            if bank == 0:
                return location - 0x20
            else:
                return 0x10 + bank * 0x60 + (location - 0x20)
        elif 0x2000 <= address <= 0x29AF:
            # convert to a bank, location
            bank, location = divmod(address - 0x2000, 0x50)
            # the common ram in bank 0 is not included
            if bank == 0:
                return location
            else:
                return 0x10 + bank * 0x50 + location

        raise IndexError()

    def __getitem__(self, address):
        location = self.translate(address)
        return self.gpr[location]

    def __setitem__(self, address, value):
        location = self.translate(address)
        self.gpr[location] = value


