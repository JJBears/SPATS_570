
import logging
import time
import serial
import sys
import threading


#define Class & commands
class Pump(object):
    COMMANDS = {
        "DIA": "DIA {:.4f}\r",  # diameter
        "PHN": "PHN {}\r",  # ask/look up    
        "FUN": "FUN {}\r",  # function
        "RAT": "RAT {} {} {}\r",  # rate
        "VOL": "VOL {:.4f}\r",  # volume
        "DIR": "DIR {}\r",  # direction
        "RUN": "RUN {}\r",  # run
        "BUZ": "BUZ {} {}\r",  # buzz make sound
    }
    

    def __init__(self, conn_name=None, baud_rate=19200, timeout=0.1):
        self.conn_name = conn_name
        self.baud_rate = baud_rate  # baud rate for syringe pump is 19200
        self.timeout = timeout
        self.conn = None
        if conn_name is not None:
            self.open_connection()
            
    def open_connection(self):
        self.conn = serial.Serial(self.conn_name, self.baud_rate, timeout=self.timeout)
        print('connected to', self.conn.name)


    def send_command(self, cmd, *args):
        cmd_string = self.COMMANDS[cmd].format(*args)
        print("write -> %s" % cmd_string.strip())
        self.conn.write(cmd_string.encode())
        return self.get_response()

    def get_response(self):
        msg = self.conn.read_until('\x03')
        print(msg)
        if not len(msg):
            print("Received an empty response.")
        return msg

    def buzz(self, duration=0.05):
        self.send_command("BUZ", 1, 1)
        time.sleep(duration)
        self.send_command("BUZ", 0, 1)


    def run_pump_commands(pump, counter):
        for _ in range(counter):
            pump.buzz()
            pump.send_command("DIA", 26.59)
            time.sleep(1)  # Add delay
            pump.send_command("PHN", 1)
            time.sleep(1)  # Add delay
            pump.send_command("FUN", "RAT")
            time.sleep(1)  # Add delay
            pump.send_command("RAT", "", 20.0, 'MM')
            time.sleep(1)  # Add delay
            pump.send_command("VOL", 0.02)
            time.sleep(1)  # Add delay
            pump.send_command("DIR", 'INF')
            time.sleep(1)  # Add delay
            pump.buzz()
            time.sleep(1)  # Add delay
            pump.send_command("RUN", "")
            #for j in range(5 * 60 * 60, 0, -1):  # 5 hours in seconds
            for j in range(5 , 0, -1):  # 5 seconds
                if j % 60 == 0:  # print remaining time every minute
                    print(f"{pump}: {j // 60} minutes remaining pump 1")
                time.sleep(1)
        logging.info("run_pump_commands finished at %s", time.strftime("%Y-%m-%d %H:%M:%S"))

#ask for pump test beep
Test_beep = input("Do you want to test the beep? (y/n): ")
if Test_beep == 'y':
    print('Testing beep...')
    pump = Pump('COM8')
    pump.BUZ()
    print('Beep test done.')

#ask for which solution to use
solution = input("Which solution do you want to use?: ")
if solution == 'CaC':
    print('CaC 120mL rate 40ml/6 hours')
    pump = Pump('RUN'
    'DIA 26.59\r'
    'PHN 1\r'
    'FUN RAT\r'
    'RAT 40.0 MM\r'
    'VOL 120.0\r'
    'DIR INF\r'
    'RUN\r'
    'BUZ 1 1\r')
if solution == 'EtOh':
    print('EtOh 120mL rate 40ml/6 hours')
    pump = Pump('RUN'
    'DIA 26.59\r'
    'PHN 1\r'
    'FUN RAT\r'
    'RAT 30.0 MM\r'
    'VOL 60.0\r'
    'DIR INF\r'
    'RUN\r'
    'BUZ 1 1\r')
if solution == 'CaC_H2O':
    print('CaC_H2O 120mL rate 40ml/6 hours')
    pump = Pump('RUN'
    'DIA 26.59\r'
    'PHN 1\r'
    'FUN RAT\r'
    'RAT 40.0 MM\r'
    'VOL 120.0\r'
    'DIR INF\r'
    'RUN\r'
    'BUZ 1 1\r')



    def run_pump_commands2(pump, counter):
        for _ in range(counter):
            print('TEST 2 PUMP')
            for j in range(5 , 0, -1):  # 5 hours in seconds
                if j % 60 == 0:  # print remaining time every minute
                    print(f"{pump}: {j // 60} minutes remaining pump 2")
                time.sleep(1)
            time.sleep(1)  # Add delay
        logging.info("run_pump_commands2 finished at %s", time.strftime("%Y-%m-%d %H:%M:%S"))



if __name__ == '__main__':


    try:
        pump1 = Pump('COM8')
        while pump1.conn.inWaiting():
            print(pump1.get_response())
        thread1 = threading.Thread(target=Pump.run_pump_commands, args=(pump1, 3))
        thread1.daemon = True
    except Exception as e:
        print(f"Failed to connect to pump1: {e}")

    try:
        pump2 = Pump('COM9')
        while pump2.conn.inWaiting():
            print(pump2.get_response())
        thread2 = threading.Thread(target=Pump.run_pump_commands2, args=(pump1, 3))
        thread2.daemon = True
    except Exception as e:
        print(f"Failed to connect to pump2: {e}")

    try:
        if thread1 is not None:
            thread1.start()
        if thread2 is not None:
            thread2.start()

        # if thread1 is not None:
        #     thread1.join()
        # if thread2 is not None:
        #     thread2.join()
        
        
        while thread1.is_alive() or thread2.is_alive():
            time.sleep(1)  # Wait for the threads to finish
        
    except (KeyboardInterrupt, SystemExit):
        print("Stopping threads...")
        # Here you can add any cleanup code if needed
        sys.exit(0)
