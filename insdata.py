
'''
This is the instruction data grabbed from the Instruction Set Summary table
in the Pic data sheet for an enhanced midrange (14bit) processor such as the
16f1826 or 12f1822.  This is used to initialize the decoder.

fields:
    mnemonic
    arguments
    description
    cycles
    opcode format
    status bits affected :
    notes
'''

ENHMID = [
    ('NOP', '-', 'No Operation', '1', '00 0000 0000 0000', '', ''),
    ('RESET', '-', 'Software device Reset', '1', '00 0000 0000 0001', '', ''),
    ('RETURN', '-', 'Return from Subroutine', '2', '00 0000 0000 1000', '', ''),
    ('RETFIE', '-', 'Return from interrupt', '2', '00 0000 0000 1001', '', ''),
    ('CALLW', '-', 'Call Subroutine with W', '2', '00 0000 0000 1010', '', ''),
    ('BRW', '-', 'Relative Branch with W', '2', '00 0000 0000 1011', '', ''),
    ('MOVLB', 'k', 'Move literal to BSR', '1', '00 0000 001k kkkk', '', ''),
    ('OPTION', '-', 'Load OPTION_REG register with W', '1', '00 0000 0110 0010', '', ''),
    ('SLEEP', '-', 'Go into Standby mode', '1', '00 0000 0110 0011', 'TO,PD', ''),
    ('CLRWDT', '-', 'Clear Watchdog Timer', '1', '00 0000 0110 0100', 'TO,PD', ''),
    ('TRIS', 'f', 'Load TRIS register with W', '1', '00 0000 0110 0fff', '', ''),
    ('MOVWF', 'f', 'Move W to f', '1', '00 0000 1fff ffff', '', '2'),
    ('CLRW', '-', 'Clear W', '1', '00 0001 0000 00xx', 'Z', '2'),
    ('CLRF', 'f', 'Clear f', '1', '00 0001 1fff ffff', 'Z', ''),
    ('SUBWF', 'f,d', 'Subtract W from f', '1', '00 0010 dfff ffff', 'C,DC,Z', '2'),
    ('DECF', 'f,d', 'Decrement f', '1', '00 0011 dfff ffff', 'Z', '2'),
    ('IORWF', 'f,d', 'Inclusive OR W with f', '1', '00 0100 dfff ffff', 'Z', '2'),
    ('ANDWF', 'f,d', 'AND W with f', '1', '00 0101 dfff ffff', 'Z', '2'),
    ('XORWF', 'f,d', 'Exclusive OR W with f', '1', '00 0110 dfff ffff', 'Z', '2'),
    ('ADDWF', 'f,d', 'Add W and f', '1', '00 0111 dfff ffff', 'C,DC,Z', '2'),
    ('MOVF', 'f,d', 'Move f', '1', '00 1000 dfff ffff', 'Z', '2'),
    ('COMF', 'f,d', 'Complement f', '1', '00 1001 dfff ffff', 'Z', '2'),
    ('INCF', 'f,d', 'Increment f', '1', '00 1010 dfff ffff', 'Z', '2'),
    ('DECFSZ', 'f,d', 'Decrementf,Skip if 0', '1,2', '00 1011 dfff ffff', '', '1,2'),
    ('RRF', 'f,d', 'Rotate Right f through Carry', '1', '00 1100 dfff ffff', 'C', '2'),
    ('RLF', 'f,d', 'Rotate Left f through Carry', '1', '00 1101 dfff ffff', 'C', '2'),
    ('SWAPF', 'f,d', 'Swap nibbles in f', '1', '00 1110 dfff ffff', '', '2'),
    ('INCFSZ', 'f,d', 'Incrementf, Skip if 0', '1,2', '00 1111 dfff ffff', '', '1,2'),
    ('BCF', 'f,b', 'Bit Clear f', '1', '01 00bb bfff ffff', '', '2'),
    ('BSF', 'f,b', 'Bit Set f', '1', '01 01bb bfff ffff', '', '2'),
    ('BTFSC', 'f,b', 'Bit Test f, Skip if Clear', '1,2', '01 10bb bfff ffff', '', '1,2'),
    ('BTFSS', 'f,b', 'Bit Test f, Skip if Set', '1,2', '01 11bb bfff ffff', '', '1,2'),
    ('CALL', 'k', 'Call Subroutine', '2', '10 0kkk kkkk kkkk', '', ''),
    ('GOTO', 'k', 'Goto address', '2', '10 1kkk kkkk kkkk', '', ''),
    ('MOVLW', 'k', 'Move literal to W', '1', '11 0000 kkkk kkkk', '', ''),
    ('ADDFSR', 'n,k', 'Add Literal k to FSRn', '1', '11 0001 0nkk kkkk', '', ''),
    ('MOVLP', 'k', 'Move literal to PCLATH', '1', '11 0001 1kkk kkkk', '', ''),
    ('BRA', 'k', 'Relative Branch', '2', '11 001k kkkk kkkk', '', ''),
    ('RETLW', 'k', 'Return with literal in W', '2', '11 0100 kkkk kkkk', '', ''),
    ('LSLF', 'f,d', 'Logical Left Shift', '1', '11 0101 dfff ffff', 'C,Z', '2'),
    ('LSRF', 'f,d', 'Logical Right Shift', '1', '11 0110 dfff ffff', 'C,Z', '2'),
    ('ASRF', 'f,d', 'Arithmetic Right Shift', '1', '11 0111 dfff ffff', 'C,Z', '2'),
    ('IORLW', 'k', 'Inclusive OR literal with W', '1', '11 1000 kkkk kkkk', 'Z', ''),
    ('ANDLW', 'k', 'AND literal with W', '1', '11 1001 kkkk kkkk', 'Z', ''),
    ('XORLW', 'k', 'Exclusive OR literal with W', '1', '11 1010 kkkk kkkk', 'Z', ''),
    ('SUBWFB', 'f,d', 'Subtract with Borrow W from f', '1', '11 1011 dfff ffff', 'C,DC,Z', '2'),
    ('SUBLW', 'k', 'Subtract W from literal', '1', '11 1100 kkkk kkkk', 'C,DC,Z', ''),
    ('ADDWFC', 'f,d', 'Add with Carry W and f', '1', '11 1101 dfff ffff', 'C,DC,Z', '2'),
    ('ADDLW', 'k', 'Add literal and W', '1', '11 1110 kkkk kkkk', 'C,DC,Z', ''),
    ('MOVIW', 'n mm', 'Move Indirect FSRn to W with pre/post inc/dec', '1', '00 0000 0001 0nmm', 'Z', '2,3'),
    ('MOVIW', 'k[n]', 'Move INDFn to W, Indexed Indirect', '1', '11 1111 0nkk kkkk', 'Z', '2,3'),
    ('MOVWI', 'n mm', 'Move W to Indirect FSRn with pre/post inc/dec', '1', '00 0000 0001 1nmm', '', '2'),
    ('MOVWI', 'k[n]', 'Move W to INDFn, Indexed Indirect', '1', '11 1111 lnkk kkkk', '', '2'),
]
