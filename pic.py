#! /usr/bin/python3
'''
minimal Microchip Pic Enhanced (16f1826) midrange (14bit) core simulator

todo:
- add some same programs using the build in assembler to flesh it out
- finish coding instructions
- add push and pop

'''

import re
import time
import array

import insdata
import binascii
import datamem

MAXROM = 0x800
MAXSTACK = 0x0010 


class Pic:
    def __init__(self, decoder, incfile):
        ''' init class with table of instruction set data '''
        
        # load include file with reg definitions
        self.load_inc_file(incfile)
        
        self.prog = array.array('H')
        self.stack = array.array('H')
        self.data = datamem.DataMem(256, self.reg)
        self.clear()

        # cycle counter
        self.cycles = 0

        # program counter high byte
        self.pch = 0

        self.decoder = decoder

    def load_inc_file(self, filename):
        ''' load the register and config word definitions from .inc file and build a dict'''
        
        with open(filename) as fp:
            self.reg = {}
            for line in fp:
                # STATUS EQU  H'0003'
                m = re.search("(?i)^(\S+)\s+EQU\s+H'(\S+)'", line.strip())
                if m:
                    name, value = m.groups()
                    self.reg[name] = int(value, 16)

    def clear(self):
        ''' clear memory '''
        # special function registers
        self.prog = [0 for i in range(MAXROM)]
        # stack
        self.stack = [0 for i in range(MAXSTACK)]

        self.cycles = 0
        self.pch = 0

    def load_program(self, address, words):
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

    def load(self, f):
        ''' load data from banked memory '''
        address = self.data['BSR'] + f
        return self.data[address]

    def store(self, f, value):
        address = self.data['BSR'] + f
        self.data[address] = value

    def set_data(self, address, value):
        ''' handles writing to special locations '''
        if address < MAXRAM and address & 0x7F == PCL:
            self.set_pc((self.data[PCLATH] << 8) | value)
        else:
            self.data[address] = value
            
    def dump_program(self, address_list):
        ''' dump program memory '''
        for address in address_list:
            print(self.decoder.format(address, self.prog[address]))

    def status(self):
        ''' print the current state of the processor registers '''
        print('PC:{:02X}{:02X} SP:{:02X} BS:{:02X}'.format(self.pch, self.data['PCL'], self.data['STKPTR'], self.data['BSR']), end='')
        
        print(' TO:{} PD:{} Z:{} DC:{} Z:{}'.format(self.get_bit('STATUS', 'NOT_TO'), self.get_bit('STATUS', 'NOT_PD'), self.z, self.dc, self.c), end='')
        
        print(' W:{:02X} CC:{:d}'.format(self.data['WREG'], self.cycles))
        
    def dump_data(self, addresses):
        for i, address in enumerate(addresses):
            if i % 8 == 0:
                print()
                print('{:04X}: '.format(address), end='')

            print('{:02X} '.format(self.data[address]), end='')

        print()

    @property        
    def pc(self):
        ''' get the value of the program counter '''
        return (self.pch << 8) | self.data['PCL']
    
    @pc.setter
    def pc(self, address):
        self.pch, self.data['PCL'] = divmod(address, 0X100)

    @property
    def z(self):
        ''' get STATUS register Z bit as 0 or 1 '''
        return 1 if self.data['STATUS'] & (1 << self.reg['Z']) else 0
    
    @z.setter
    def z(self, value):
        if value:
            self.set_bit('STATUS', 'Z')
        else:
            self.clear_bit('STATUS', 'Z')

    @property
    def c(self):
        ''' get STATUS register Z bit as 0 or 1 '''
        return self.get_bit('STATUS', 'C')

    @c.setter
    def c(self, value):
        if value:
            self.set_bit('STATUS', 'C')
        else:
            self.clear_bit('STATUS', 'C')

    @property
    def dc(self):
        ''' get STATUS register Z bit as 0 or 1 '''
        return self.get_bit('STATUS', 'DC')
    
    @dc.setter
    def dc(self, value):
        if value:
            self.set_bit('STATUS', self.reg['DC'])
        else:
            self.clear_bit('STATUS', self.reg['DC'])
            
    def get_bit(self, register, bit_number):
        ''' get a bit in register specified by number or name '''
        if isinstance(bit_number, str):
            bit_number = self.reg[bit_number]
        return 1 if self.data['STATUS'] & (1 << bit_number) else 0
        
    def set_bit(self, register, bit_number):
        ''' set a bit in a register specified by number or name '''
        if isinstance(bit_number, str):
            bit_number = self.reg[bit_number]
        self.data[register] |= (1 << bit_number)

    def clear_bit(self, register, bit_number):
        ''' clear a bit in a register specified by number or name '''
        if isinstance(bit_number, str):
            bit_number = self.reg[bit_number]
        self.data[register] &= ~(1 << bit_number)

    def push(self):
        ''' push pc onto stack '''
        # get sp
        sp = self.data['STKPTR']

        # Set overflow bit
        if sp == 0x0F:
            self.set_bit('PCON', 'STKOVR')

        # STVREN is not implemented so stack wraps and no reset occurs
        sp = (sp + 1) & 0x0F

        # save return address and update STKPTR
        self.stack[sp] = self.pc
        self.data['STKPTR'] = sp

        
    def pop(self):
        ''' pop value on stack into pc '''
        # get sp
        sp = self.data['STKPTR']

        # set underflow bit
        if sp == 0:
            self.set_bit('PCON', 'STKUNF')

        # restore return address and update STKPTR
        self.pc = self.stack[sp]

        # STVREN is not implemented so stack wraps and no reset occurs
        self.data['STKPTR'] = (sp - 1) & 0x0F

    def reset(self, cond=None):
        self.data.clear()
        if cond is None or cond == self.reg['NOT_POR']:
            self.data['PCON'] = (1 << self.reg['NOT_POR']) | (1 << self.reg['NOT_BOR'])
            self.data['STATUS'] = (1 << self.reg['NOT_PD']) | (1 << self.reg['NOT_TO'])
        elif cond == self.reg['NOT_RI']:
            self.data['PCON'] = (1 << self.reg['NOT_POR']) | (1 << self.reg['NOT_BOR'])
            self.data['STATUS'] = (1 << self.reg['NOT_PD']) | (1 << self.reg['NOT_TO'])

        self.data['STKPTR'] = 0x1F

    def run(self):
        ''' run until pc == 07FF. i.e. GOTO 0x7FF is HALT '''
        start = time.clock()
        while True:
            self.status()
            self.exec()

            # Check for HALT address
            if (self.pc == 0x7FF):
                break

        print('runtime: {:0.2f}ms'.format((time.clock() - start) * 1000))

    def exec(self):
        ''' exec a single instruction '''
 
        word = self.prog[self.pc]
        fields = self.decode(word)

        # display instruction
        print(self.decoder.format(self.pc, word))

        self.cycles += 1
        self.pc += 1
        
        self.dispatch(fields) 

    def decode(self, word):
        return self.decoder.decode(word)
        
    def dispatch(self, fields):
        ''' dispatch opcode to handler '''
        opcode = fields[1]
        return {
            '1100010': self._addfsr,
            '111110': self._addlw,
            '000111': self._addwf,
            '111101': self._addwfc,
            '111001': self._andlw,
            '000101': self._andwf,
            '110111': self._asrf,
            '0100': self._bcf,
            '11001': self._bra,
            '00000000001011': self._brw,
            '0101': self._bsf,
            '0110': self._btfsc,
            '0111': self._btfss,
            '100': self._call,
            '00000000001010': self._callw,
            '0000011': self._clrf,
            '000001000000': self._clrw,
            '00000001100100': self._clrwdt,
            '001001': self._comf,
            '000011': self._decf,
            '001011': self._decfsz,
            '101': self._goto,
            '001010': self._incf,
            '001111': self._incfsz,
            '111000': self._iorlw,
            '000100': self._iorwf,
            '110101': self._lslf,
            '110110': self._lsrf,
            '001000': self._movf,
            '1111110': self._moviw,
            '000000001': self._movlb,
            '1100011': self._movlp,
            '110000': self._movlw,
            '0000001': self._movwf,
            '111111': self._movwi,
            '00000000000000': self._nop,
            '00000001100010': self._option,
            '00000000000001': self._reset,
            '00000000001001': self._retfie,
            '110100': self._retlw,
            '00000000001000': self._return,
            '001101': self._rlf,
            '001100': self._rrf,
            '00000001100011': self._sleep,
            '111100': self._sublw,
            '000010': self._subwf,
            '111011': self._subwfb,
            '001110': self._swapf,
            '00000001100': self._tris,
            '111010': self._xorlw,
            '000110': self._xorwf,
        }[opcode](fields)
        
    # opcode implementations
    def _addfsr(self, fields):
        n = fields[5]
        k = twos_complement(int(fields[7], 2), len(fields[7]))
        if n == '0':
            v = ((self.data['FSR0H'] << 8) | self.data['FSR0L']) + k
            self.data['FSR0H'], self.data['FSR0L'] = divmod(v % 0xFFFF, 0xFF)
        else:
            v = ((self.data['FSR1H'] << 8) | self.data['FSR1L']) + k
            self.data['FSR1H'], self.data['FSR1L'] = divmod(v % 0xFFFF, 0xFF)   

    def _addlw(self, fields):
        k = int(fields[7], 2)
        v = self.data['WREG'] + k
        r = (self.data['WREG'] & 0x0f) + (k & 0xf)
        self.data['WREG'] = v
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _addwf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = self.load(f) + self.data['WREG']
        r = (self.load(f) & 0x0f) + (self.data['WREG'] & 0x0f)
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _addwfc(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = self.load(f) + self.data['WREG'] + self.c
        r = (self.load(f) & 0x0f) + (self.data['WREG'] & 0x0f) + self.c
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _andlw(self, fields):
        k = int(fields[7], 2)
        v = self.data['WREG'] & k
        self.data['WREG'] = v
        self.z = v == 0

    def _andwf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = self.load(f) & self.data['WREG']
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _asrf(self, fields):
        pass

    def _bcf(self, fields):
        f = int(fields[4], 2)
        b = int(fields[2], 2)
        v = self.load(f) & ~(1 << b)
        self.store(f, v)

    def _bra(self, fields):
        k = int(fields[7], 2)
        self.pc += twos_complement(k, len(fields[7]))
        self.cycles += 1

    def _brw(self, fields):
        self.pc += self.data['WREG']
        self.cycles += 1

    def _bsf(self, fields):
        f = int(fields[4], 2)
        b = int(fields[2], 2)
        v = self.load(f) | (1 << b)
        self.store(f, v)

    def _btfsc(self, fields):
        f = int(fields[4], 2)
        b = int(fields[2], 2)
        if not self.load(f) & (1 << b):
            self.pc += 1
            self.cycles += 1

    def _btfss(self, fields):
        f = int(fields[4], 2)
        b = int(fields[2], 2)
        if self.load(f) & (1 << b):
            self.pc += 1
            self.cycles += 1

    def _call(self, fields):
        k = int(fields[7], 2)
        self.push()
        self.pc = (self.data['PCLATH'] & 0b01111000 << 8) | k
        self.cycles += 1

    def _callw(self, fields):
        self.push()
        self.pc = (self.data['PCLATH'] & 0b01111111 << 8) | self.data['WREG']
        self.cycles += 1

    def _clrf(self, fields):
        f = int(fields[4], 2)
        self.store(f, 0)
        self.z = 0

    def _clrw(self, fields):
        self.data['WREG'] = 0
        self.z = 0

    def _clrwdt(self, fields):
        pass

    def _comf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = (self.load(f) - 1) & 0xFF
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _decf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = (~self.load(f)) & 0xFF
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _decfsz(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = (self.load(f) - 1) & 0xFF
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        if not v:
            self.pc += 1
            self.cycles += 1

    def _goto(self, fields):
        k = int(fields[7], 2)
        self.pc = (self.data['PCLATH'] & 0b01111000 << 8) | k
        self.cycles += 1

    def _incf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = (self.load(f) + 1) & 0xFF
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _incfsz(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = (self.load(f) + 1) & 0xFF
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        if not v:
            self.pc += 1
            self.cycles += 1

    def _iorlw(self, fields):
        k = int(fields[7], 2)
        v = self.data['WREG'] | k
        self.data['WREG'] = v
        self.z = v == 0

    def _iorwf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = self.load(f) | self.data['WREG']
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _lslf(self, fields):
        pass

    def _lsrf(self, fields):
        pass

    def _movf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = self.load(f)
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v

    def _moviw(self, fields):
        pass

    def _movlb(self, fields):
        k = int(fields[7], 2)
        self.data['BSR'] = k

    def _movlp(self, fields):
        k = int(fields[7], 2)
        self.data['PCLATH'] = k

    def _movlw(self, fields):
        k = int(fields[7], 2)
        self.data['WREG'] = k

    def _movwf(self, fields):
        f = int(fields[4], 2)
        v = self.data['WREG']
        self.store(f, v)

    def _movwi(self, fields):
        pass

    def _nop(self, fields):
        pass

    def _option(self, fields):
        self.data['OPTION' ] = self.data['WREG']

    def _reset(self, fields):
        self.reset(self.reg['NOT_RI'])
        
    def _retfie(self, fields):
        pass

    def _retlw(self, fields):
        k = int(fields[7], 2)
        self.data['WREG'] = k
        self.pop()
        self.cycles += 1

    def _return(self, fields):
        self.pop()
        self.cycles += 1

    def _rlf(self, fields):
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
        f = int(fields[4], 2)
        if f == '101':
            self.data['TRISA'] = self.data['WREG']
        elif F == '110':
            self.data['TRISB'] = self.data['WREG']

    def _xorlw(self, fields):
        k = int(fields[7], 2)
        v = self.data['WREG'] ^ k
        self.data['WREG'] = v
        self.z = v == 0

    def _xorwf(self, fields):
        f = int(fields[4], 2)
        d = fields[3]
        v = self.load(f) ^ self.data['WREG']
        if d == '0':
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0
  

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
    
    def __str__(self):
        s = self.opcode
        for field, span in zip(self.field_list, self.field_spans):
            if span[0] != span[1]:
                s += ', {}={}'.format(field, span)
            
        return s


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
            x, y = ins.field_spans[i]
            if field_name in kwargs:
                bits += '{:0{}b}'.format(kwargs[field_name], y - x)
            elif field_name != 'opcode' and x != y:
                raise IndexError('{} {}:{} missing'.format(field_name, x, y))
        
        # convert from string to numeric
        return int(bits, 2)

    def format(self, pc, word):
        fields = self.decode(word)
        ins, opcode, b, d, f, n, m, k = fields

        if len(f) and len(d):
            sd = 'W' if d == '0' else 'F'
            return '{:04x}  {:10} 0x{:02x}, {}'.format(pc, ins.mnemonic, int(f, 2), sd)
        elif len(f) and len(b):
            return '{:04x}  {:10} 0x{:02x}, {}'.format(pc, ins.mnemonic, int(f, 2), b)
        elif len(f):
            return '{:04x}  {:10} 0x{:02x}'.format(pc, ins.mnemonic, int(f, 2))
        elif len(n) and len(k):
            return '{:04x}  {:10} FSR{}, 0x{:02x}'.format(pc, ins.mnemonic, n, int(k, 2))
        elif len(k) > 8:
            return '{:04x}  {:10} 0x{:03x}'.format(pc, ins.mnemonic, int(k, 2))
        elif len(k):
            return '{:04x}  {:10} 0x{:02x}'.format(pc, ins.mnemonic, int(k, 2))
        else:
            return '{:04x}  {:10}'.format(pc, ins.mnemonic)


def twos_complement(input_value, num_bits):
    '''Calculates a two's complement integer from the given input and num bits'''
    mask = 2**(num_bits - 1)
    return -(input_value & mask) + (input_value & ~mask)

def test():
    d = datamem.datamem(256)

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
    
    x = decoder.encode('GOTO', k=0x65)
    print(decoder.format(0, x))


def code1(p, d):
    ''' Simple countdown loop'''
    code = [
        d.encode('GOTO', k=0x004),
        d.encode('NOP'),
        d.encode('NOP'),
        d.encode('NOP'),
        d.encode('MOVLW', k=0x10),
        d.encode('MOVWF', f=0x30),
        d.encode('DECFSZ', d=1, f=0x30),
        d.encode('BRA', k=-2 & 0x1ff),

        d.encode('CALL', k=0x00A),

        d.encode('GOTO', k=0x7FF),

        d.encode('MOVLW', k=0x45),
        d.encode('MOVWF', f=0x31),
        d.encode('ANDLW', k=0x00),
        d.encode('RETURN'),
        
    ]

    p.load_program(0, code)
    p.dump_program(range(len(code)))
    print()
 
def code2(p, d):
    p.load_from_file('test.hex')

if __name__ == '__main__':
    decoder = Decoder(insdata.ENHMID)
    p = Pic(decoder, 'p16f1826.inc')

    code1(p, decoder)
    p.run()

    p.dump_data(range(64))
