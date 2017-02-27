#! /usr/bin/python3

import re
import array
import insdata
import binascii
from datamem import *
from bitdef import *

MAXROM = 0x800


class Pic:
    def __init__(self, decoder):
        ''' init class with table of instruction set data '''
        self.prog = array.array('H')
        self.data = DataMem(256)
        self.clear()

        # cycle counter
        self.cycles = 0

        # program counter high byte
        self.pch = 0

        self.decoder = decoder

#        for k in sorted(self.ins_ref):
#            i= self.ins_ref[k]
#            print('    def _{}(self):\n        pass\n'.format(i.mnemonic.lower()))

    def clear(self):
        ''' clear memory '''
        # special function registers
        self.prog = [0 for i in range(MAXROM)]

        self.cycles = 0
        self.pch = 0

    def load(self, address, words):
        ''' load program memory '''
        for i, word in enumerate(words):
            self.prog[address + i] = word

    def load_from_file(self, filename):
        self.clear()
        
        base = 0x00
        
        with open(filename) as fp:
            for line in fp:
                m = re.search('^:(\S\S)(\S\S\S\S)(\S\S)(\S*)(\S\S)', line.strip())
                count, address, rectype, data, checksum = m.groups()
        
                # Convert data fields from hex
                count = int(count, 16)
        
                # Look for a extended address record
                if rectype == '04':
                    base = int(data, 16) << 16
        
                # compute checksum of data
                sum = 0
                for hex_byte in [data[i: i + 2] for i in range(0, len(data), 2)]:
                    sum += int(hex_byte, 16)
                    
                # add other fields from record
                sum += count + int(address[0:2], 16) + int(address[2:4], 16) + int(rectype, 16)
                
                # convert to intel style
                sum = '{:02X}'.format((~sum + 1) & 0xff)
                
                assert sum == checksum, "Record at address ({} {}) has bad checksum ({})  I get {}".format(base, address, checksum, sum)
        
                # load words into program mem
                if rectype == '00':
                    full_address = base + int(address, 16) // 2
                    if full_address < len(self.prog):
                        for i in range(count // 2):
                            word = int(data[i * 4 + 2:i * 4 + 4] + data[i * 4:i * 4 + 2], 16)
                            self.prog[full_address + i] = word
        
                            #print('{:04x} {:02x} {:02x} {:04x}'.format(full_address, count, i, word))

    def set_data(self, address, value):
        ''' handles writing to special locations '''
        if address < MAXRAM and address & 0x7F == PCL:
            self.set_pc((self.data[PCLATH] << 8) | value)
        else:
            self.data[address] = value
            
    def get_pc(self):
        return (self.pch << 8) | self.data[PCL]
        
    def set_pc(self, address):
        self.pch, self.data[PCL] = divmod(address, 0X100)

    def reset(self, cond=NOT_POR):
        self.data.clear()
        if cond == NOT_POR:
            data[PCON] = (1 << NOT_POR) | (1 << NOT_BOR)
            data[STATUS] = (1 << NOT_PD) | (1 << NOT_TO)
        elif cond == NOT_RI:
            data[PCON] = (1 << NOT_POR) | (1 << NOT_BOR)
            data[STATUS] = (1 << NOT_PD) | (1 << NOT_TO)  

    def run(self):
        for _ in range(10):
            self.exec()

    def exec(self):
        ''' exec a single instruction '''
        
        self.pc = self.get_pc()
 
        word = self.prog[self.pc]
        fields = self.decode(word)

        self.cycles += 1
        self.set_pc(self.pc + 1)
        
        print(self.decoder.format(self.pc, word))
        #self.dispatch(opcode, fields)

    def decode(self, word):
        return self.decoder.decode(word)
        
    def dump(self, address_list):
        for address in address_list:
            print(self.decoder.format(address, self.prog[address]))
        
    def dispatch(self, opcode, fields):
        ''' dispatch opcode to handler '''
        return {
            '1100010': _addfsr,
            '111110': _addlw,
            '000111': _addwf,
            '111101': _addwfc,
            '111001': _andlw,
            '000101': _andwf,
            '110111': _asrf,
            '0100': _bcf,
            '11001': _bra,
            '00000000001011': _brw,
            '0101': _bsf,
            '0110': _btfsc,
            '0111': _btfss,
            '100': _call,
            '00000000001010': _callw,
            '0000011': _clrf,
            '000001000000': _clrw,
            '00000001100100': _clrwdt,
            '001001': _comf,
            '000011': _decf,
            '001011': _decfsz,
            '101': _goto,
            '001010': _incf,
            '001111': _incfsz,
            '111000': _iorlw,
            '000100': _iorwf,
            '110101': _lslf,
            '110110': _lsrf,
            '001000': _movf,
            '1111110': _moviw,
            '000000001': _movlb,
            '1100011': _movlp,
            '110000': _movlw,
            '0000001': _movwf,
            '111111': _movwi,
            '00000000000000': _nop,
            '00000001100010': _option,
            '00000000000001': _reset,
            '00000000001001': _retfie,
            '110100': _retlw,
            '00000000001000': _return,
            '001101': _rle,
            '001100': _rrf,
            '00000001100011': _sleep,
            '111100': _sublw,
            '000010': _subwf,
            '111011': _subwfb,
            '001110': _swapf,
            '00000001100': _tris,
            '111010': _xorlw,
            '000110': _xorwf,
        }[opcode](fields)
        
    # opcode implementations
    def _addfsr(self, fields):
        pass

    def _addlw(self, fields):
        pass

    def _addwf(self, fields):
        pass

    def _addwfc(self, fields):
        pass

    def _andlw(self, fields):
        pass

    def _andwf(self, fields):
        pass

    def _asrf(self, fields):
        pass

    def _bcf(self, fields):
        pass

    def _bra(self, fields):
        pass

    def _brw(self, fields):
        pass

    def _bsf(self, fields):
        pass

    def _btfsc(self, fields):
        pass

    def _btfss(self, fields):
        pass

    def _call(self, fields):
        pass

    def _callw(self, fields):
        pass

    def _clrf(self, fields):
        pass

    def _clrw(self, fields):
        pass

    def _clrwdt(self, fields):
        pass

    def _comf(self, fields):
        pass

    def _decf(self, fields):
        pass

    def _decfsz(self, fields):
        pass

    def _goto(self, fields):
        pass

    def _incf(self, fields):
        pass

    def _incfsz(self, fields):
        pass

    def _iorlw(self, fields):
        pass

    def _iorwf(self, fields):
        pass

    def _lslf(self, fields):
        pass

    def _lsrf(self, fields):
        pass

    def _movf(self, fields):
        pass

    def _moviw(self, fields):
        pass

    def _movlb(self, fields):
        pass

    def _movlp(self, fields):
        pass

    def _movlw(self, fields):
        pass

    def _movwf(self, fields):
        pass

    def _movwi(self, fields):
        pass

    def _nop(self, fields):
        pass

    def _option(self, fields):
        pass

    def _reset(self, fields):
        self.reset(NOT_RI)
        
    def _retfie(self, fields):
        pass

    def _retlw(self, fields):
        pass

    def _return(self, fields):
        pass

    def _rle(self, fields):
        pass

    def _rrf(self, fields):
        pass

    def _sleep(self, fields):
        pass

    def _sublw(self, fields):
        pass

    def _subwf(self, fields):
        pass

    def _subwfb(self, fields):
        pass

    def _swapf(self, fields):
        pass

    def _tris(self, fields):
        pass

    def _xorlw(self, fields):
        pass

    def _xorwf(self, fields):
        pass
  

class InstructionInfo:
    ''' info on an instruction '''

    field_list = ['opcode', 'b', 'd', 'f', 'n', 'm', 'k']

    def __init__(self, rec):
        self.mnemonic, self.arg, self.desc, self.cycles, self.opcode_mask, self.flags, self.notes = rec

        # get opcode mask and remove any whitespace
        # break opcode mask into bit spans for each field for decoding later
        m = re.match('([01]+)x*(b*)(d*)(f*)(n*)(m*)(k*)', self.opcode_mask.replace(' ', ''))

        # build a tuple of fields and their spans
        self.opcode = m.group(1)
        self.field_spans = tuple(m.span(i + 1) for i in range(len(self.field_list)))


class Decoder:
    ''' Decodes and encodes instructions from/to 14 bit program words'''
        
    def __init__(self, data):
        ''' parse instruction table and build lookup tables '''
        self.ins_list = []
        self.mnemonic_dict = {}

        for rec in data:
            ins = InstructionInfo(rec)
            self.ins_list.append(ins)
            self.mnemonic_dict[ins.mnemonic] = ins

    def decode(self, word):
        ''' return a tuple of ins, opcode, b, d, f, n, m, k '''

        # convert program word to a bit string
        bits = '{:014b}'.format(word)

        # the instruction word starts with the instruction opcode.  Use a generator
        # comprehension to find match.  It returns a list so use a comma on the lhs
        # to force an unpack.  An exception is thrown if no or multiple matches
        ins, = [item for item in self.ins_list if bits.startswith(item.opcode)]

        #print(mnemonic, ins.opcode, ins.field_spans, bits)
        return (ins,) + tuple(bits[x:y] for x, y in ins.field_spans)

#        for k in sorted(self.ins_ref):
#            i= self.ins_ref[k]
#            print('    def _{}(self):\n        pass\n'.format(i.mnemonic.lower()))

    def encode(self, mnemonic, **kwargs):
        # find matching mnemonic in instruction table
        ins = self.mnemonic_dict[mnemonic.upper()]

        bits = ins.opcode

        # build instruction from fields starting after opcode
        for i, field_name in enumerate(InstructionInfo.field_list):
            if field_name in kwargs:
                x, y = ins.field_spans[i]
                bits += '{:0{}b}'.format(kwargs[field_name], y - x)

        print(bits, int(bits, 2))
        # convert from string to numeric
        return int(bits, 2)

    def format(self, pc, word):
        fields = self.decode(word)
        ins, opcode, b, d, f, n, m, k = fields

        # format the optional bit field
        sb = ', {}'.format(b) if len(b) else ''

        if len(f) and len(d):
            sd = 'W' if d == '0' else 'F'
            return '{:04x}  {:10} 0x{:02x}, {}'.format(pc, ins.mnemonic, int(f, 2), sd)
        elif len(f) and len(b):
            return '{:04x}  {:10} 0x{:02x}, {}'.format(pc, ins.mnemonic, int(f, 2), b)
        elif len(f):
            return '{:04x}  {:10} 0x{:02x}'.format(pc, ins.mnemonic, int(f, 2))
        elif len(n) and len(k):
            return '{:04x}  {:10} FSR{}, 0x{:02x}'.format(pc, ins.mnemonic, n, int(k, 2))
        elif len(k):
            return '{:04x}  {:10} 0x{:02x}'.format(pc, ins.mnemonic, int(k, 2))
        else:
            return '{:04x}  {:10}'.format(pc, ins.mnemonic)




def test():
    d = datamem(256)

    d[0x7f] = 5
    d[0xa5] = 4
    d[STATUS] = 7

    print(hex(0x50), d.translate(0x50))
    print(hex(0x125), d.translate(0x125))
    print(hex(0x1ff), d.translate(0x1ff), d[0x1ff])
    print(hex(0xa5), d.translate(0xa5), d[0xa5])
    print(hex(0x2055), d.translate(0x2055), d[0x2055])
    print(hex(0x204f), d.translate(0x204f), d[0x204f])
    print(hex(0x2050), d.translate(0x2050), d[0x2050])
    
    print(decoder.format(1, 0b00000001100001))
    print(decoder.format(2, 0b01100110011101))
    print(decoder.format(3, 0b00100110010110))
    print(decoder.format(4, 0b11111000100101))
    print(decoder.format(5, 0b11000101011011))

decoder = Decoder(insdata.ENHMID)
p = Pic(decoder)

x = decoder.encode('GOTO', k=0x65)
print(decoder.format(0, x))

p.clear()
p.load(0, [0b01100110011101, 0b00100110010110])
#p.run()

p.load_from_file('test.hex')
p.dump(range(20))
