import re
import array
import insdata



class pic:
    def __init__(self, ins_table):
        ''' init class with table of instruction set data '''
        self.progmem = array.array('H')
        self.datamem = array.array('B')
        
        self.init_ins_info(ins_table)

    def init_ins_info(self, ins_table):
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
            m = re.match('([01]+)(x*)(d*)(f*)(n*)(k*)', ins.opcode_mask)
            
            # build a dict of fields and their spand
            ins.opcode = m.group(1)
            ins.field_spans = tuple(m.span(i + 1) for i in range(len(ins.field_list)))

            self.ins_ref[rec[0]] = ins
            
            #print('{:8} {:14}'.format(rec[0]), ins.field_spans)

    def decode(self, word):
        ''' return a tuple of opcode, d, b, f, k '''

        # convert program word to a bit string
        bits = '{:014b}'.format(word)
        
        # lookup matching instruction
        for mnemonic in self.ins_ref:
            ins = self.ins_ref[mnemonic]
            #print(mnemonic, ins.opcode_mask, ins.opcode)
            if bits.startswith(ins.opcode):
                print(mnemonic, ins.opcode, bits)
                break
        
        for name, span in zip(ins.field_list, ins.field_spans):
            x, y = span
            if x != y:
                print(name, x, y, bits[x:y])

      
class instruction_info:
    ''' info on an instruction '''
    
    field_list = ['opcode', 'x', 'd', 'f', 'n', 'k']
    
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.fields = None
        self.desc = None
        self.cycles = None
        self.flags = None
        

p = pic(insdata.enhmid)

p.decode(0b00000001100001)
