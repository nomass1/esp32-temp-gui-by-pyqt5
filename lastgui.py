import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGroupBox, QFrame, QTableWidget, \
    QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer, QDateTime, Qt
import pyqtgraph as pg
import serial

# Serial port for UART communication with ESP32
SERIAL_PORT = 'COM3'  # Adjust according to the port where ESP32 is connected

# Save path for data files
SAVE_PATH = 'C:/Keng/test note'

class SensorGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.time_data = []
        self.temperature_data = []
        self.humidity_data = []
        self.pressure_data = []

        self.initUI()
        self.init_serial()
        self.init_timers()

    def initUI(self):
        self.setWindowTitle('ESP32 Sensor Data')
        self.resize(1200, 800)

        # Left side: Group box for sensor data
        self.group_box = QGroupBox('Sensor Data')
        group_layout = QVBoxLayout()

        # Temperature label
        self.temperature_label = QLabel('Temperature: N/A')
        self.temperature_label.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.temperature_label.setLineWidth(2)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.temperature_label.setStyleSheet("background-color: #FF6347; font-size: 18px; padding: 10px;")

        # Humidity label
        self.humidity_label = QLabel('Humidity: N/A')
        self.humidity_label.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.humidity_label.setLineWidth(2)
        self.humidity_label.setAlignment(Qt.AlignCenter)
        self.humidity_label.setStyleSheet("background-color: #1E90FF; font-size: 18px; padding: 10px;")

        # Pressure label
        self.pressure_label = QLabel('Pressure: N/A')
        self.pressure_label.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.pressure_label.setLineWidth(2)
        self.pressure_label.setAlignment(Qt.AlignCenter)
        self.pressure_label.setStyleSheet("background-color: #32CD32; font-size: 18px; padding: 10px;")

        # Add labels to group layout
        group_layout.addWidget(self.temperature_label)
        group_layout.addWidget(self.humidity_label)
        group_layout.addWidget(self.pressure_label)

        # Set group layout to group box
        self.group_box.setLayout(group_layout)

        # Right side: Table and Graph
        table_graph_layout = QVBoxLayout()

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Timestamp", "Temperature (°C)", "Humidity (%)", "Pressure (hPa)"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Graphs layout
        graph_layout = QHBoxLayout()

        # Temperature Graph
        self.temperature_group = QGroupBox('Temperature Graph')
        temperature_layout = QVBoxLayout()
        self.temperature_graph = pg.PlotWidget()
        self.temperature_graph.setBackground('k')  # Set black background
        self.temperature_graph.setTitle("Temperature over Time", color="b", size="15pt")
        self.temperature_graph.setLabel('left', 'Temperature (°C)', color='red', size=12)
        self.temperature_graph.setLabel('bottom', 'Time', color='red', size=12)
        self.temperature_graph.showGrid(x=True, y=True)
        self.temperature_graph.addLegend()
        self.temperature_plot = self.temperature_graph.plot([], [], pen=pg.mkPen(color='r', width=2), name="Temperature")
        self.temperature_graph.setYRange(0, 70)  # Set fixed range for Y-axis
        temperature_layout.addWidget(self.temperature_graph)
        self.temperature_group.setLayout(temperature_layout)
        graph_layout.addWidget(self.temperature_group)

        # Humidity Graph
        self.humidity_group = QGroupBox('Humidity Graph')
        humidity_layout = QVBoxLayout()
        self.humidity_graph = pg.PlotWidget()
        self.humidity_graph.setBackground('k')  # Set black background
        self.humidity_graph.setTitle("Humidity over Time", color="b", size="15pt")
        self.humidity_graph.setLabel('left', 'Humidity (%)', color='blue', size=12)
        self.humidity_graph.setLabel('bottom', 'Time', color='blue', size=12)
        self.humidity_graph.showGrid(x=True, y=True)
        self.humidity_graph.addLegend()
        self.humidity_plot = self.humidity_graph.plot([], [], pen=pg.mkPen(color='b', width=2), name="Humidity")
        self.humidity_graph.setYRange(0, 100)  # Set fixed range for Y-axis
        humidity_layout.addWidget(self.humidity_graph)
        self.humidity_group.setLayout(humidity_layout)
        graph_layout.addWidget(self.humidity_group)

        # Pressure Graph
        self.pressure_group = QGroupBox('Pressure Graph')
        pressure_layout = QVBoxLayout()
        self.pressure_graph = pg.PlotWidget()
        self.pressure_graph.setBackground('k')  # Set black background
        self.pressure_graph.setTitle("Pressure over Time", color="b", size="15pt")
        self.pressure_graph.setLabel('left', 'Pressure (hPa)', color='green', size=12)
        self.pressure_graph.setLabel('bottom', 'Time', color='green', size=12)
        self.pressure_graph.showGrid(x=True, y=True)
        self.pressure_graph.addLegend()
        self.pressure_plot = self.pressure_graph.plot([], [], pen=pg.mkPen(color='g', width=2), name="Pressure")
        self.pressure_graph.setYRange(0, 1100)  # Set fixed range for Y-axis
        pressure_layout.addWidget(self.pressure_graph)
        self.pressure_group.setLayout(pressure_layout)
        graph_layout.addWidget(self.pressure_group)

        # Add table and graphs to the layout
        table_graph_layout.addWidget(self.table_widget)
        table_graph_layout.addLayout(graph_layout)

        # Combine left and right layouts
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.group_box, stretch=3)
        main_layout.addLayout(table_graph_layout, stretch=7)

        # Add button layout at the bottom
        button_layout = QHBoxLayout()
        self.save_button = QPushButton('Save to Notepad')
        self.save_button.clicked.connect(self.save_to_notepad)
        button_layout.addStretch(1)
        button_layout.addWidget(self.save_button)
        button_layout.addStretch(1)

        # Combine main layout and button layout
        main_layout.addLayout(button_layout)

        # Set main layout
        self.setLayout(main_layout)

        # Set stylesheet for entire application
        self.setStyleSheet("""
        QWidget {
        font-family: 'Arial';
        font-size: 14px;
        background-color: #333; /* Dark background color */
        color: white; /* Text color */
        }
        QGroupBox {
        font-weight: bold;
        font-size: 16px;
        padding: 10px;
        margin-top: 20px;
        background-color: #444; /* Darker group box background */
        border: 2px solid #666; /* Border color */
        border-radius: 8px;
        }
        QTableWidget {
        font-size: 14px;
        background-color: #555; /* Table background color */
        color: white; /* Table text color */
        gridline-color: #666; /* Table grid line color */
        }
        QPushButton {
        font-size: 16px;
        padding: 10px 20px;
        background-color: #4682B4;
        color: white;
        border-radius: 10px;
        }
        QPushButton:hover {
        background-color: #5A9BD5;
        }
        """)


    def init_serial(self):
        # Connect to ESP32 via UART
        try:
            self.serial = serial.Serial(SERIAL_PORT, 115200, timeout=1)
            print(f"Connected to {SERIAL_PORT}")
        except serial.SerialException as e:
            print(f"Failed to connect to {SERIAL_PORT}: {e}")
            sys.exit(1)

    def init_timers(self):
        # Start timer for updating sensor data
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(1000)  # Update every second

        # Start timer for auto-saving data
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.auto_save_data)
        self.save_timer.start(10000)  # Auto-save every 10 seconds

    def update_sensor_data(self):
        # Update sensor data from ESP32
        try:
            while self.serial.in_waiting:
                data = self.serial.readline().strip()
                if data:
                    try:
                        temperature, pressure, humidity = data.split(b',')
                        temperature = temperature.decode()
                        humidity = humidity.decode()
                        pressure = pressure.decode()

                        # Update labels
                        self.temperature_label.setText(f'Temperature: {temperature} °C')
                        self.humidity_label.setText(f'Humidity: {humidity} %')
                        self.pressure_label.setText(f'Pressure: {pressure} Pa')

                        # Update table
                        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
                        self.table_widget.insertRow(0)
                        self.table_widget.setItem(0, 0, QTableWidgetItem(timestamp))
                        self.table_widget.setItem(0, 1, QTableWidgetItem(temperature))
                        self.table_widget.setItem(0, 2, QTableWidgetItem(humidity))
                        self.table_widget.setItem(0, 3, QTableWidgetItem(pressure))

                        # Update graph data
                        self.time_data.append(QDateTime.currentDateTime().toSecsSinceEpoch())
                        self.temperature_data.append(float(temperature))
                        self.humidity_data.append(float(humidity))
                        self.pressure_data.append(float(pressure))

                        # Limit data points in graph
                        if len(self.time_data) > 100:
                            self.time_data = self.time_data[-100:]
                            self.temperature_data = self.temperature_data[-100:]
                            self.humidity_data = self.humidity_data[-100:]
                            self.pressure_data = self.pressure_data[-100:]

                        # Set data explicitly for the plots
                        self.temperature_plot.setData(self.time_data, self.temperature_data)
                        self.humidity_plot.setData(self.time_data, self.humidity_data)
                        self.pressure_plot.setData(self.time_data, self.pressure_data)

                        # Adjust graph range
                        self.temperature_graph.setXRange(min(self.time_data), max(self.time_data))
                        self.humidity_graph.setXRange(min(self.time_data), max(self.time_data))
                        self.pressure_graph.setXRange(min(self.time_data), max(self.time_data))


                    except ValueError:
                        print(f"Invalid data: {data}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")

    def save_to_notepad(self):
        # Save current data to a text file
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            filename, _ = QFileDialog.getSaveFileName(self, "Save Data to Notepad", "", "Text Files (*.txt)", options=options)
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
                    f.write('\t'.join(headers) + '\n')
                    for row in range(self.table_widget.rowCount()):
                        row_data = []
                        for column in range(self.table_widget.columnCount()):
                            item = self.table_widget.item(row, column)
                            if item is not None:
                                row_data.append(item.text())
                            else:
                                row_data.append('')
                        f.write('\t'.join(row_data) + '\n')
                QMessageBox.information(self, "Save Successful", "Data has been saved to Notepad successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving: {str(e)}")

    def auto_save_data(self):
        # Auto-save data to a file in specified path
        try:
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd-HHmmss")
            save_file = os.path.join(SAVE_PATH, f"data_{timestamp}.txt")
            with open(save_file, 'w', encoding='utf-8') as f:
                headers = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
                f.write('\t'.join(headers) + '\n')
                for row in range(self.table_widget.rowCount()):
                    row_data = []
                    for column in range(self.table_widget.columnCount()):
                        item = self.table_widget.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    f.write('\t'.join(row_data) + '\n')
            files = os.listdir(SAVE_PATH)
            if len(files) >= 1:
                files.sort(key=lambda x: os.path.getctime(os.path.join(SAVE_PATH, x)))
                files_to_delete = files[:len(files) - 9]
                for file_name in files_to_delete:
                    file_to_delete = os.path.join(SAVE_PATH, file_name)
                    os.remove(file_to_delete)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during auto save: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SensorGUI()
    window.setWindowTitle('ESP32 Sensor Data')
    window.show()
    sys.exit(app.exec_())
