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
    def __init__(self, core):
        ''' init class with table of instruction set data '''
        
        self.stack = array.array('H')
        self.cycles = array.array('L')
        self.data = datamem.DataMem(256, core.reg)
        self.clear()

        # program counter high byte
        self.pch = 0

        self.core = core

    def clear(self):
        ''' clear memory '''
        # special function registers
        self.prog = [None for i in range(MAXROM)]
        # cycle counts
        self.cycles = [0 for i in range(MAXROM)]
        # stack
        self.stack = [0 for i in range(MAXSTACK)]

        self.data.clear()

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
        address = self.bsr + f
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
        address = self.bsr + f
        self.data[address] = value

    def store_indirect(self, address, value):
        if address < 0x29B0:
            self.data[address] = value
        
    def set_data(self, address, value):
        ''' handles writing to special locations '''
        if address < datamem.MAXRAM and address & 0x7F == self.core.reg['PCL']:
            self.set_pc((self.pclath << 8) | value)
        else:
            self.data[address] = value
            
    def dump_program(self, address_list):
        ''' dump program memory '''
        for address in address_list:
            print('{:04X}  '.format(address), self.prog[address])

    def dump_profile(self, address_list):
        ''' dump program memory '''
        for address in address_list:
            print('{:04X}   {:20} {:4}'.format(address, str(self.prog[address]), self.cycles[address]))

    def dump_data(self, addresses):
        self.data.dump(addresses)

    def status(self):
        ''' print the current state of the processor registers '''
        print('PC:{:04X} SP:{:02X} BS:{:02X}'.format(self.pc, self.stkptr, self.bsr), end='')
        
        print(' TO:{} PD:{} Z:{} DC:{} C:{}'.format(self.get_bit('STATUS', 'NOT_TO'), self.get_bit('STATUS', 'NOT_PD'), self.z, self.dc, self.c), end='')

        print(' W:{:02X} CC:{:d}'.format(self.wreg, self.total_cycles()))

    def inc_cycles(self, cycles):
        self.cycles[self.ins_pc] += cycles

    def total_cycles(self):
        total = 0
        for c in self.cycles:
            total += c
        return total

    @property
    def pc(self):
        ''' get the value of the program counter '''
        return (self.pch << 8) | self.pcl
    
    @pc.setter
    def pc(self, address):
        self.pch, self.pcl = divmod(address, 0X100)

    @property
    def pcl(self):
        return self.data['PCL']
        
    @pcl.setter
    def pcl(self, value):
        self.data['PCL'] = value

    @property
    def pclath(self):
        return self.data['PCLATH']
        
    @pclath.setter
    def pclath(self, value):
        self.data['PCLATH'] = value

    @property
    def wreg(self):
        return self.data['WREG']
        
    @wreg.setter
    def wreg(self, value):
        self.data['WREG'] = value

    @property
    def bsr(self):
        return self.data['BSR']
        
    @bsr.setter
    def bsr(self, value):
        self.data['BSR'] = value

    @property
    def fsr0(self):
        return (self.data['FSR0H'] << 8) | self.data['FSR0L']
        
    @fsr0.setter
    def fsr0(self, value):
        self.data['FSR0H'], self.data['FSR0L'] = divmod(value % 0x10000, 0x100)

    @property
    def fsr1(self):
        return (self.data['FSR1H'] << 8) | self.data['FSR1L']
        
    @fsr1.setter
    def fsr1(self, value):
        self.data['FSR1H'], self.data['FSR1L'] = divmod(value % 0x10000, 0x100)

    @property
    def stkptr(self):
        return self.data['STKPTR']
    
    @stkptr.setter
    def stkptr(self, value):
        self.data['STKPTR'] = value

    @property
    def z(self):
        ''' get STATUS register zero bit as 0 or 1 '''
        return self.get_bit('STATUS', 'Z')

    @z.setter
    def z(self, value):
        if value:
            self.set_bit('STATUS', 'Z')
        else:
            self.clear_bit('STATUS', 'Z')

    @property
    def c(self):
        ''' get STATUS register carry bit as 0 or 1 '''
        return self.get_bit('STATUS', 'C')

    @c.setter
    def c(self, value):
        if value:
            self.set_bit('STATUS', 'C')
        else:
            self.clear_bit('STATUS', 'C')

    @property
    def dc(self):
        ''' get STATUS register digit carry bit as 0 or 1 '''
        return self.get_bit('STATUS', 'DC')
    
    @dc.setter
    def dc(self, value):
        if value:
            self.set_bit('STATUS', 'DC')
        else:
            self.clear_bit('STATUS', 'DC')
            
    def get_bit(self, register, bit_number):
        ''' get a bit in register specified by number or name '''
        if isinstance(bit_number, str):
            bit_number = self.core.reg[bit_number]
        return 1 if self.data[register] & (1 << bit_number) else 0
        
    def set_bit(self, register, bit_number, state=1):
        ''' set a bit in a register specified by number or name '''
        if isinstance(bit_number, str):
            bit_number = self.core.reg[bit_number]
        if state:
            self.data[register] |= (1 << bit_number)
        else:
            self.data[register] &= ~(1 << bit_number)
            
    def clear_bit(self, register, bit_number):
        ''' clear a bit in a register specified by number or name '''
        if isinstance(bit_number, str):
            bit_number = self.core.reg[bit_number]
        self.data[register] &= ~(1 << bit_number)

    def push(self):
        ''' push pc onto stack '''
        # get sp
        sp = self.stkptr

        # Set overflow bit
        if sp == 0x0F:
            self.set_bit('PCON', 'STKOVR')

        # STVREN is not implemented so stack wraps and no reset occurs
        sp = (sp + 1) & 0x0F

        # save return address and update STKPTR
        self.stack[sp] = self.pc
        self.stkptr = sp

    def pop(self):
        ''' pop value on stack into pc '''
        # get sp
        sp = self.stkptr

        # set underflow bit
        if sp == 0:
            self.set_bit('PCON', 'STKUNF')

        # restore return address and update STKPTR
        self.pc = self.stack[sp]

        # STVREN is not implemented so stack wraps and no reset occurs
        self.stkptr = (sp - 1) & 0x0F

    def preset(self):
        self.data.clear()
