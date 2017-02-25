#! /usr/bin/python3

import re
import array
import insdata
from datamem import *
from bitdef import *

MAXROM = 0x800


class pic:
    def __init__(self, ins_table):
        ''' init class with table of instruction set data '''
        self.prog = array.array('H')
        self.data = datamem(256)
        self.clear()

        # program counter high byte
        self.pch = 0

        self.init_ins_info(ins_table)

    def init_ins_info(self, ins_table):
        ''' parse instruction table and build lookup tables '''
        self.ins_ref = {}

        for rec in ins_table:
            # create an instruction info instance
            ins = instruction_info(rec[0])
            ins.arg = rec[1]
            ins.desc = rec[2]
            ins.cycles = rec[3]
            ins.flags = rec[5]

            # get opcode mask and remove any whitespace added for readability
            ins.opcode_mask = rec[4].replace(' ', '')

            # break opcode mask into bit spans for each field for decoding later
            m = re.match('([01]+)x*(b*)(d*)(f*)(n*)(m*)(k*)', ins.opcode_mask)

            # build a dict of fields and their spand
            ins.opcode = m.group(1)
            ins.field_spans = tuple(m.span(i + 1) for i in range(len(ins.field_list)))

            self.ins_ref[ins.opcode] = ins

#        for k in sorted(self.ins_ref):
#            i= self.ins_ref[k]
#            print('    def _{}(self):\n        pass\n'.format(i.mnemonic.lower()))

    def clear(self):
        # special function registers
        self.prog = [0 for i in range(MAXROM)]
        
    def decode(self, word):
        ''' return a tuple of opcode, b, d, f, n, m, k '''

        # convert program word to a bit string
        bits = '{:014b}'.format(word)

        # lookup matching instruction
        for opcode in self.ins_ref:
            ins = self.ins_ref[opcode]
            #print(ins.mnemonic, ins.opcode_mask, ins.opcode)
            if bits.startswith(ins.opcode):
                #print(mnemonic, ins.opcode, ins.field_spans, bits)
                return (ins.mnemonic,) + tuple(bits[span[0]:span[1]] for span in ins.field_spans)

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

        self.set_pc(self.pc + 1)
        
        print(self.format(self.pc, word))
        #self.dispatch(opcode, fields)
        
    def dispatch(self, opcode, fields):
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
      
    def format(self, pc, word):
        fields = self.decode(word)
        mnemonic, opcode, b, d, f, n, m, k = fields

        ins = self.ins_ref[opcode]
 
        # format the optional bit field
        sb = ', {}'.format(b) if len(b) else ''

        # format the optional destination
        if d == '0':
            sd = ', W'
        elif d == '1':
            sd = ', F'
        else:
            sd = ''

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


class instruction_info:
    ''' info on an instruction '''

    field_list = ['opcode', 'b', 'd', 'f', 'n', 'm', 'k']

    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.fields = None
        self.desc = None
        self.cycles = None
        self.flags = None

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

p = pic(insdata.enhmid)

print(p.decode(0b00000001100001))
print(p.decode(0b01100110011101))
print(p.decode(0b00100110010110))
print(p.decode(0b11111000100101))

print(p.format(1, 0b00000001100001))
print(p.format(2, 0b01100110011101))
print(p.format(3, 0b00100110010110))
print(p.format(4, 0b11111000100101))
print(p.format(5, 0b11000101011011))

p.clear()
p.run()
