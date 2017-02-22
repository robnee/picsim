# from p16f1826.inc
 
#-----Bank0------------------
INDF0          = 0x0000
INDF1          = 0x0001
PCL            = 0x0002
STATUS         = 0x0003
FSR0           = 0x0004
FSR0L          = 0x0004
FSR0H          = 0x0005
FSR1           = 0x0006
FSR1L          = 0x0006
FSR1H          = 0x0007
BSR            = 0x0008
WREG           = 0x0009
PCLATH         = 0x000A
INTCON         = 0x000B
PORTA          = 0x000C
PORTB          = 0x000D
PIR1           = 0x0011
PIR2           = 0x0012
TMR0           = 0x0015
TMR1           = 0x0016
TMR1L          = 0x0016
TMR1H          = 0x0017
T1CON          = 0x0018
T1GCON         = 0x0019
TMR2           = 0x001A
PR2            = 0x001B
T2CON          = 0x001C
CPSCON0        = 0x001E
CPSCON1        = 0x001F

#-----Bank1------------------
TRISA          = 0x008C
TRISB          = 0x008D
PIE1           = 0x0091
PIE2           = 0x0092
OPTION_REG     = 0x0095
PCON           = 0x0096
WDTCON         = 0x0097
OSCTUNE        = 0x0098
OSCCON         = 0x0099
OSCSTAT        = 0x009A
ADRES          = 0x009B
ADRESL         = 0x009B
ADRESH         = 0x009C
ADCON0         = 0x009D
ADCON1         = 0x009E

#-----Bank2------------------
LATA           = 0x010C
LATB           = 0x010D
CM1CON0        = 0x0111
CM1CON1        = 0x0112
CM2CON0        = 0x0113
CM2CON1        = 0x0114
CMOUT          = 0x0115
BORCON         = 0x0116
FVRCON         = 0x0117
DACCON0        = 0x0118
DACCON1        = 0x0119
SRCON0         = 0x011A
SRCON1         = 0x011B
APFCON0        = 0x011D
APFCON1        = 0x011E

#-----Bank3------------------
ANSELA         = 0x018C
ANSELB         = 0x018D
EEADR          = 0x0191
EEADRL         = 0x0191
EEADRH         = 0x0192
EEDAT          = 0x0193
EEDATL         = 0x0193
EEDATH         = 0x0194
EECON1         = 0x0195
EECON2         = 0x0196
RCREG          = 0x0199
TXREG          = 0x019A
SP1BRG         = 0x019B
SP1BRGL        = 0x019B
SPBRG          = 0x019B
SPBRGL         = 0x019B
SP1BRGH        = 0x019C
SPBRGH         = 0x019C
RCSTA          = 0x019D
TXSTA          = 0x019E
BAUDCON        = 0x019F

#-----Bank4------------------
WPUA           = 0x020C
WPUB           = 0x020D
SSP1BUF        = 0x0211
SSPBUF         = 0x0211
SSP1ADD        = 0x0212
SSPADD         = 0x0212
SSP1MSK        = 0x0213
SSPMSK         = 0x0213
SSP1STAT       = 0x0214
SSPSTAT        = 0x0214
SSP1CON1       = 0x0215
SSPCON         = 0x0215
SSPCON1        = 0x0215
SSP1CON2       = 0x0216
SSPCON2        = 0x0216
SSP1CON3       = 0x0217
SSPCON3        = 0x0217

#-----Bank5------------------
CCPR1          = 0x0291
CCPR1L         = 0x0291
CCPR1H         = 0x0292
CCP1CON        = 0x0293
PWM1CON        = 0x0294
CCP1AS         = 0x0295
ECCP1AS        = 0x0295
PSTR1CON       = 0x0296

#-----Bank7------------------
IOCBP          = 0x0394
IOCBN          = 0x0395
IOCBF          = 0x0396
CLKRCON        = 0x039A
MDCON          = 0x039C
MDSRC          = 0x039D
MDCARL         = 0x039E
MDCARH         = 0x039F

