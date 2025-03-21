from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont


class TemperatureHumidityWidget(QWidget):
    """Widget to display temperature and humidity data from Arduino sensor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title label
        title_label = QLabel("Environmental Conditions")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Data frame
        data_frame = QFrame()
        data_frame.setFrameShape(QFrame.StyledPanel)
        data_frame.setFrameShadow(QFrame.Raised)
        data_layout = QVBoxLayout(data_frame)
        
        # Temperature display
        temp_layout = QHBoxLayout()
        temp_label = QLabel("Temperature:")
        temp_label.setMinimumWidth(100)
        self.temp_value = QLabel("--.- °C")
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_value)
        data_layout.addLayout(temp_layout)
        
        # Humidity display
        humidity_layout = QHBoxLayout()
        humidity_label = QLabel("Humidity:")
        humidity_label.setMinimumWidth(100)
        self.humidity_value = QLabel("--.-- %")
        humidity_layout.addWidget(humidity_label)
        humidity_layout.addWidget(self.humidity_value)
        data_layout.addLayout(humidity_layout)
        
        layout.addWidget(data_frame)
        layout.addStretch()
        
        self.setLayout(layout)
        
    @Slot(float)
    def update_temperature(self, value):
        """Update temperature display"""
        self.temp_value.setText(f"{value:.1f} °C")
        
    @Slot(float)
    def update_humidity(self, value):
        """Update humidity display"""
        self.humidity_value.setText(f"{value:.1f} %")
