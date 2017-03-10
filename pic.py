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
import datamem

MAXROM = 0x800
MAXSTACK = 0x0010


class Pic:
    def __init__(self, decoder, incfile):
        ''' init class with table of instruction set data '''
        
        # load include file with reg definitions
        self.load_inc_file(incfile)

        self.stack = array.array('H')
        self.data = datamem.DataMem(256, self.reg)
        self.clear()

        # cycle counter
        self.cycles = 0

        # program counter high byte
        self.pch = 0

        self.decoder = decoder

    def load_inc_file(self, filename):
        ''' load the register and config word definitions from .inc file and build a dict '''
        
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
        self.prog = [None for i in range(MAXROM)]
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
    
    def load_indirect(self, address):
        ''' inderect adressing which can access fraditional, linear and program mem '''
        if 0x8000 <= address < 0x8000 + MAXROM:
            ins = self.prog[address - 0x8000]
            word = int(ins.to_bits(), 2) if ins else 0
            return word & 0xFF
        elif address < 0x29B0:
            return self.data[address]
        else:
            return 0

    def store(self, f, value):
        ''' banked store '''
        address = self.data['BSR'] + f
        self.data[address] = value

    def store_indirect(self, address, value):
        if address < 0x29B0:
            self.data[address] = value
        
    def set_data(self, address, value):
        ''' handles writing to special locations '''
        if address < datamem.MAXRAM and address & 0x7F == self.reg['PCL']:
            self.set_pc((self.data['PCLATH'] << 8) | value)
        else:
            self.data[address] = value
            
    def dump_program(self, address_list):
        ''' dump program memory '''
        for address in address_list:
            print('{:04X}  '.format(address), self.prog[address])

    def status(self):
        ''' print the current state of the processor registers '''
        print('PC:{:02X}{:02X} SP:{:02X} BS:{:02X}'.format(self.pch, self.data['PCL'], self.data['STKPTR'], self.data['BSR']), end='')
        
        print(' TO:{} PD:{} Z:{} DC:{} C:{}'.format(self.get_bit('STATUS', 'NOT_TO'), self.get_bit('STATUS', 'NOT_PD'), self.z, self.dc, self.c), end='')
        
        print(' W:{:02X} CC:{:d}'.format(self.data['WREG'], self.cycles))
        
    def dump_data(self, addresses):
        self.data.dump(addresses)

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

    def run(self, verbose=False):
        ''' run until pc == 07FF. i.e. GOTO 0x7FF is HALT '''
        start = time.clock()
        while True:
            if verbose:
                self.status()
            self.exec(verbose)

            # Check for HALT address
            if (self.pc == 0x7FF):
                break

        if verbose:
            print('runtime: {:0.2f}ms'.format((time.clock() - start) * 1000))

    def exec(self, verbose=False):
        ''' exec a single instruction '''
 
        ins = self.prog[self.pc]

        # display instruction
        if verbose:
            print('{:04X}  '.format(self.pc), ins)

        self.cycles += 1
        self.pc += 1
        
        self.dispatch(ins)

    def dispatch(self, ins):
        ''' dispatch opcode to handler '''
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
            '1111110': self._moviwk,
            '00000000010': self._moviwm,
            '000000001': self._movlb,
            '1100011': self._movlp,
            '110000': self._movlw,
            '0000001': self._movwf,
            '1111111': self._movwik,
            '00000000011': self._movwim,
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
        }[ins.opcode](ins)
        
    # opcode implementations
    def _addfsr(self, ins):
        k = twos_complement(ins.k, 6)
        if ins.n == 0:
            v = ((self.data['FSR0H'] << 8) | self.data['FSR0L']) + k
            self.data['FSR0H'], self.data['FSR0L'] = divmod(v % 0xFFFF, 0xFF)
        else:
            v = ((self.data['FSR1H'] << 8) | self.data['FSR1L']) + k
            self.data['FSR1H'], self.data['FSR1L'] = divmod(v % 0xFFFF, 0xFF)

    def _addlw(self, ins):
        v = self.data['WREG'] + ins.k
        r = (self.data['WREG'] & 0x0f) + (ins.k & 0xf)
        self.data['WREG'] = v
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _addwf(self, ins):
        f = ins.f
        v = self.load(f) + self.data['WREG']
        r = (self.load(f) & 0x0f) + (self.data['WREG'] & 0x0f)
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _addwfc(self, ins):
        f = ins.f
        v = self.load(f) + self.data['WREG'] + self.c
        r = (self.load(f) & 0x0f) + (self.data['WREG'] & 0x0f) + self.c
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _andlw(self, ins):
        v = self.data['WREG'] & ins.k
        self.data['WREG'] = v
        self.z = v == 0

    def _andwf(self, ins):
        f = ins.f
        v = self.load(f) & self.data['WREG']
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _asrf(self, ins):
        pass

    def _bcf(self, ins):
        f = ins.f
        v = self.load(f) & ~(1 << ins.b)
        self.store(f, v)

    def _bra(self, ins):
        self.pc += twos_complement(ins.k, 9)
        self.cycles += 1

    def _brw(self, ins):
        self.pc += self.data['WREG']
        self.cycles += 1

    def _bsf(self, ins):
        f = ins.f
        v = self.load(f) | (1 << ins.b)
        self.store(f, v)

    def _btfsc(self, ins):
        if not self.load(ins.f) & (1 << ins.b):
            self.pc += 1
            self.cycles += 1

    def _btfss(self, ins):
        if self.load(ins.f) & (1 << ins.b):
            self.pc += 1
            self.cycles += 1

    def _call(self, ins):
        self.push()
        self.pc = (self.data['PCLATH'] & 0b01111000 << 8) | ins.k
        self.cycles += 1

    def _callw(self, ins):
        self.push()
        self.pc = (self.data['PCLATH'] & 0b01111111 << 8) | self.data['WREG']
        self.cycles += 1

    def _clrf(self, ins):
        self.store(ins.f, 0)
        self.z = 1

    def _clrw(self, ins):
        self.data['WREG'] = 0
        self.z = 1

    def _clrwdt(self, ins):
        pass

    def _comf(self, ins):
        f = ins.f
        v = (self.load(f) - 1) & 0xFF
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _decf(self, ins):
        f = ins.f
        v = (~self.load(f)) & 0xFF
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _decfsz(self, ins):
        f = ins.f
        v = (self.load(f) - 1) & 0xFF
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        if not v:
            self.pc += 1
            self.cycles += 1

    def _goto(self, ins):
        self.pc = (self.data['PCLATH'] & 0b01111000 << 8) | ins.k
        self.cycles += 1

    def _incf(self, ins):
        f = ins.f
        v = (self.load(f) + 1) & 0xFF
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _incfsz(self, ins):
        f = ins.f
        v = (self.load(f) + 1) & 0xFF
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        if not v:
            self.pc += 1
            self.cycles += 1

    def _iorlw(self, ins):
        v = self.data['WREG'] | ins.k
        self.data['WREG'] = v
        self.z = v == 0

    def _iorwf(self, ins):
        f = ins.f
        v = self.load(f) | self.data['WREG']
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _lslf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.data['WREG'] = v << 1
        else:
            self.store(f, v << 1)
        self.c = v & 0x80
        self.z = not (v & 0x7F)

    def _lsrf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.data['WREG'] = v >> 1
        else:
            self.store(f, v >> 1)
        self.c = v & 0x01
        self.z = not (v & 0xfe)

    def _movf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _moviwk(self, ins):
        k = twos_complement(ins.k, 6)
        if ins.n == 0:
            a = ((self.data['FSR0H'] << 8) | self.data['FSR0L']) + k
        else:
            a = ((self.data['FSR1H'] << 8) | self.data['FSR1L']) + k
        v = self.load_indirect(a)
        self.data['WREG'] = v
        self.z = v == 0
        pass

    def _moviwm(self, ins):
        m = ins.m
        if ins.n == 0:
            a = ((self.data['FSR0H'] << 8) | self.data['FSR0L'])
        else:
            a = ((self.data['FSR1H'] << 8) | self.data['FSR1L'])
        if m == 0:
            a += 1
        elif m == 1:
            a -= 1
        v = self.load_indirect(a)
        self.data['WREG'] = v
        self.z = v == 0
        if m == 2:
            a += 1
        elif m == 3:
            a -= 1
        if ins.n == 0:
            self.data['FSR0H'], self.data['FSR0L'] = divmod(a % 0xFFFF, 0xFF)
        else:
            self.data['FSR1H'], self.data['FSR1L'] = divmod(a % 0xFFFF, 0xFF)

    def _movlb(self, ins):
        self.data['BSR'] = ins.k

    def _movlp(self, ins):
        self.data['PCLATH'] = ins.k

    def _movlw(self, ins):
        self.data['WREG'] = ins.k

    def _movwf(self, ins):
        f = ins.f
        v = self.data['WREG']
        self.store(f, v)

    def _movwik(self, ins):
        k = twos_complement(ins.k, 6)
        if ins.n == 0:
            a = ((self.data['FSR0H'] << 8) | self.data['FSR0L']) + k
        else:
            a = ((self.data['FSR1H'] << 8) | self.data['FSR1L']) + k
        self.store_indirect(a, self.data['WREG'])

    def _movwim(self, ins):
        m = ins.m
        if ins.n == 0:
            a = ((self.data['FSR0H'] << 8) | self.data['FSR0L'])
        else:
            a = ((self.data['FSR1H'] << 8) | self.data['FSR1L'])
        if m == 0:
            a += 1
        elif m == 1:
            a -= 1
        self.store_indirect(a, self.data['WREG'])
        if m == 2:
            a += 1
        elif m == 3:
            a -= 1
        if ins.n == 0:
            self.data['FSR0H'], self.data['FSR0L'] = divmod(a % 0xFFFF, 0xFF)
        else:
            self.data['FSR1H'], self.data['FSR1L'] = divmod(a % 0xFFFF, 0xFF)

    def _nop(self, ins):
        pass

    def _option(self, ins):
        self.data['OPTION'] = self.data['WREG']

    def _reset(self, ins):
        self.reset(self.reg['NOT_RI'])
        
    def _retfie(self, ins):
        self.pop()
        self.set_bit('INTCON', 'GIE')
        self.cycles += 1

    def _retlw(self, ins):
        self.data['WREG'] = ins.k
        self.pop()
        self.cycles += 1

    def _return(self, ins):
        self.pop()
        self.cycles += 1

    def _rlf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.data['WREG'] = (v << 1) | self.c
        else:
            self.store(f, (v << 1) | self.c)
        self.c = v & 0x80

    def _rrf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.data['WREG'] = (self.c << 7) | (v >> 1)
        else:
            self.store(f, (self.c << 7) | (v >> 1))
        self.c = v & 0x01

    def _sleep(self, ins):
        pass

    def _sublw(self, ins):
        v = (-self.data['WREG']) & 0xFF + ins.k
        r = (-self.data['WREG']) & 0x0F + (ins.k & 0x0F)
        self.data['WREG'] = v
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)
        pass

    def _subwf(self, ins):
        f = ins.f
        v = (-self.data['WREG']) & 0xFF + self.load(f)
        r = (-self.data['WREG']) & 0x0F + (self.load(f) & 0x0F)
        if ins.d == 0:
            self.data['WREG'] = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _subwfb(self, ins):
        pass

    def _swapf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.data['WREG'] = (v << 4) & 0xFF | (v >> 4)
        else:
            self.store((v << 4) & 0xFF | (v >> 4))

    def _tris(self, ins):
        if ins.f == 0b101:
            self.data['TRISA'] = self.data['WREG']
        elif ins.f == 0b110:
            self.data['TRISB'] = self.data['WREG']

    def _xorlw(self, ins):
        v = self.data['WREG'] ^ ins.k
        self.data['WREG'] = v
        self.z = v == 0

    def _xorwf(self, ins):
        f = ins.f
        v = self.load(f) ^ self.data['WREG']
        if ins.d == 0:
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