#-----Bank31------------------
STATUS_SHAD    = 0x0FE4
WREG_SHAD      = 0x0FE5
BSR_SHAD       = 0x0FE6
PCLATH_SHAD    = 0x0FE7
FSR0L_SHAD     = 0x0FE8
FSR0H_SHAD     = 0x0FE9
FSR1L_SHAD     = 0x0FEA
FSR1H_SHAD     = 0x0FEB
STKPTR         = 0x0FED
TOSL           = 0x0FEE
TOSH           = 0x0FEF

#----- STATUS Bits -----------------------------------------------------
C              = 0x0000
DC             = 0x0001
Z              = 0x0002
NOT_PD         = 0x0003
NOT_TO         = 0x0004


#----- BSR Bits -----------------------------------------------------
BSR0           = 0x0000
BSR1           = 0x0001
BSR2           = 0x0002
BSR3           = 0x0003
BSR4           = 0x0004



#----- INTCON Bits -----------------------------------------------------
IOCIF          = 0x0000
INTF           = 0x0001
TMR0IF         = 0x0002
IOCIE          = 0x0003
INTE           = 0x0004
TMR0IE         = 0x0005
PEIE           = 0x0006
GIE            = 0x0007

T0IF           = 0x0002
T0IE           = 0x0005


#----- PORTA Bits -----------------------------------------------------
RA0            = 0x0000
RA1            = 0x0001
RA2            = 0x0002
RA3            = 0x0003
RA4            = 0x0004
RA5            = 0x0005
RA6            = 0x0006
RA7            = 0x0007


#----- PORTB Bits -----------------------------------------------------
RB0            = 0x0000
RB1            = 0x0001
RB2            = 0x0002
RB3            = 0x0003
RB4            = 0x0004
RB5            = 0x0005
RB6            = 0x0006
RB7            = 0x0007


#----- PIR1 Bits -----------------------------------------------------
TMR1IF         = 0x0000
TMR2IF         = 0x0001
CCP1IF         = 0x0002
SSP1IF         = 0x0003
TXIF           = 0x0004
RCIF           = 0x0005
ADIF           = 0x0006
TMR1GIF        = 0x0007


#----- PIR2 Bits -----------------------------------------------------
BCL1IF         = 0x0003
EEIF           = 0x0004
C1IF           = 0x0005
C2IF           = 0x0006
OSFIF          = 0x0007


#----- T1CON Bits -----------------------------------------------------
TMR1ON         = 0x0000
NOT_T1SYNC     = 0x0002
T1OSCEN        = 0x0003
T1CKPS0        = 0x0004
T1CKPS1        = 0x0005
TMR1CS0        = 0x0006
TMR1CS1        = 0x0007



#----- T1GCON Bits -----------------------------------------------------
T1GSS0         = 0x0000
T1GSS1         = 0x0001
T1GVAL         = 0x0002
T1GGO          = 0x0003
T1GSPM         = 0x0004
T1GTM          = 0x0005
T1GPOL         = 0x0006
TMR1GE         = 0x0007



#----- T2CON Bits -----------------------------------------------------
T2CKPS0        = 0x0000
T2CKPS1        = 0x0001
TMR2ON         = 0x0002
T2OUTPS0       = 0x0003
T2OUTPS1       = 0x0004
T2OUTPS2       = 0x0005
T2OUTPS3       = 0x0006



#----- CPSCON0 Bits -----------------------------------------------------
T0XCS          = 0x0000
CPSOUT         = 0x0001
CPSRNG0        = 0x0002
CPSRNG1        = 0x0003
CPSON          = 0x0007



#----- CPSCON1 Bits -----------------------------------------------------
CPSCH0         = 0x0000
CPSCH1         = 0x0001
CPSCH2         = 0x0002
CPSCH3         = 0x0003



#----- TRISA Bits -----------------------------------------------------
TRISA0         = 0x0000
TRISA1         = 0x0001
TRISA2         = 0x0002
TRISA3         = 0x0003
TRISA4         = 0x0004
TRISA5         = 0x0005
TRISA6         = 0x0006
TRISA7         = 0x0007