#        if cond is None or cond == self.reg['NOT_POR']:
#            self.data['PCON'] = 0
#            self.set_bit('PCON', 'NOT_POR')
#            self.set_bit('PCON', 'NOT_BOR')
#            self.data['STATUS'] = (1 << self.reg['NOT_PD']) | (1 << self.reg['NOT_TO'])
#        elif cond == self.reg['NOT_RI']:
#            self.data['PCON'] = (1 << self.reg['NOT_POR']) | (1 << self.reg['NOT_BOR'])
#            self.data['STATUS'] = (1 << self.reg['NOT_PD']) | (1 << self.reg['NOT_TO'])

        self.stkptr = 0x1F

    def run(self, verbose=False):
        ''' run until pc == 07FF. i.e. GOTO 0x7FF is HALT '''
        start = time.clock()
        while self.pc < 0x7FF:
            if verbose:
                self.status()
            self.exec(verbose)

        self.status()

        if verbose:
            print('runtime: {:0.2f}ms'.format((time.clock() - start) * 1000))

    def exec(self, verbose=False):
        ''' exec a single instruction '''
 
        ins = self.prog[self.pc]

        # display instruction
        if verbose:
            print('{:04X}  '.format(self.pc), ins)

        self.ins_pc, self.pc = self.pc, self.pc + 1
        cycles = ins.info.cycles.split(',')[0]
        self.inc_cycles(int(cycles))

        self.dispatch(ins)

    def dispatch(self, ins):
        ''' dispatch opcode to handler '''
        return {
            'ADDFSR': self._addfsr,
            'ADDLW': self._addlw,
            'ADDWF': self._addwf,
            'ADDWFC': self._addwfc,
            'ANDLW': self._andlw,
            'ANDWF': self._andwf,
            'ASRF': self._asrf,
            'BCF': self._bcf,
            'BRA': self._bra,
            'BRW': self._brw,
            'BSF': self._bsf,
            'BTFSC': self._btfsc,
            'BTFSS': self._btfss,
            'CALL': self._call,
            'CALLW': self._callw,
            'CLRF': self._clrf,
            'CLRW': self._clrw,
            'CLRWDT': self._clrwdt,
            'COMF': self._comf,
            'DECF': self._decf,
            'DECFSZ': self._decfsz,
            'GOTO': self._goto,
            'INCF': self._incf,
            'INCFSZ': self._incfsz,
            'IORLW': self._iorlw,
            'IORWF': self._iorwf,
            'LSLF': self._lslf,
            'LSRF': self._lsrf,
            'MOVF': self._movf,
            'MOVIWK': self._moviwk,
            'MOVIWM': self._moviwm,
            'MOVLB': self._movlb,
            'MOVLP': self._movlp,
            'MOVLW': self._movlw,
            'MOVWF': self._movwf,
            'MOVWIK': self._movwik,
            'MOVWIM': self._movwim,
            'NOP': self._nop,
            'OPTION': self._option,
            'RESET': self._reset,
            'RETFIE': self._retfie,
            'RETLW': self._retlw,
            'RETURN': self._return,
            'RLF': self._rlf,
            'RRF': self._rrf,
            'SLEEP': self._sleep,
            'SUBLW': self._sublw,
            'SUBWF': self._subwf,
            'SUBWFB': self._subwfb,
            'SWAPF': self._swapf,
            'TRIS': self._tris,
            'XORLW': self._xorlw,
            'XORWF': self._xorwf,
        }[ins.info.mnemonic](ins)
        
    # opcode implementations
    def _addfsr(self, ins):
        k = twos_complement(ins.k, 6)
        if ins.n == 0:
            self.fsr0 += k
        else:
            self.fsr1 += k

    def _addlw(self, ins):
        v = self.wreg + ins.k
        r = (self.wreg & 0x0f) + (ins.k & 0xf)
        self.wreg = v
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _addwf(self, ins):
        f = ins.f
        v = self.load(f) + self.wreg
        r = (self.load(f) & 0x0f) + (self.wreg & 0x0f)
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _addwfc(self, ins):
        f = ins.f
        v = self.load(f) + self.wreg + self.c
        r = (self.load(f) & 0x0f) + (self.wreg & 0x0f) + self.c
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _andlw(self, ins):
        v = self.wreg & ins.k
        self.wreg = v
        self.z = v == 0

    def _andwf(self, ins):
        f = ins.f
        v = self.load(f) & self.wreg
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _asrf(self, ins):
        f = ins.f
        v = self.load(f)
        self.c = v & 0x01
        v = (v >> 1) | (v & 0x80)
        self.z = v == 0
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        
    def _bcf(self, ins):
        f = ins.f
        v = self.load(f) & ~(1 << ins.b)
        self.store(f, v)

    def _bra(self, ins):
        self.pc += twos_complement(ins.k, 9)

    def _brw(self, ins):
        self.pc += self.wreg

    def _bsf(self, ins):
        f = ins.f
        v = self.load(f) | (1 << ins.b)
        self.store(f, v)

    def _btfsc(self, ins):
        if not self.load(ins.f) & (1 << ins.b):
            self.pc += 1
            self.inc_cycles(1)

    def _btfss(self, ins):
        if self.load(ins.f) & (1 << ins.b):
            self.pc += 1
            self.inc_cycles(1)

    def _call(self, ins):
        self.push()
        self.pc = (self.pclath & 0b01111000 << 8) | ins.k

    def _callw(self, ins):
        self.push()
        self.pc = (self.pclath & 0b01111111 << 8) | self.wreg

    def _clrf(self, ins):
        self.store(ins.f, 0)
        self.z = 1

    def _clrw(self, ins):
        self.wreg = 0
        self.z = 1

    def _clrwdt(self, ins):
        pass

    def _comf(self, ins):
        f = ins.f
        v = (self.load(f) - 1) & 0xFF
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _decf(self, ins):
        f = ins.f
        v = (~self.load(f)) & 0xFF
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _decfsz(self, ins):
        f = ins.f
        v = (self.load(f) - 1) & 0xFF
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        if not v:
            self.pc += 1
            self.inc_cycles(1)

    def _goto(self, ins):
        self.pc = (self.pclath & 0b01111000 << 8) | ins.k

    def _incf(self, ins):
        f = ins.f
        v = (self.load(f) + 1) & 0xFF
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _incfsz(self, ins):
        f = ins.f
        v = (self.load(f) + 1) & 0xFF
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        if not v:
            self.pc += 1
            self.inc_cycles(1)

    def _iorlw(self, ins):
        v = self.wreg | ins.k
        self.wreg = v
        self.z = v == 0

    def _iorwf(self, ins):
        f = ins.f
        v = self.load(f) | self.wreg
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _lslf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.wreg = v << 1
        else:
            self.store(f, v << 1)
        self.c = v & 0x80
        self.z = not (v & 0x7F)

    def _lsrf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.wreg = v >> 1
        else:
            self.store(f, v >> 1)
        self.c = v & 0x01
        self.z = not (v & 0xfe)

    def _movf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0

    def _moviwk(self, ins):
        k = twos_complement(ins.k, 6)
        a = (self.fsr0 if ins.n == 0 else self.fsr1) + k
        v = self.load_indirect(a)
        self.wreg = v
        self.z = v == 0
        pass

    def _moviwm(self, ins):
        m = ins.m
        a = self.fsr0 if ins.n == 0 else self.fsr1
        if m == 0:
            a += 1
        elif m == 1:
            a -= 1
        v = self.load_indirect(a)
        self.wreg = v
        self.z = v == 0
        if m == 2:
            a += 1
        elif m == 3:
            a -= 1
        if ins.n == 0:
            self.fsr0 = a
        else:
            self.fsr1 = a

    def _movlb(self, ins):
        self.bsr = ins.k

    def _movlp(self, ins):
        self.pclath = ins.k

    def _movlw(self, ins):
        self.wreg = ins.k

    def _movwf(self, ins):
        f = ins.f
        v = self.wreg
        self.store(f, v)

    def _movwik(self, ins):
        k = twos_complement(ins.k, 6)
        a = (self.fsr0 if ins.n == 0 else self.fsr1) + k
        self.store_indirect(a, self.wreg)

    def _movwim(self, ins):
        m = ins.m
        a = self.fsr0 if ins.n == 0 else self.fsr1
        if m == 0:
            a += 1
        elif m == 1:
            a -= 1
        self.store_indirect(a, self.wreg)
        if m == 2:
            a += 1
        elif m == 3:
            a -= 1
        if ins.n == 0:
            self.fsr0 = a
        else:
            self.fsr1 = a

    def _nop(self, ins):
        pass

    def _option(self, ins):
        self.data['OPTION'] = self.wreg

    def _reset(self, ins):
        self.reset()
        
    def _retfie(self, ins):
        self.pop()
        self.set_bit('INTCON', 'GIE')

    def _retlw(self, ins):
        self.wreg = ins.k
        self.pop()

    def _return(self, ins):
        self.pop()

    def _rlf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.wreg = (v << 1) | self.c
        else:
            self.store(f, (v << 1) | self.c)
        self.c = v & 0x80

    def _rrf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.wreg = (self.c << 7) | (v >> 1)
        else:
            self.store(f, (self.c << 7) | (v >> 1))
        self.c = v & 0x01

    def _sleep(self, ins):
        pass

    def _sublw(self, ins):
        v = ((-self.wreg) & 0xFF) + ins.k
        r = ((-self.wreg) & 0x0F) + (ins.k & 0x0F)
        self.wreg = v
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)
        pass

    def _subwf(self, ins):
        f = ins.f
        v = ((-self.wreg) & 0xFF) + self.load(f)
        r = ((-self.wreg) & 0x0F) + (self.load(f) & 0x0F)
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _subwfb(self, ins):
        f = ins.f
        v = self.load(f) + ((-self.wreg) & 0xFF) - (1 - self.c)
        r = (self.load(f) & 0x0F) + ((-self.wreg) & 0x0F) + (1 - self.c)
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.c = v & 0x100
        self.dc = r & 0x10
        self.z = not (v & 0xff)

    def _swapf(self, ins):
        f = ins.f
        v = self.load(f)
        if ins.d == 0:
            self.wreg = (v << 4) & 0xFF | (v >> 4)
        else:
            self.store((v << 4) & 0xFF | (v >> 4))

    def _tris(self, ins):
        if ins.f == 0b101:
            self.data['TRISA'] = self.wreg
        elif ins.f == 0b110:
            self.data['TRISB'] = self.wreg

    def _xorlw(self, ins):
        v = self.wreg ^ ins.k
        self.wreg = v
        self.z = v == 0

    def _xorwf(self, ins):
        f = ins.f
        v = self.load(f) ^ self.wreg
        if ins.d == 0:
            self.wreg = v
        else:
            self.store(f, v)
        self.z = v == 0
  

