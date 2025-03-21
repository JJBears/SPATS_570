import serial
import json
import logging
from PySide6.QtCore import QThread, Signal, QObject, Slot, QTimer

logger = logging.getLogger(__name__)

class ArduinoTempHumidity(QObject):
    """
    Arduino-based temperature and humidity sensor device using DHT22
    
    Communicates with an Arduino running temp_humidity.ino sketch via serial
    """
    temperature_changed = Signal(float)
    humidity_changed = Signal(float)
    logger = Signal(str, str)
    heartbeat = Signal(str, bool)  # device_name, is_connected
    stateChanged = Signal(str, str)  # device_name, state

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.port = config.get("port", "COM4")
        self.baud_rate = config.get("baud_rate", 9600)
        self.name = config.get("name", "ArduinoTempHumidity")
        self.serial = None
        self.connected = False
        self.temperature = 0.0
        self.humidity = 0.0
        self.state = "disconnected"
        
        # Setup thread
        self.thread = QThread()
        self.thread.setObjectName(f"{self.name}Thread")
        self.moveToThread(self.thread)
        self.thread.started.connect(self.initialize)
        
        # Setup timer for polling sensor data
        self.timer = QTimer()
        self.timer.moveToThread(self.thread)
        self.timer.timeout.connect(self.read_sensor_data)
        self.polling_interval = config.get("polling_interval", 2000)  # 2 seconds default
        
    def start(self):
        """Start the device thread"""
        self.thread.start()
        
    def stop(self):
        """Stop the device thread and clean up resources"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.timer.stop()
        self.thread.quit()
        self.thread.wait()
        
    @Slot()
    def initialize(self):
        """Initialize serial connection to Arduino"""
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            self.logger.emit(f"{self.name} connected on port {self.port}", "info")
            self.connected = True
            self.state = "connected"
            self.stateChanged.emit(self.name, self.state)
            self.heartbeat.emit(self.name, True)
            
            # Start polling timer
            self.timer.start(self.polling_interval)
        except Exception as e:
            self.logger.emit(f"Failed to connect to {self.name}: {str(e)}", "error")
            self.heartbeat.emit(self.name, False)
            self.state = "error"
            self.stateChanged.emit(self.name, self.state)
    
    @Slot()
    def read_sensor_data(self):
        """Read and process temperature and humidity data from the Arduino"""
        if not self.serial or not self.serial.is_open:
            self.heartbeat.emit(self.name, False)
            return
            
        try:
            # Clear any old data in the buffer
            self.serial.reset_input_buffer()
            
            # Read a line from the serial port
            line = self.serial.readline().decode('utf-8').strip()
            
            if line:
                # Parse the data - expecting format: "Humidity: XX.XX %, Temp: YY.YY Celsius"
                if "Humidity:" in line and "Temp:" in line:
                    parts = line.split(',')
                    
                    # Extract humidity
                    hum_part = parts[0].strip()
                    hum_val = float(hum_part.split(':')[1].strip().split('%')[0])
                    
                    # Extract temperature
                    temp_part = parts[1].strip()
                    temp_val = float(temp_part.split(':')[1].strip().split('Celsius')[0])
                    
                    # Update values and emit signals
                    if self.temperature != temp_val:
                        self.temperature = temp_val
                        self.temperature_changed.emit(self.temperature)
                        
                    if self.humidity != hum_val:
                        self.humidity = hum_val
                        self.humidity_changed.emit(self.humidity)
                        
                    # Emit heartbeat
                    self.heartbeat.emit(self.name, True)
                    
                    logger.debug(f"Read from Arduino: Temp={self.temperature}°C, Humidity={self.humidity}%")
                    
        except Exception as e:
            self.logger.emit(f"Error reading from {self.name}: {str(e)}", "error")
            self.heartbeat.emit(self.name, False)
            
    def get_temperature(self):
        """Return the current temperature"""
        return self.temperature
        
    def get_humidity(self):
        """Return the current humidity"""
        return self.humidity