#----- TRISB Bits -----------------------------------------------------
TRISB0         = 0x0000
TRISB1         = 0x0001
TRISB2         = 0x0002
TRISB3         = 0x0003
TRISB4         = 0x0004
TRISB5         = 0x0005
TRISB6         = 0x0006
TRISB7         = 0x0007


#----- PIE1 Bits -----------------------------------------------------
TMR1IE         = 0x0000
TMR2IE         = 0x0001
CCP1IE         = 0x0002
SSP1IE         = 0x0003
TXIE           = 0x0004
RCIE           = 0x0005
ADIE           = 0x0006
TMR1GIE        = 0x0007


#----- PIE2 Bits -----------------------------------------------------
BCL1IE         = 0x0003
EEIE           = 0x0004
C1IE           = 0x0005
C2IE           = 0x0006
OSFIE          = 0x0007


#----- OPTION_REG Bits -----------------------------------------------------
PS0            = 0x0000
PS1            = 0x0001
PS2            = 0x0002
PSA            = 0x0003
TMR0SE         = 0x0004
TMR0CS         = 0x0005
INTEDG         = 0x0006
NOT_WPUEN      = 0x0007

T0SE           = 0x0004
T0CS           = 0x0005


#----- PCON Bits -----------------------------------------------------
NOT_BOR        = 0x0000
NOT_POR        = 0x0001
NOT_RI         = 0x0002
NOT_RMCLR      = 0x0003
STKUNF         = 0x0006
STKOVF         = 0x0007


#----- WDTCON Bits -----------------------------------------------------
SWDTEN         = 0x0000
WDTPS0         = 0x0001
WDTPS1         = 0x0002
WDTPS2         = 0x0003
WDTPS3         = 0x0004
WDTPS4         = 0x0005



#----- OSCTUNE Bits -----------------------------------------------------
TUN0           = 0x0000
TUN1           = 0x0001
TUN2           = 0x0002
TUN3           = 0x0003
TUN4           = 0x0004
TUN5           = 0x0005



#----- OSCCON Bits -----------------------------------------------------
SCS0           = 0x0000
SCS1           = 0x0001
IRCF0          = 0x0003
IRCF1          = 0x0004
IRCF2          = 0x0005
IRCF3          = 0x0006
SPLLEN         = 0x0007



#----- OSCSTAT Bits -----------------------------------------------------
HFIOFS         = 0x0000
LFIOFR         = 0x0001
MFIOFR         = 0x0002
HFIOFL         = 0x0003
HFIOFR         = 0x0004
OSTS           = 0x0005
PLLR           = 0x0006
T1OSCR         = 0x0007


#----- ADCON0 Bits -----------------------------------------------------
ADON           = 0x0000
GO_NOT_DONE    = 0x0001
CHS0           = 0x0002
CHS1           = 0x0003
CHS2           = 0x0004
CHS3           = 0x0005
CHS4           = 0x0006

ADGO           = 0x0001

GO             = 0x0001


#----- ADCON1 Bits -----------------------------------------------------
ADPREF0        = 0x0000
ADPREF1        = 0x0001
ADNREF         = 0x0002
ADCS0          = 0x0004
ADCS1          = 0x0005
ADCS2          = 0x0006
ADFM           = 0x0007



#----- LATA Bits -----------------------------------------------------
LATA0          = 0x0000
LATA1          = 0x0001
LATA2          = 0x0002
LATA3          = 0x0003
LATA4          = 0x0004
LATA6          = 0x0006
LATA7          = 0x0007


#----- LATB Bits -----------------------------------------------------
LATB0          = 0x0000
LATB1          = 0x0001
LATB2          = 0x0002
LATB3          = 0x0003
LATB4          = 0x0004
LATB5          = 0x0005
LATB6          = 0x0006
LATB7          = 0x0007