class InstructionInfo:
    ''' info on an instruction '''

    field_list = ['opcode', 'b', 'd', 'f', 'n', 'm', 'k']

    def __init__(self, rec):
        self.mnemonic, arg, self.desc, self.cycles, self.opcode_mask, self.flags, self.notes = rec

        # get opcode mask and remove any whitespace
        # break opcode mask into bit spans for each field for decoding later
        m = re.match('([01]+)x*(b*)(d*)(f*)(n*)(m*)(k*)', self.opcode_mask.replace(' ', ''))

        # build a tuple of fields and their spans
        self.opcode = m.group(1)
        self.field_spans = tuple(m.span(i + 1) for i in range(len(self.field_list)))

        # make a tuple for convenience
        self.arg = tuple(arg.split(','))
        
    def __str__(self):
        s = self.opcode
        for field, span in zip(self.field_list, self.field_spans):
            if span[0] != span[1]:
                s += ', {}={}'.format(field, span)
            
        return s


class Instruction:
    ''' instruction instance '''
    def __init__(self, info, fields):
        self.info = info
        self.fields = fields
    
    def __getattr__(self, name):
        if name == 'opcode':
            return self.info.opcode
        elif name in self.fields:
            return self.fields[name]
        else:
            return None
    
    def to_bits(self):
        ''' convert instruction into 14 bit string '''
        bits = self.info.opcode
        
        # build instruction from fields starting after opcode
        for i, field_name in enumerate(InstructionInfo.field_list[1:], 1):
            x, y = self.info.field_spans[i]
            value = getattr(self, field_name)
            if value is not None:
                bits += '{:0{}b}'.format(value, y - x)

        return bits
    
    def __str__(self):
        if self.f is not None and self.d is not None:
            sd = 'W' if self.d == 0 else 'F'
            return '{:10} 0x{:02x}, {}'.format(self.info.mnemonic, self.f, sd)
        elif self.f is not None and self.b is not None:
            return '{:10} 0x{:02x}, {}'.format(self.info.mnemonic, self.f, self.b)
        elif self.f is not None:
            return '{:10} 0x{:02x}'.format(self.info.mnemonic, self.f)
        elif self.n is not None and self.k is not None:
            return '{:10} FSR{}, 0x{:02x}'.format(self.info.mnemonic, self.n, self.k)
        elif self.k is not None:
            x, y = self.info.field_spans[6]
            width = 4 if y - x > 8 else 2
            return '{:10} 0x{:0{}X}'.format(self.info.mnemonic, self.k, width)
        else:
            return '{:10}'.format(self.info.mnemonic)


