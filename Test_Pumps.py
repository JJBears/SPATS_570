# To see example instructions, please go to examples.md


import time
#import serial # 
import sys
import threading
import importlib

class AbstractPump(object):
    @classmethod
    def create(cls, config={'name': 'DummyPump'}):
        name = config.get('name', 'DummyPump')
        module = importlib.import_module(__name__)
        pump_class = getattr(module, name)
        return pump_class(config)
    
    def __init__(self, config):
        self.config = config
        self.name = config.get('name')
        self.conn_name = config.get('conn_name', None)
        self.baud_rate = config.get('baud_rate', 19200)
        self.solution = config.get('solution', None)
        self.timeout = config.get('timeout', 0.1)
        self.conn = None
    
class DummyPump(AbstractPump):

    def __init__(self, config):
        super().__init__(config)
        for key, value in config.items():
            setattr(self, key, value)
            print(f"Set {key} to {value}")
        print(f"Created {self.__class__.__name__} with config: {config}")

    def open_connection(self):
        print('connected to', self.conn_name)

    def send_command(self, cmd, *args):
        print(f"Sending command {cmd} with args {args}")

    def get_response(self):
        print("Getting response")

    def buzz(self, duration=0.05):
        print(f"Buzzing for {duration} seconds")

    def run_pump_commands(self, counter):
        for _ in range(counter):
            self.buzz()
            self.send_command("DIA", 26.59)
            self.send_command("PHN", 1)
            self.send_command("FUN", "RAT")
            self.send_command("RAT", "", 20.0, 'MM')
            self.send_command("VOL", 0.02)
            self.send_command("DIR", 'INF')
            self.buzz()
            self.send_command("RUN", "")
            #for j in range(5 * 60 * 60, 0, -1):  # 5 hours in seconds
            for j in range(5 , 0, -1):  # 5 seconds
                if j % 60 == 0:  # print remaining time every minute
                    print(f"{self}: {j // 60} minutes remaining pump 1")
                time.sleep(1)

class Pump(AbstractPump):
    COMMANDS = {
        "DIA": "DIA {:.4f}\r",
        "PHN": "PHN {}\r",
        "FUN": "FUN {}\r",
        "RAT": "RAT {} {} {}\r",
        "VOL": "VOL {:.4f}\r",
        "DIR": "DIR {}\r",
        "RUN": "RUN {}\r",
        "BUZ": "BUZ {} {}\r",
    }

    def __init__(self, conn_name=None, baud_rate=19200, timeout=0.1):
        self.conn_name = conn_name
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.conn = None
        if conn_name is not None:
            self.open_connection()
            
    #def open_connection(self):
        #self.conn = serial.Serial(self.conn_name, self.baud_rate, timeout=self.timeout)
        #print('connected to', self.conn.name)


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
            pump.send_command("PHN", 1)
            pump.send_command("FUN", "RAT")
            pump.send_command("RAT", "", 20.0, 'MM')
            pump.send_command("VOL", 0.02)
            pump.send_command("DIR", 'INF')
            pump.buzz()
            pump.send_command("RUN", "")
            #for j in range(5 * 60 * 60, 0, -1):  # 5 hours in seconds
            for j in range(5 , 0, -1):  # 5 seconds
                if j % 60 == 0:  # print remaining time every minute
                    print(f"{pump}: {j // 60} minutes remaining pump 1")
                time.sleep(1)

    def run_pump_commands2(pump, counter):
        for _ in range(counter):
            print('TEST 2 PUMP')
            for j in range(5 , 0, -1):  # 5 hours in seconds
                if j % 60 == 0:  # print remaining time every minute
                    print(f"{pump}: {j // 60} minutes remaining pump 2")
                time.sleep(1)

if __name__ == '__main__':

    pump_port = input("Which COM port?: ")
    if 'COM' not in pump_port: # if the user enters a non-COM port, use the DummyPump
        pump_port = None
        pump_name = 'DummyPump'
    else:
        pump_name = 'Pump'

    solution = input("Which solution do you want to use?: ")
    pump1 = AbstractPump.create({'name': pump_name, 'conn_name': pump_port, 'solution': solution})
    pump2 = AbstractPump.create({'name': pump_name, 'conn_name': pump_port, 'solution': solution})

    try:
        # pump1 = Pump('COM8')
        if pump1.conn is not None:
            while pump1.conn.inWaiting():
                print(pump1.get_response())
        thread1 = threading.Thread(target=Pump.run_pump_commands, args=(pump1, 3))
        thread1.daemon = True
    except Exception as e:
        print(f"Failed to connect to pump1: {e}")

    try:
        # pump2 = Pump('COM9')
        if pump2.conn is not None:
            while pump2.conn.inWaiting():
                print(pump2.get_response())
        thread2 = threading.Thread(target=Pump.run_pump_commands, args=(pump1, 3))
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
