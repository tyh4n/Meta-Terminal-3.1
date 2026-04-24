import sys
import os

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from device import Manager_Base, Serial_Manager, Socket_Manager, Bluetooth_Manager
from chart_widget import ChartList


class Meta_UI(QWidget):

    def __init__(self):
        super(Meta_UI, self).__init__()
        self.received_data = ''  
        self.communicate_manager = Manager_Base('') 

        # State variables for pairing the two lines of telemetry
        self.latest_target = 0.0
        self.latest_actual = 0.0

        # Create main widgets
        self.terminal_widget = QWidget(self)
        self.plotting_tab = QWidget(self)

        # Setup main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.terminal_widget)
        main_splitter.addWidget(self.plotting_tab)
        main_splitter.setSizes([600, 1000])  # Terminal is 600px wide, plot is 1000px

        # Setup main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # Setup widgets
        self.setup_terminal_widget()
        self.setup_plotting_tab()

        # Set window properties
        self.setWindowTitle('Meta Terminal 3.1 - PID Dashboard')
        # self.setWindowIcon(QtGui.QIcon('res/meta_logo.jpeg'))
        self.resize(1600, 800) 

    def create_tuning_dashboard(self):
        """Creates a dedicated layout for PID and Signal tuning"""
        group_box = QGroupBox("PID Tuning Dashboard")
        layout = QGridLayout()

        # --- Row 0: Mode Selection & Telemetry ---
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["v2i (Velocity)", "a2v (Angle)"])
        # Send command immediately when combo box changes
        self.mode_combo.currentTextChanged.connect(
            lambda text: self.send_msg(f"tune mode {'v2i' if 'v2i' in text else 'a2v'}")
        )

        self.telemetry_check = QCheckBox("Enable Live Telemetry")
        self.telemetry_check.stateChanged.connect(
            lambda state: self.send_msg("tune print on" if state == Qt.Checked else "tune print off")
        )

        layout.addWidget(QLabel("Tuning Mode:"), 0, 0)
        layout.addWidget(self.mode_combo, 0, 1)
        layout.addWidget(self.telemetry_check, 0, 2, 1, 2)

        # --- Row 1: Signal Generation ---
        self.sig_combo = QComboBox()
        self.sig_combo.addItems(["const", "step"])
        self.sig_val_input = QLineEdit()
        self.sig_val_input.setPlaceholderText("Target Value")
        sig_btn = QPushButton("Set Signal")
        sig_btn.clicked.connect(
            lambda: self.send_msg(f"tune sig {self.sig_combo.currentText()} {self.sig_val_input.text()}")
        )

        layout.addWidget(QLabel("Target Signal:"), 1, 0)
        layout.addWidget(self.sig_combo, 1, 1)
        layout.addWidget(self.sig_val_input, 1, 2)
        layout.addWidget(sig_btn, 1, 3)

        # --- Row 2: V2I PID Row ---
        self.v2i_p = QLineEdit(); self.v2i_p.setPlaceholderText("Kp")
        self.v2i_i = QLineEdit(); self.v2i_i.setPlaceholderText("Ki")
        self.v2i_d = QLineEdit(); self.v2i_d.setPlaceholderText("Kd")
        v2i_btn = QPushButton("Send V2I")
        
        def update_v2i():
            # Only send commands for boxes that actually have text in them
            if self.v2i_p.text(): self.send_msg(f"tune pid v p {self.v2i_p.text()}")
            if self.v2i_i.text(): self.send_msg(f"tune pid v i {self.v2i_i.text()}")
            if self.v2i_d.text(): self.send_msg(f"tune pid v d {self.v2i_d.text()}")
            
        v2i_btn.clicked.connect(update_v2i)

        layout.addWidget(QLabel("V2I PID:"), 2, 0)
        layout.addWidget(self.v2i_p, 2, 1)
        layout.addWidget(self.v2i_i, 2, 2)
        layout.addWidget(self.v2i_d, 2, 3)
        layout.addWidget(v2i_btn, 2, 4)

        # --- Row 3: A2V PID Row ---
        self.a2v_p = QLineEdit(); self.a2v_p.setPlaceholderText("Kp")
        self.a2v_i = QLineEdit(); self.a2v_i.setPlaceholderText("Ki")
        self.a2v_d = QLineEdit(); self.a2v_d.setPlaceholderText("Kd")
        a2v_btn = QPushButton("Send A2V")
        
        def update_a2v():
            # Only send commands for boxes that actually have text in them
            if self.a2v_p.text(): self.send_msg(f"tune pid a p {self.a2v_p.text()}")
            if self.a2v_i.text(): self.send_msg(f"tune pid a i {self.a2v_i.text()}")
            if self.a2v_d.text(): self.send_msg(f"tune pid a d {self.a2v_d.text()}")
            
        a2v_btn.clicked.connect(update_a2v)

        layout.addWidget(QLabel("A2V PID:"), 3, 0)
        layout.addWidget(self.a2v_p, 3, 1)
        layout.addWidget(self.a2v_i, 3, 2)
        layout.addWidget(self.a2v_d, 3, 3)
        layout.addWidget(a2v_btn, 3, 4)

        group_box.setLayout(layout)
        return group_box

    def setup_terminal_widget(self):
        # Elements setup for terminal widget
        connection_port_combo = QComboBox()
        connection_port_list = ['Serial', 'TCP']
        connection_port_combo.addItems(connection_port_list)

        port_device_text = QLineEdit()
        port_device_text.setPlaceholderText('COMX or /dev/ttyUSB0')

        connection_button = QPushButton('Connect')

        self.terminal_display = QTextBrowser()
        self.terminal_display.setMinimumHeight(200)

        command_line = QLineEdit()
        send_button = QPushButton('Send')
        clear_data_button = QPushButton('Clear Terminal')

        # Generate the new dedicated dashboard
        self.tuning_dashboard = self.create_tuning_dashboard()

        # Layout setup
        control_button_layout = QHBoxLayout()
        control_button_layout.addWidget(connection_port_combo)
        control_button_layout.addWidget(port_device_text)
        control_button_layout.addWidget(connection_button)

        command_line_layout = QHBoxLayout()
        command_line_layout.addWidget(command_line)
        command_line_layout.addWidget(send_button)
        command_line_layout.addWidget(clear_data_button)

        terminal_part_layout = QVBoxLayout()
        terminal_part_layout.addLayout(control_button_layout)
        terminal_part_layout.addWidget(self.tuning_dashboard) # Added the custom dashboard here
        terminal_part_layout.addWidget(QLabel("<b>Terminal Output:</b>"))
        terminal_part_layout.addWidget(self.terminal_display)
        terminal_part_layout.addLayout(command_line_layout)

        # Event Callback Setup
        def update_connect_button(set_on: bool):
            connection_button.setText('Disconnect' if set_on else 'Connect')

        def clear_data():
            self.terminal_display.clear()

        def command_line_send_msg():
            msg = command_line.text()
            self.send_msg(msg)
            command_line.clear()

        def connection_button_clicked():
            if connection_button.text() == 'Connect':
                method = connection_port_combo.currentText()
                device = port_device_text.text()
                if method == 'Serial':
                    self.communicate_manager = Serial_Manager(device)
                elif method == 'TCP':
                    self.communicate_manager = Socket_Manager(device)
                else:
                    return
                self.received_data = ''
                self.communicate_manager.device_signal.connect(self.process_feedback)
                self.communicate_manager.connection_signal.connect(update_connect_button)
                self.communicate_manager.start()
            else:
                if self.communicate_manager is not None:
                    self.communicate_manager.stop()

        send_button.clicked.connect(command_line_send_msg)
        command_line.returnPressed.connect(command_line_send_msg)
        connection_button.clicked.connect(connection_button_clicked)
        clear_data_button.clicked.connect(clear_data)
        self.terminal_widget.setLayout(terminal_part_layout)

    def setup_plotting_tab(self):
        # One chart for active tuning loop
        self.chart_list = ChartList(self.plotting_tab, [{'name': 'Active Tuning Loop'}])
        plotting_layout = QVBoxLayout()
        plotting_layout.addWidget(self.chart_list)
        self.plotting_tab.setLayout(plotting_layout)

    def process_feedback(self, feedback: bytes):
        self.received_data += feedback.decode(encoding='utf-8', errors='ignore')
        
        if '\n' in self.received_data:
            lines = self.received_data.split('\n')
            self.received_data = lines.pop() 
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('>target:'):
                    try:
                        self.latest_target = float(line.split(':')[1])
                    except ValueError:
                        pass
                elif line.startswith('>actual:'):
                    try:
                        self.latest_actual = float(line.split(':')[1])
                        self.chart_list.update_tuning_chart(self.latest_target, self.latest_actual)
                    except ValueError:
                        pass
                else:
                    self.update_terminal_display(line + '\n')

    def update_terminal_display(self, input_str: str):
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(input_str)
        self.terminal_display.setTextCursor(cursor)

    def send_msg(self, msg):
        try:
            self.communicate_manager.SendData(bytes(msg + '\r\n', encoding='utf-8'))
            self.update_terminal_display(f"[TX] {msg}\n")
        except Exception as err:
            self.update_terminal_display('Fail to send message!\n')

if __name__ == '__main__':
    app = QApplication(sys.argv) 
    demo = Meta_UI()  
    demo.show()  
    sys.exit(app.exec_())