import sys
import os

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import serial.tools.list_ports

from device import Manager_Base, Serial_Manager, Socket_Manager, Bluetooth_Manager
from chart_widget import ChartList


class Meta_UI(QWidget):

    def __init__(self):
        super(Meta_UI, self).__init__()
        self.received_data = ''  
        self.communicate_manager = Manager_Base('') 

        # State variables
        self.latest_t_a = 0.0
        self.latest_a_a = 0.0
        self.latest_t_v = 0.0
        self.latest_a_v = 0.0

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
        # Replaced QGroupBox with a standard QWidget
        dashboard_widget = QWidget()
        
        # Add a vertical layout to stack the bold title above the grid
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # The bold title matching "Terminal Output:" (without the colon)
        title_label = QLabel("<b>PID Tuning Dashboard</b>")
        main_layout.addWidget(title_label)

        # Your existing grid layout starts here
        layout = QGridLayout()

        # --- Row 0: Mode Selection & Fetch ---
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["v2i (Velocity)", "a2v (Angle)"])
        self.mode_combo.currentTextChanged.connect(
            lambda text: self.send_msg(f"tune mode {'v2i' if 'v2i' in text else 'a2v'}")
        )
        
        fetch_btn = QPushButton("Fetch Current PIDs")
        fetch_btn.clicked.connect(lambda: self.send_msg("tune get"))

        layout.addWidget(QLabel("Tuning Mode:"), 0, 0)
        layout.addWidget(self.mode_combo, 0, 1, 1, 2) 
        layout.addWidget(fetch_btn, 0, 3)

        # --- Row 1: Single-Shot Step Generation ---
        self.step_val_input = QLineEdit()
        self.step_val_input.setPlaceholderText("Target (e.g. 100)")
        
        self.step_dur_input = QLineEdit()
        self.step_dur_input.setPlaceholderText("Duration ms (e.g. 500)")
        
        step_btn = QPushButton("Run Step Sequence")
        step_btn.clicked.connect(
            lambda: self.send_msg(f"tune step {self.step_val_input.text()} {self.step_dur_input.text()}")
        )

        layout.addWidget(QLabel("Step Response:"), 1, 0)
        layout.addWidget(self.step_val_input, 1, 1)
        layout.addWidget(self.step_dur_input, 1, 2)
        layout.addWidget(step_btn, 1, 3)

        # --- Row 2: V2I PID Row ---
        self.v2i_p = QLineEdit(); self.v2i_p.setPlaceholderText("Kp")
        self.v2i_i = QLineEdit(); self.v2i_i.setPlaceholderText("Ki")
        self.v2i_d = QLineEdit(); self.v2i_d.setPlaceholderText("Kd")
        v2i_btn = QPushButton("Send V2I")
        
        def update_v2i():
            cmds = []
            if self.v2i_p.text(): cmds.append(f"tune pid v p {self.v2i_p.text()}")
            if self.v2i_i.text(): cmds.append(f"tune pid v i {self.v2i_i.text()}")
            if self.v2i_d.text(): cmds.append(f"tune pid v d {self.v2i_d.text()}")
            
            if not cmds: return # Do nothing if all boxes are empty
            
            # Disable the button temporarily to prevent spam-clicking overflows
            v2i_btn.setEnabled(False)
            
            # Send each command with a generous 150ms delay
            delay_ms = 150
            for i, cmd in enumerate(cmds):
                QTimer.singleShot(i * delay_ms, lambda c=cmd: self.send_msg(c))
                
            # Re-enable the button precisely after the last command finishes
            QTimer.singleShot(len(cmds) * delay_ms, lambda: v2i_btn.setEnabled(True))
            
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
            cmds = []
            if self.a2v_p.text(): cmds.append(f"tune pid a p {self.a2v_p.text()}")
            if self.a2v_i.text(): cmds.append(f"tune pid a i {self.a2v_i.text()}")
            if self.a2v_d.text(): cmds.append(f"tune pid a d {self.a2v_d.text()}")
            
            if not cmds: return
            
            # Disable the button temporarily 
            a2v_btn.setEnabled(False)
            
            # Send each command with a 150ms delay
            delay_ms = 150
            for i, cmd in enumerate(cmds):
                QTimer.singleShot(i * delay_ms, lambda c=cmd: self.send_msg(c))
                
            # Re-enable the button
            QTimer.singleShot(len(cmds) * delay_ms, lambda: a2v_btn.setEnabled(True))
            
        a2v_btn.clicked.connect(update_a2v)

        layout.addWidget(QLabel("A2V PID:"), 3, 0)
        layout.addWidget(self.a2v_p, 3, 1)
        layout.addWidget(self.a2v_i, 3, 2)
        layout.addWidget(self.a2v_d, 3, 3)
        layout.addWidget(a2v_btn, 3, 4)

        main_layout.addLayout(layout)
        dashboard_widget.setLayout(main_layout)
        return dashboard_widget

    def setup_terminal_widget(self):
        connection_port_combo = QComboBox()
        connection_port_combo.addItems(['Serial', 'TCP'])

        # --- NEW: Dropdown for Ports instead of TextEdit ---
        self.port_device_combo = QComboBox()
        self.port_device_combo.setMinimumWidth(150)
        
        refresh_ports_btn = QPushButton('↻')
        refresh_ports_btn.setMaximumWidth(30)
        
        def refresh_ports():
            self.port_device_combo.clear()
            ports = [port.device for port in serial.tools.list_ports.comports()]
            if not ports:
                self.port_device_combo.addItem("No ports found")
            else:
                self.port_device_combo.addItems(ports)
                
        refresh_ports_btn.clicked.connect(refresh_ports)
        refresh_ports() # Call once on startup
        # --------------------------------------------------

        connection_button = QPushButton('Connect')
        self.terminal_display = QTextBrowser()
        self.terminal_display.setMinimumHeight(200)

        command_line = QLineEdit()
        send_button = QPushButton('Send')
        clear_data_button = QPushButton('Clear Terminal')

        self.tuning_dashboard = self.create_tuning_dashboard()

        # Layout setup
        control_button_layout = QHBoxLayout()
        control_button_layout.addWidget(connection_port_combo)
        control_button_layout.addWidget(self.port_device_combo) # Replaced QLineEdit
        control_button_layout.addWidget(refresh_ports_btn)      # Added refresh button
        control_button_layout.addWidget(connection_button)

        command_line_layout = QHBoxLayout()
        command_line_layout.addWidget(command_line)
        command_line_layout.addWidget(send_button)
        command_line_layout.addWidget(clear_data_button)

        terminal_part_layout = QVBoxLayout()
        terminal_part_layout.addLayout(control_button_layout)
        terminal_part_layout.addWidget(self.tuning_dashboard) # Added the custom dashboard here
        terminal_part_layout.addWidget(QLabel("<b>Terminal Output</b>"))
        terminal_part_layout.addWidget(self.terminal_display)
        terminal_part_layout.addLayout(command_line_layout)

        # Event Callback Setup
        def update_connect_button(set_on: bool):
            connection_button.setText('Disconnect' if set_on else 'Connect')
            # if set_on:
            #     # Wait 500ms for the serial buffer to clear, then ask STM32 for PID status
            #     QTimer.singleShot(500, lambda: self.send_msg("tune status"))

        def clear_data():
            self.terminal_display.clear()

        def command_line_send_msg():
            msg = command_line.text()
            self.send_msg(msg)
            command_line.clear()

        def connection_button_clicked():
            if connection_button.text() == 'Connect':
                method = connection_port_combo.currentText()
                # Fetch text from the new combo box
                device = self.port_device_combo.currentText() 
                
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
        
        # Force the chart widget to expand into all available space
        self.chart_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        plotting_layout = QVBoxLayout()
        # Strip all default UI padding and margins
        plotting_layout.setContentsMargins(0, 0, 0, 0)
        plotting_layout.setSpacing(0)
        
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
                
                # --- Dual-Loop Telemetry Parsing ---
                if line.startswith('>t_a:'):
                    try: self.latest_t_a = float(line.split(':')[1])
                    except ValueError: pass
                
                elif line.startswith('>a_a:'):
                    try: self.latest_a_a = float(line.split(':')[1])
                    except ValueError: pass
                
                elif line.startswith('>t_v:'):
                    try: self.latest_t_v = float(line.split(':')[1])
                    except ValueError: pass
                
                elif line.startswith('>a_v:'):
                    try: 
                        self.latest_a_v = float(line.split(':')[1])
                        # WE ONLY UPDATE THE CHART HERE, ONCE WE HAVE ALL 4 VALUES
                        self.chart_list.update_tuning_chart(
                            self.latest_t_a, self.latest_a_a, 
                            self.latest_t_v, self.latest_a_v
                        )
                    except ValueError: pass

                # --- PID Fetch Parsing ---
                elif line.startswith('>pid:'):
                    parts = line.split(':')
                    if len(parts) == 5: # Expected: >pid, v, P, I, D
                        p_val, i_val, d_val = parts[2], parts[3], parts[4]
                        if parts[1] == 'v':
                            self.v2i_p.setText(p_val)
                            self.v2i_i.setText(i_val)
                            self.v2i_d.setText(d_val)
                        elif parts[1] == 'a':
                            self.a2v_p.setText(p_val)
                            self.a2v_i.setText(i_val)
                            self.a2v_d.setText(d_val)
                
                # --- Standard Terminal Print ---
                else:
                    self.update_terminal_display(line + '\n')

    def update_terminal_display(self, input_str: str):
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(input_str)
        self.terminal_display.setTextCursor(cursor)

    def send_msg(self, msg):
        try:
            clean_msg = msg.strip() 
            self.communicate_manager.SendData(bytes(clean_msg + '\r', encoding='utf-8'))
            self.update_terminal_display(f"[TX] {clean_msg}\n")
        except Exception as err:
            self.update_terminal_display('Fail to send message!\n')

if __name__ == '__main__':
    app = QApplication(sys.argv) 
    demo = Meta_UI()  
    demo.show()  
    sys.exit(app.exec_())