#----- CM1CON0 Bits -----------------------------------------------------
C1SYNC         = 0x0000
C1HYS          = 0x0001
C1SP           = 0x0002
C1POL          = 0x0004
C1OE           = 0x0005
C1OUT          = 0x0006
C1ON           = 0x0007


#----- CM1CON1 Bits -----------------------------------------------------
C1NCH0         = 0x0000
C1NCH1         = 0x0001
C1PCH0         = 0x0004
C1PCH1         = 0x0005
C1INTN         = 0x0006
C1INTP         = 0x0007



#----- CM2CON0 Bits -----------------------------------------------------
C2SYNC         = 0x0000
C2HYS          = 0x0001
C2SP           = 0x0002
C2POL          = 0x0004
C2OE           = 0x0005
C2OUT          = 0x0006
C2ON           = 0x0007


#----- CM2CON1 Bits -----------------------------------------------------
C2NCH0         = 0x0000
C2NCH1         = 0x0001
C2PCH0         = 0x0004
C2PCH1         = 0x0005
C2INTN         = 0x0006
C2INTP         = 0x0007



#----- CMOUT Bits -----------------------------------------------------
MC1OUT         = 0x0000
MC2OUT         = 0x0001


#----- BORCON Bits -----------------------------------------------------
BORRDY         = 0x0000
SBOREN         = 0x0007


#----- FVRCON Bits -----------------------------------------------------
ADFVR0         = 0x0000
ADFVR1         = 0x0001
CDAFVR0        = 0x0002
CDAFVR1        = 0x0003
TSRNG          = 0x0004
TSEN           = 0x0005
FVRRDY         = 0x0006
FVREN          = 0x0007



#----- DACCON0 Bits -----------------------------------------------------
DACNSS         = 0x0000
DACPSS0        = 0x0002
DACPSS1        = 0x0003
DACOE          = 0x0005
DACLPS         = 0x0006
DACEN          = 0x0007



#----- DACCON1 Bits -----------------------------------------------------
DACR0          = 0x0000
DACR1          = 0x0001
DACR2          = 0x0002
DACR3          = 0x0003
DACR4          = 0x0004



#----- SRCON0 Bits -----------------------------------------------------
SRPR           = 0x0000
SRPS           = 0x0001
SRNQEN         = 0x0002
SRQEN          = 0x0003
SRCLK0         = 0x0004
SRCLK1         = 0x0005
SRCLK2         = 0x0006
SRLEN          = 0x0007



#----- SRCON1 Bits -----------------------------------------------------
SRRC1E         = 0x0000
SRRC2E         = 0x0001
SRRCKE         = 0x0002
SRRPE          = 0x0003
SRSC1E         = 0x0004
SRSC2E         = 0x0005
SRSCKE         = 0x0006
SRSPE          = 0x0007


#----- APFCON0 Bits -----------------------------------------------------
CCP1SEL        = 0x0000
P1CSEL         = 0x0001
P1DSEL         = 0x0002
SS1SEL         = 0x0005
SDO1SEL        = 0x0006
RXDTSEL        = 0x0007


#----- APFCON1 Bits -----------------------------------------------------
TXCKSEL        = 0x0000


#----- ANSELA Bits -----------------------------------------------------
ANSA0          = 0x0000
ANSA1          = 0x0001
ANSA2          = 0x0002
ANSA3          = 0x0003
ANSA4          = 0x0004



#----- ANSELB Bits -----------------------------------------------------
ANSB1          = 0x0001
ANSB2          = 0x0002
ANSB3          = 0x0003
ANSB4          = 0x0004
ANSB5          = 0x0005
ANSB6          = 0x0006
ANSB7          = 0x0007



#----- EECON1 Bits -----------------------------------------------------
RD             = 0x0000
WR             = 0x0001
WREN           = 0x0002
WRERR          = 0x0003
FREE           = 0x0004
LWLO           = 0x0005
CFGS           = 0x0006
EEPGD          = 0x0007


#----- RCSTA Bits -----------------------------------------------------
RX9D           = 0x0000
OERR           = 0x0001
FERR           = 0x0002
ADDEN          = 0x0003
CREN           = 0x0004
SREN           = 0x0005
RX9            = 0x0006
SPEN           = 0x0007


