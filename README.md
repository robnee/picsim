# picsim
Simulator and Cycle counter for PIC Enhanced midrange core processors

Support for PIC Enhanced Midrange core such as the PIC 16F1826.  Mostly used for cycle counting as the bloated and cumbersome MPLAB X is terrible overkill for this task.

### Mini assembler

Includes a mini assembler that allows a partial symbolic representation. Mostly useful for writing test cases vs real coding.  assembler function takes decoder object, source code and register name dictionary

Assembly format:

[symbol]  [instruction [arg, arg, ...]]
    
symbol if present must start in column 1. arg values may be symbols or predefined 
register or bit names (STATUS, BSR, GIE, etc) or destination flags (F or W).  Case
is ignored.  Numeric values assume decimal radix.
    
macro instructions:
ORG - defines value of pc: org 0x004
EQU - defines a symbolic constant: x equ 0x20
    
symbol when not part of an EQU macro defines symbolic constant for current pc.  May
preface machine instruction, ORG macro or by itself

Example:

    x       equ 0x20
    
    reset   org 0x0000
            clrf STATUS, f
    loop    
            org 0x0004
            movlw 0x23
            movwf x
            addwf x,w
            goto loop