class Instruction:
    def __init__(self, info, fields):
        self.info = info
        self.fields = fields
        assert len(fields) == 7
    
    def __getattr__(self, name):
        i = InstructionInfo.field_list.index(name)
        return self.fields[i]
    
    def to_bits(self):
        bits = self.info.opcode
        
        # build instruction from fields starting after opcode
        for i, field_name in enumerate(InstructionInfo.field_list[1:]):
            x, y = self.info.field_spans[i + 1]
            value = getattr(self, field_name)
            if value is not None:
                bits += '{:0{}b}'.format(value, y - x)

        return bits
    
    def __str__(self):
        opcode, b, d, f, n, m, k = self.fields

        if f is not None and d is not None:
            sd = 'W' if d == 0 else 'F'
            return '{:10} 0x{:02x}, {}'.format(self.info.mnemonic, f, sd)
        elif f is not None and b is not None:
            return '{:10} 0x{:02x}, {}'.format(self.info.mnemonic, f, b)
        elif f is not None:
            return '{:10} 0x{:02x}'.format(self.info.mnemonic, f)
        elif n is not None and k is not None:
            return '{:10} FSR{}, 0x{:02x}'.format(self.info.mnemonic, n, k)
        elif k is not None:
            x, y = self.info.field_spans[6]
            width = 4 if y - x > 8 else 2
            return '{:10} 0x{:0{}X}'.format(self.info.mnemonic, k, width)
        else:
            return '{:10}'.format(self.info.mnemonic)


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
        ''' return an Instruction consisting of info and tuple (opcode, b, d, f, n, m, k) '''

        # convert program word to a bit string
        bits = '{:014b}'.format(word)

        # the instruction word starts with the instruction opcode.  Use a generator
        # comprehension to find match.  It returns a list so use a comma on the lhs
        # to force an unpack.  An exception is thrown if no or multiple matches
        info, = [item for item in self.ins_list if bits.startswith(item.opcode)]

        # build list of fields
        l = []
        for x, y in info.field_spans:
            if x != y:
                l.append(int(bits[x:y], 2))
            else:
                l.append(None)
      
        return Instruction(info, tuple(l))

    def encode(self, mnemonic, **kwargs):
        info = self.mnemonic_dict[mnemonic.upper()]

        fields = []
        
        # build instruction from fields starting after opcode
        for i, field_name in enumerate(InstructionInfo.field_list):
            x, y = info.field_spans[i]
            if field_name == 'opcode':
                fields.append(info.opcode)
            elif field_name in kwargs:
                fields.append(kwargs[field_name])
            elif field_name != 'opcode' and x != y:
                raise IndexError('{} {}:{} missing'.format(field_name, x, y))
            else:
                fields.append(None)
        
        return Instruction(info, tuple(fields))


