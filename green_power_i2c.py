import smbus
import math

bus = smbus.SMBus(1)

##Greenland power board sensor addresses (fixed):
BOARD_ADDRESS = 0x6f

##Useful sensor registers:
REG_CTRLA  = 0x00 #operation control register A
REG_CTRLB  = 0x01 #operation control register B
REG_NADC   = 0x04 #set ADC resolution
REG_I1_MSB = 0x14 #deltaSENSE1
REG_I1_LSB = 0x15 #deltaSENSE1
REG_S1_MSB = 0x1E #SENSE1 voltage
REG_S1_LSB = 0x1F #SENSE1 voltage
REG_I2_MSB = 0x46 #deltaSENSE2
REG_I2_LSB = 0x47 #deltaSENSE2
REG_S2_MSB = 0x50 #SENSE2 voltage
REG_S2_LSB = 0x51 #SENSE2 voltage
REG_G1_MSB = 0x28 #GPIO value
REG_G1_LSB = 0x29 #GPIO value

##A handful of useful command masks
LTC_ADC_RESOLUTION     = 0x80
LTC_MODE_SHUTDOWN      = 0x60
LTC_MODE_SINGLE_CYCLE  = 0x40
LTC_MODE_SNAPSHOT      = 0x20
LTC_MODE_CONTINUOUS    = 0x00

##board-level constants:
SENSE1_RESISTOR         = 0.005 #ohms
SENSE2_RESISTOR         = 0.010 #ohms
LMT88_R_DIV             = 0.8
LTC2992_SENSE_LSB_12bit = 25.00e-3 #volts
LTC2992_SENSE_LSB_8bit  = 400.00e-3 #volts
LTC2992_DELTASENSE_LSB_12bit  = 12.50e-6 #volts
LTC2992_DELTASENSE_LSB_8bit   = 200.00e-6 #volts
LTC2992_GPIO_LSB_12bit  = 0.500e-3 #volts
LTC2992_GPIO_LSB_8bit   = 8.000e-3 #volts

def write(i2c_address, register, cmd):
    '''
    8-bit code write, returns state of acknowledge bit (0=ack, 1=no ack)
    '''
    ack = bus.write_byte_data(i2c_address, register, cmd)

    return ack

def read(i2c_address, register):

    read_data = bus.read_byte_data(i2c_address, register)

    return read_data

def read12bitADC(msb, lsb):

    word = (((msb << 8) | lsb) >> 4)
    return word

def convertVoltsToTemp(volts):
    volts = float(volts) * 1./ (LMT88_R_DIV)
    temp = -1481.96 + math.sqrt(2.1962e6 + (1.8639-volts)/(3.88e-6))
    return temp

def getBoardTemp():
    '''
    assuming 12-bit ADC mode (default)
    returns temp in Celsius
    '''
    
    msb = read(BOARD_ADDRESS, REG_G1_MSB)
    lsb = read(BOARD_ADDRESS, REG_G1_LSB)
    volts = read12bitADC(msb,lsb) * LTC2992_GPIO_LSB_12bit

    temp = convertVoltsToTemp(volts)
    return temp

def getVoltsAndCurrents():
    '''
    assuming 12-bit ADC mode (default)
    returns volts and amps
    '''
    #PV panel (perhaps only PVv is a sensible measurement, depending on field wiring)
    PVv_msb = read(BOARD_ADDRESS, REG_S1_MSB)
    PVv_lsb = read(BOARD_ADDRESS, REG_S1_LSB)
    PVi_msb = read(BOARD_ADDRESS, REG_I1_MSB)
    PVi_lsb = read(BOARD_ADDRESS, REG_I1_LSB)
    
    BATv_msb = read(BOARD_ADDRESS, REG_S2_MSB)
    BATv_lsb = read(BOARD_ADDRESS, REG_S2_LSB)
    BATi_msb = read(BOARD_ADDRESS, REG_I2_MSB)
    BATi_lsb = read(BOARD_ADDRESS, REG_I2_LSB)

    PVv = read12bitADC(PVv_msb,PVv_lsb) * LTC2992_SENSE_LSB_12bit
    PVi = read12bitADC(PVi_msb,PVi_lsb) * LTC2992_DELTASENSE_LSB_12bit / SENSE1_RESISTOR

    BATv = read12bitADC(BATv_msb,BATv_lsb) * LTC2992_SENSE_LSB_12bit
    BATi = read12bitADC(BATi_msb,BATi_lsb) * LTC2992_DELTASENSE_LSB_12bit / SENSE2_RESISTOR

    return PVv,PVi,BATv,BATi
    
if __name__=='__main__':

    
    print read(BOARD_ADDRESS, REG_CTRLA)
    print getBoardTemp()
    print getVoltsAndCurrents()

    