#----- TXSTA Bits -----------------------------------------------------
TX9D           = 0x0000
TRMT           = 0x0001
BRGH           = 0x0002
SENDB          = 0x0003
SYNC           = 0x0004
TXEN           = 0x0005
TX9            = 0x0006
CSRC           = 0x0007


#----- BAUDCON Bits -----------------------------------------------------
ABDEN          = 0x0000
WUE            = 0x0001
BRG16          = 0x0003
SCKP           = 0x0004
RCIDL          = 0x0006
ABDOVF         = 0x0007


#----- WPUA Bits -----------------------------------------------------
WPUA5          = 0x0005



#----- WPUB Bits -----------------------------------------------------
WPUB0          = 0x0000
WPUB1          = 0x0001
WPUB2          = 0x0002
WPUB3          = 0x0003
WPUB4          = 0x0004
WPUB5          = 0x0005
WPUB6          = 0x0006
WPUB7          = 0x0007



#----- SSP1STAT Bits -----------------------------------------------------
BF             = 0x0000
UA             = 0x0001
R_NOT_W        = 0x0002
S              = 0x0003
P              = 0x0004
D_NOT_A        = 0x0005
CKE            = 0x0006
SMP            = 0x0007


#----- SSPSTAT Bits -----------------------------------------------------
BF             = 0x0000
UA             = 0x0001
R_NOT_W        = 0x0002
S              = 0x0003
P              = 0x0004
D_NOT_A        = 0x0005
CKE            = 0x0006
SMP            = 0x0007


#----- SSP1CON1 Bits -----------------------------------------------------
SSPM0          = 0x0000
SSPM1          = 0x0001
SSPM2          = 0x0002
SSPM3          = 0x0003
CKP            = 0x0004
SSPEN          = 0x0005
SSPOV          = 0x0006
WCOL           = 0x0007



#----- SSPCON Bits -----------------------------------------------------
SSPM0          = 0x0000
SSPM1          = 0x0001
SSPM2          = 0x0002
SSPM3          = 0x0003
CKP            = 0x0004
SSPEN          = 0x0005
SSPOV          = 0x0006
WCOL           = 0x0007



#----- SSPCON1 Bits -----------------------------------------------------
SSPM0          = 0x0000
SSPM1          = 0x0001
SSPM2          = 0x0002
SSPM3          = 0x0003
CKP            = 0x0004
SSPEN          = 0x0005
SSPOV          = 0x0006
WCOL           = 0x0007



#----- SSP1CON2 Bits -----------------------------------------------------
SEN            = 0x0000
RSEN           = 0x0001
PEN            = 0x0002
RCEN           = 0x0003
ACKEN          = 0x0004
ACKDT          = 0x0005
ACKSTAT        = 0x0006
GCEN           = 0x0007


#----- SSPCON2 Bits -----------------------------------------------------
SEN            = 0x0000
RSEN           = 0x0001
PEN            = 0x0002
RCEN           = 0x0003
ACKEN          = 0x0004
ACKDT          = 0x0005
ACKSTAT        = 0x0006
GCEN           = 0x0007


#----- SSP1CON3 Bits -----------------------------------------------------
DHEN           = 0x0000
AHEN           = 0x0001
SBCDE          = 0x0002
SDAHT          = 0x0003
BOEN           = 0x0004
SCIE           = 0x0005
PCIE           = 0x0006
ACKTIM         = 0x0007


#----- SSPCON3 Bits -----------------------------------------------------
DHEN           = 0x0000
AHEN           = 0x0001
SBCDE          = 0x0002
SDAHT          = 0x0003
BOEN           = 0x0004
SCIE           = 0x0005
PCIE           = 0x0006
ACKTIM         = 0x0007


#----- CCP1CON Bits -----------------------------------------------------
CCP1M0         = 0x0000
CCP1M1         = 0x0001
CCP1M2         = 0x0002
CCP1M3         = 0x0003
DC1B0          = 0x0004
DC1B1          = 0x0005
P1M0           = 0x0006
P1M1           = 0x0007