def twos_complement(input_value, num_bits):
    '''Calculates a two's complement integer from the given input and num bits'''
    mask = 2**(num_bits - 1)
    return -(input_value & mask) + (input_value & ~mask)


def code1(p, d):
    ''' Simple countdown loop'''
    
    # allow defining variable names in a dict to pass to load program.
    # load_program will substitute the names before calling encode
    data = {
        'x': 0x20,
        'y': 0x21,
    }
    code = [
        d.encode('GOTO', k=0x004),
        d.encode('NOP'),
        d.encode('NOP'),
        d.encode('NOP'),
        d.encode('MOVLW', k=0x50),
        d.encode('MOVWF', f=data['x']),
        d.encode('DECFSZ', d=1, f=data['x']),
        d.encode('BRA', k=-2 & 0x1ff),

        d.encode('CALL', k=0x00A),

        d.encode('GOTO', k=0x7FF),

        d.encode('MOVLW', k=0x45),
        d.encode('MOVWF', f=data['y']),
        d.encode('ANDLW', k=0x00),
        d.encode('RETURN'),
    ]

    p.load_program(0, code)
    p.dump_program(range(len(code)))
    print()
    p.run(verbose=True) 
    p.dump_data(range(0x20, 0x30))
    

def code2(p, d):
    # this should use the decoder
    p.load_from_file('test.hex')

    
def code3(p, d):
    d = p.decoder
    
    code = [
        d.encode('MOVLW', k=0x47),
        d.encode('MOVWF', f=0x20),
        d.encode('SWAPF', f=0x20, d=0),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    p.load_program(0, code)
    p.dump_program(range(len(code)))
    print()
    p.run(verbose=True) 
    p.dump_data(range(0x20, 0x30))


def code4(p, d):
    d = p.decoder
    
    code = [
        d.encode('MOVLW', k=0x10),
        d.encode('SUBLW', k=0x20),
        d.encode('MOVWF', f=0x20),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    p.load_program(0, code)
    p.dump_program(range(len(code)))
    print()
    p.run(verbose=True) 
    p.dump_data(range(0x20, 0x30))
      
if __name__ == '__main__':
    decoder = Decoder(insdata.ENHMID)
    p = Pic(decoder, 'p16f1826.inc')

    code3(p, decoder)
    

