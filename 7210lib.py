import serial  
import time
import datetime
import MySQLdb

def serial_settings (serialport):
    #serialport = "/dev/ttyUSB0"
    return serial.Serial(
        port=serialport,
        baudrate=19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )

def database_upload (timedata,voltdata,currnetdata):

    try:
        conn = MySQLdb.connect(host= "192.168.60.26",
            user="root",
            passwd="nusseris",
            db="outdoorpid")
    except:
        print "unable to connect to the database"
    cur = conn.cursor()
    query = "INSERT INTO leakagecurrent (timestamp,voltage,leakagecurrent) VALUES (%s,%s,%s) "
    sqldata = (timedata,float(voltdata),float(currnetdata))
    cur.execute (query,sqldata)
    conn.commit()
    conn.close    

def logdata(serialport) :
    res = getdata (serialport)
    database_upload(currenttime (),res[0],res[2])    


def runcommand (serialport,cmd):
    ser = serial_settings (serialport)
    ser.write((cmd+"\r").encode())
    time.sleep(0.05)
    reply = remove_letter(ser.readline())
    time.sleep(0.05)
    ser.close()
    return reply
    

def executecommand (serialport,command):    
    if (check_machine (serialport)&8 !=8) :
        print "machine is not on "  
    time.sleep(0.05)
    return runcommand (serialport,command)

def check_machine (serialport):
    state = runcommand(serialport,"DSR?")
    #time.sleep(0.2)
    if state =="": 
        # replace into warning in future
        print "machine down"
    #print ("state is "+state) 
    return int (state)    

def machine_status (serialport):
    statusvalue = check_machine (serialport)
    status= ''
    if (statusvalue & 1 ==1 ): status = status+'machine is ready \n'
    if (statusvalue & 2 ==2 ): status = status+'machine is Invalid setting \n'
    if (statusvalue & 4 ==4 ): status = status+'test voltage is on (testing is on) \n'
    if (statusvalue & 8 ==8 ): status = status+'machine has voltage output \n'
    if (statusvalue & 16 ==16 ): 
        failstatus = int (runcommand(serialport,"fail?"))
        if (failstatus & 2 ==2 ): status = status+' Lower resistance has problem \n'
        if (failstatus & 4 ==4 ): status = status+' upper resistance has problem \n'
    print (status)
    
def getdata (serialport):
    return executecommand (serialport,'mon?').split(',')

def set_voltage (serialport,voltage):
    feedback = runcommand (serialport,'tes '+str(voltage))
    print ("voltage set is "+ feedback)
    

def start_machine (serialport):
    if (1&check_machine(serialport)==1):
        print 'machine is ready'
        runcommand(serialport,"star")
        time.sleep(0.2)
        if (12==check_machine (serialport)):print 'machine is on'
    else : print 'machine is off'
    
    
def stop_machine (serialport):
    time.sleep(0.2)
    executecommand (serialport,'stop')   
    
def set_lower_resistance_limit(serialport,lower_resistance):
    feedback = runcommand (serialport,'low '+str(lower_resistance)+',0')
    print ("lower resistance set is "+ feedback)
    
def set_upper_resistance_limit(serialport,upper_resistance):
    feedback = runcommand (serialport,'upp '+str(upper_resistance)+',0')
    print ("upper resistance set is "+ feedback)
    
def set_polarity (serialport,polarity):
    feedback = runcommand (serialport,'pol '+str(polarity))
    if (polarity==0) : print ("A terminal set to negative is "+ feedback)
    else : print ("A terminal set to positive is "+ feedback)

def check_resistance_limit(serialport):   
    feedback = runcommand (serialport,'upp?')
    print ("upper resistance set is "+ feedback)
    feedback = runcommand (serialport,'low?')
    print ("lower resistance set is "+ feedback)

def check_polarity (serialport):
    feedback = runcommand (serialport,'pol?')
    if (int(feedback)==0) : print ("A terminal  is set to negative")
    else : print ("A terminal is set to positive")
    
def currenttime (): 
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    
def remove_letter (letter):
    letter = letter[0:len(letter)-2]
    return letter
 
        
def TOS7210_setup():
    port = "/dev/ttyUSB0"
    set_voltage (port,10)
    set_upper_resistance_limit(port,'500E7')
    set_lower_resistance_limit(port,'100E6')
    set_polarity(port,0)
    start_machine (port)
    logdata(port) 
    machine_status(port)
    check_resistance_limit (port)
    check_polarity (port)
    stop_machine (port)

def main():
    TOS7210_setup()

if __name__ == '__main__':
    main()