class Decoder:
    ''' Decodes and encodes instructions from/to 14 bit program words'''
        
    def __init__(self, ins_data, inc_file):
        ''' parse instruction table and build lookup tables '''
        self.info_list = []
        self.mnemonic_dict = {}

        for rec in ins_data:
            info = InstructionInfo(rec)
            self.info_list.append(info)
            self.mnemonic_dict[info.mnemonic] = info

        # load include file with reg definitions
        self.load_inc_file(inc_file)

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

    def decode(self, word):
        ''' return an Instruction consisting of info and dict of fields (b, d, f, n, m, k) '''

        # convert program word to a bit string
        bits = '{:014b}'.format(word)

        # the instruction word starts with the instruction opcode.  Use a generator
        # comprehension to find match.  It returns a list so use a comma on the lhs
        # to force an unpack.  An exception is thrown if no or multiple matches
        info, = [item for item in self.info_list if bits.startswith(item.opcode)]

        # build list of fields
        fields = {}
        for name, span in zip(info.field_list, info.field_spans):
            x, y = span
            if x != y:
                fields[name] = int(bits[x:y], 2)
      
        return Instruction(info, fields)

    def encode(self, mnemonic, **kwargs):
        info = self.mnemonic_dict[mnemonic.upper()]

        fields = {}
        
        # build instruction from fields starting after opcode
        for i, field_name in enumerate(InstructionInfo.field_list):
            x, y = info.field_spans[i]
            if field_name == 'opcode':
                pass
            elif field_name in kwargs:
                fields[field_name] = kwargs[field_name]
            elif x != y:
                raise IndexError('{} {}:{} missing'.format(field_name, x, y))
        
        return Instruction(info, fields)

    def assemble(self, source):
        '''
        Mini assembler.  Takes source code string
        
        [symbol]  [instruction [arg, arg, ...]]
        
        symbol if present must start in column 1. arg values may be symbols or predefined
        register or bit names (STATUS, BSR, GIE, etc) or destination flags (F or W).  Case
        is ignored.  Numeric values assume decimal radix.
        
        macro instructions:
        ORG - defines value of pc: org 0x004
        EQU - defines a symbolic constant: x equ 0x20
        
        symbol when not part of an EQU macro defines symbolic constant for current pc.  May
        preface machine instruction, ORG macro or by itself
        '''
    
        code = []
        symtab = {}
        pc = 0
        
        for line in source.splitlines():
            m = re.search("(?i)(^\S+)?(\s+\S+)?(\s+.+)?", line)
            if m:
                # unpak parsed groups
                sym, op, args = m.groups()

                # kludge because regex isn't quite right
                #if not op and args:
                #    op, args = args, None

                op = op.upper().strip() if op else ''
                sym = sym.upper().strip() if sym else ''
                
                # convert args into a list of values looking up symbols if needed
                values = []
                if args:
                    for arg in args.upper().split(','):
                        # handle arg by first treating as numeric
                        arg = arg.strip().upper()
                        try:
                            if arg.startswith('0X'):
                                values.append(int(arg, 16))
                            else:
                                values.append(to2comp(int(arg), 8))
                        except ValueError:
                            if arg in self.reg:
                                values.append(self.reg[arg])
                            elif arg in symtab:
                                values.append(symtab[arg])
                            else:
                                values.append(0)

                if op == 'ORG':
                    pc = values[0]
                    if sym:
                        symtab[sym] = pc
                elif op == 'EQU':
                    symtab[sym] = values[0]
                else:
                    # assign symbols to current pc
                    if sym:
                        symtab[sym] = pc
                    if op:
                        # get info about the instruction
                        info = self.mnemonic_dict[op]

                        # handle special case of BRA instruction relative address
                        if op == 'BRA':
                            values[0] = (values[0] - (pc + 1)) & 0x1FF
                            
                        ins = Instruction(info, dict(zip(info.arg, values)))
                        # add instruction to code list
                        if len(code) > pc:
                            code[pc] = ins
                        else:
                            code.extend([None] * (pc - len(code)))
                            code.append(ins)
                        
                        pc += 1

        print(symtab)
        return code, symtab


