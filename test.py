'''
test cases
'''

import pic
import insdata


def run(p, code, data, verbose=False):
    p.clear()
    p.load_program(0, code)
    p.dump_program(range(len(code)))
    p.run(verbose)
    
    # determine data range to display
    x = min(data.values()) & 0xFFF8
    y = max(data.values())
    p.dump_data(range(x, y + 1))
    
    p.dump_profile(range(len(code)))
    
    
def test1(p, d):
    ''' Simple countdown loop'''

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

    run(p, code, data)

    
def test2(p, d):
    data = {
        'x': 0x20,
        'y': 0x21,
    }
    code = [
        d.encode('MOVLW', k=0x47),
        d.encode('MOVWF', f=0x20),
        d.encode('SWAPF', f=0x20, d=0),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    run(p, code, data)


def test3(p, d):
    data = {
        'x': 0x20,
        'y': 0x21,
    }
    code = [
        d.encode('MOVLW', k=0x10),
        d.encode('IORWF', f=data['x'], d=1),
        d.encode('BSF', f=data['x'], b=2),
        d.encode('BRA', k=1),
        d.encode('BSF', f=data['x'], b=7),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    run(p, code, data)


def test4(p, d):
    data = {
        'x': 0x20,
        'y': 0x21,
    }
    code = [
        d.encode('MOVLW', k=0x10),
        d.encode('SUBLW', k=0x20),
        d.encode('MOVWF', f=0x20),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    run(p, code, data)
    
    
def test5(p, d):
    ''' old style subtraction '''
    data = {
        'msb_a': 0x20,
        'lsb_a': 0x21,
        'msb_b': 0x22,
        'lsb_b': 0x23,
    }
    code = [
        d.encode('MOVLW', k=0x03),
        d.encode('MOVWF', f=data['msb_b']),
        d.encode('MOVLW', k=0x11),
        d.encode('MOVWF', f=data['lsb_b']),
        d.encode('MOVLW', k=0x02),
        d.encode('MOVWF', f=data['msb_a']),
        d.encode('MOVLW', k=0x99),
        d.encode('MOVWF', f=data['lsb_a']),
        
        d.encode('MOVF', f=data['lsb_a'], d=0),
        d.encode('SUBWF', f=data['lsb_b'], d=1),
        d.encode('MOVF', f=data['msb_a'], d=0),
        d.encode('BTFSS', f=d.reg['STATUS'], b=d.reg['C']),
        d.encode('ADDLW', k=0x01),
        d.encode('SUBWF', f=data['msb_b'], d=1),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    run(p, code, data, verbose=True)
    
    
def test6(p, d):
    ''' 16bit subtraction using enhanced midrange instructions '''
    data = {
        'msb_a': 0x20,
        'lsb_a': 0x21,
        'msb_b': 0x22,
        'lsb_b': 0x23,
    }
    code = [
        d.encode('MOVLW', k=0x03),
        d.encode('MOVWF', f=data['msb_b']),
        d.encode('MOVLW', k=0x11),
        d.encode('MOVWF', f=data['lsb_b']),
        d.encode('MOVLW', k=0x02),
        d.encode('MOVWF', f=data['msb_a']),
        d.encode('MOVLW', k=0x99),
        d.encode('MOVWF', f=data['lsb_a']),
        
        d.encode('MOVF', f=data['lsb_a'], d=0),
        d.encode('SUBWF', f=data['lsb_b'], d=1),
        d.encode('MOVF', f=data['msb_a'], d=0),
        d.encode('SUBWFB', f=data['msb_b'], d=1),
        
        d.encode('GOTO', k=0x7FF),
    ]
    
    run(p, code, data, verbose=True)


def test7(p, d):
    ''' arithmatic shift tests '''
    data = {
        'x': 0x20,
        'y': 0x21,
    }
    code = [
        d.encode('MOVLW', k=0x01),
        d.encode('MOVWF', f=data['x']),
        d.encode('MOVLW', k=0x80),
        d.encode('MOVWF', f=data['y']),
        d.encode('ASRF', f=data['x'], d=1),
        d.encode('ASRF', f=data['y'], d=1),

        d.encode('GOTO', k=0x7FF),
    ]
    
    run(p, code, data)
    

def test8(p, d):
    ''' arithmatic shift tests '''
    source = '''
x    equ   0x20
y    equ   0x21

     movlw 0x01
     movwf x
     movlw 0x80
     movwf y
     asrf  x, f
     asrf  y, f
     
     goto  0x7ff
     '''
     
    code, data = d.assemble(source)
    run(p, code, data)


def test9(p, d):
    ''' nested loop test '''
    
    source = '''
x    equ    0x20
y    equ    0x21

     movlw  10
     movwf  x

l1   movlw  5
     movwf  y
l2   decfsz y, f
     goto   l2
     
     decfsz x, f
     bra    l1
     
     goto   0x7ff
     '''
     
    code, data = d.assemble(source)
    run(p, code, data)


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


def test20(p, d):
    ''' test FSR instructions and indirect registers '''
    pass

   
def test(p, d):
    # this should use the decoder
    p.load_from_file('test.hex')


if __name__ == '__main__':
    d = pic.Decoder(insdata.ENHMID, 'p16f1826.inc')
    p = pic.Pic(d)

    '''   
    test1(p, d)
    test2(p, d)
    test3(p, d)
    test4(p, d)
    test5(p, d)
    test6(p, d)
    test7(p, d)
    test8(p, d)
    '''
    test5(p, d)
    test6(p, d)