#----- PWM1CON Bits -----------------------------------------------------
P1DC0          = 0x0000
P1DC1          = 0x0001
P1DC2          = 0x0002
P1DC3          = 0x0003
P1DC4          = 0x0004
P1DC5          = 0x0005
P1DC6          = 0x0006
P1RSEN         = 0x0007



#----- CCP1AS Bits -----------------------------------------------------
PSS1BD0        = 0x0000
PSS1BD1        = 0x0001
PSS1AC0        = 0x0002
PSS1AC1        = 0x0003
CCP1AS0        = 0x0004
CCP1AS1        = 0x0005
CCP1AS2        = 0x0006
CCP1ASE        = 0x0007



#----- ECCP1AS Bits -----------------------------------------------------
PSS1BD0        = 0x0000
PSS1BD1        = 0x0001
PSS1AC0        = 0x0002
PSS1AC1        = 0x0003
CCP1AS0        = 0x0004
CCP1AS1        = 0x0005
CCP1AS2        = 0x0006
CCP1ASE        = 0x0007



#----- PSTR1CON Bits -----------------------------------------------------
STR1A          = 0x0000
STR1B          = 0x0001
STR1C          = 0x0002
STR1D          = 0x0003
STR1SYNC       = 0x0004


#----- IOCBP Bits -----------------------------------------------------
IOCBP0         = 0x0000
IOCBP1         = 0x0001
IOCBP2         = 0x0002
IOCBP3         = 0x0003
IOCBP4         = 0x0004
IOCBP5         = 0x0005
IOCBP6         = 0x0006
IOCBP7         = 0x0007



#----- IOCBN Bits -----------------------------------------------------
IOCBN0         = 0x0000
IOCBN1         = 0x0001
IOCBN2         = 0x0002
IOCBN3         = 0x0003
IOCBN4         = 0x0004
IOCBN5         = 0x0005
IOCBN6         = 0x0006
IOCBN7         = 0x0007



#----- IOCBF Bits -----------------------------------------------------
IOCBF0         = 0x0000
IOCBF1         = 0x0001
IOCBF2         = 0x0002
IOCBF3         = 0x0003
IOCBF4         = 0x0004
IOCBF5         = 0x0005
IOCBF6         = 0x0006
IOCBF7         = 0x0007



#----- CLKRCON Bits -----------------------------------------------------
CLKRDIV0       = 0x0000
CLKRDIV1       = 0x0001
CLKRDIV2       = 0x0002
CLKRDC0        = 0x0003
CLKRDC1        = 0x0004
CLKRSLR        = 0x0005
CLKROE         = 0x0006
CLKREN         = 0x0007



#----- MDCON Bits -----------------------------------------------------
MDBIT          = 0x0000
MDOUT          = 0x0003
MDOPOL         = 0x0004
MDSLR          = 0x0005
MDOE           = 0x0006
MDEN           = 0x0007


#----- MDSRC Bits -----------------------------------------------------
MDMS0          = 0x0000
MDMS1          = 0x0001
MDMS2          = 0x0002
MDMS3          = 0x0003
MDMSODIS       = 0x0007



#----- MDCARL Bits -----------------------------------------------------
MDCL0          = 0x0000
MDCL1          = 0x0001
MDCL2          = 0x0002
MDCL3          = 0x0003
MDCLSYNC       = 0x0005
MDCLPOL        = 0x0006
MDCLODIS       = 0x0007



#----- MDCARH Bits -----------------------------------------------------
MDCH0          = 0x0000
MDCH1          = 0x0001
MDCH2          = 0x0002
MDCH3          = 0x0003
MDCHSYNC       = 0x0005
MDCHPOL        = 0x0006
MDCHODIS       = 0x0007



#----- STATUS_SHAD Bits -----------------------------------------------------
C_SHAD         = 0x0000
DC_SHAD        = 0x0001
Z_SHAD         = 0x0002