def to2comp(input_value, num_bits):
    if input_value < 0:
        return 2**num_bits + input_value
    else:
        return input_value


def twos_complement(input_value, num_bits):
    '''Calculates a two's complement integer from the given input and num bits'''
    mask = 2**(num_bits - 1)
    return -(input_value & mask) + (input_value & ~mask)


def code3(p, d):
    source = '''
x       equ 0x20
reset   org 0x0000
loop    org 0x0004
        movlw 0x23
        movwf x
        addwf x,w
        goto loop
test    org 0x0010
        movlw 0x33
        bra reset
    '''
    
    code, _ = decoder.assemble(source)
    p.load_program(0, code)
    p.dump_program(range(len(code)))


def code4(p, d):
    source = '''
x       equ 0x20
y       equ 0x21
c       equ 0x22
reset   org 0x0000
        movlw 0x23
        movwf x
        movlw 0x00
        movwf y
        
        movlw 0x22
        subwf x, f
        movlw 0x00
        subwfb y, f
        
        goto 0x7ff
    '''
    
    code, data = decoder.assemble(source)
    p.load_program(0, code)
    p.dump_program(range(len(code)))
    
    p.run(verbose=True)
    
    # determine data range to display
    x = min(data.values()) & 0xFFF8
    y = max(data.values())
    p.dump_data(range(x, y + 1))


def code5(p, d):
    source = '''
x       equ 0x20
y       equ 0x21
c       equ 0x22
reset   org 0x0000
        movlw 0x23
        movwf x
        movlw 0x00
        movwf y
        
        movlw 0x23
        subwf x, f
        movlw 0x00
        subwfb y, f
        
        goto 0x7ff
    '''
    
    code, data = decoder.assemble(source)
    p.load_program(0, code)
    p.dump_program(range(len(code)))
    
    p.run(verbose=True)
    
    # determine data range to display
    x = min(data.values()) & 0xFFF8
    y = max(data.values())
    p.dump_data(range(x, y + 1))


def code6(p, d):
    source = '''
x       equ 0x20
y       equ 0x21
c       equ 0x22
reset   org 0x0000
        movlw 0x23
        movwf x
        movlw 0x00
        movwf y
        
        movlw 0x24
        subwf x, f
        movlw 0x00
        subwfb y, f
        
        goto 0x7ff
    '''
    
    code, data = decoder.assemble(source)
    p.load_program(0, code)
    p.dump_program(range(len(code)))
    
    p.run(verbose=True)
    
    # determine data range to display
    x = min(data.values()) & 0xFFF8
    y = max(data.values())
    p.dump_data(range(x, y + 1))


def test(p, d):
    # this should use the decoder
    p.load_from_file('test.hex')


def test10(p, d):
    ''' nested stable timing loop '''
    
    source = '''
x    equ    0x20
y    equ    0x21

     movlw  0x02
     movwf  x

     movlw  0x00
     movwf  y
loop   
     movlw  -1
     
     addwf  x, f
     btfsc  STATUS, C
     clrw   x
     
     addwf  y, f
     btfsc  STATUS, C
     clrw   y
     
     iorwf	x, w
     iorwf	y, w
     btfss	STATUS, Z
     goto   loop
     
     goto   0x7ff
     '''
     
    code, data = d.assemble(source)
    run(p, code, data)


if __name__ == '__main__':
    decoder = Decoder(insdata.ENHMID, 'p16f1826.inc')
    p = Pic(decoder)

    import test
    test.test9(p, decoder)
