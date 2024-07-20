import sys
import os

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from device import Manager_Base, Serial_Manager, Socket_Manager, Bluetooth_Manager
from chart_widget import ChartList
from command_widget import CommandPanel


class Meta_UI(QWidget):

    def __init__(self):
        super(Meta_UI, self).__init__()
        self.received_data = ''  # Initialize received data variable
        self.communicate_manager = Manager_Base('')  # Initialize communication manager

        # Create main widgets
        self.terminal_widget = QWidget(self)
        self.plotting_tab = QWidget(self)

        # Setup main splitter to divide terminal and plotting tab
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.terminal_widget)
        main_splitter.addWidget(self.plotting_tab)

        # Set initial sizes for the widgets in the splitter
        main_splitter.setSizes([800, 800])  # Adjust the values to make the plotting tab wider

        # Setup main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)

        # Setup widgets
        self.setup_terminal_widget()
        self.setup_plotting_tab()

        # Set window properties
        self.setWindowTitle('Meta Terminal 3.1')
        self.setWindowIcon(QtGui.QIcon('res/meta_logo.jpeg'))
        self.resize(1600, 1200)  # Set the initial window size

    def setup_terminal_widget(self):
        # Elements setup for terminal widget
        connection_port_combo = QComboBox()
        connection_port_list = ['Serial', 'TCP']
        connection_port_combo.addItems(connection_port_list)

        port_device_text = QLineEdit()
        port_device_text.setPlaceholderText('Port/Device')

        connection_button = QPushButton()
        connection_button.setText('Connect')

        self.terminal_display = QTextBrowser()
        self.terminal_display.resize(640, 480)

        command_line = QLineEdit()

        send_button = QPushButton()
        send_button.setText('Send')

        clear_data_button = QPushButton()
        clear_data_button.setText('Clear')

        # Layout setup
        control_button_layout = QHBoxLayout()
        control_button_layout.setContentsMargins(0, 0, 0, 0)
        control_button_layout.addWidget(connection_port_combo)
        control_button_layout.addWidget(port_device_text)
        control_button_layout.addWidget(connection_button)

        command_line_layout = QHBoxLayout()
        command_line_layout.setContentsMargins(0, 0, 0, 0)
        command_line_layout.addWidget(command_line)
        command_line_layout.addWidget(send_button)
        command_line_layout.addWidget(clear_data_button)

        terminal_part_layout = QVBoxLayout()
        terminal_part_layout.addLayout(control_button_layout)
        terminal_part_layout.addWidget(self.terminal_display)
        terminal_part_layout.addLayout(command_line_layout)

        # Event Callback Setup
        def update_connect_button(set_on: bool):
            # Update the connection button text based on the connection status
            if set_on:
                connection_button.setText('Disconnect')
            else:
                connection_button.setText('Connect')

        def clear_data():
            # Clear the terminal display
            self.terminal_display.clear()

        # Connections setup
        def command_line_send_msg():
            # Send the message from the command line
            msg = command_line.text()
            self.send_msg(msg)
            command_line.clear()

        def connection_button_clicked():
            # Handle the connection button click event
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
        connection_button.clicked.connect(connection_button_clicked)
        clear_data_button.clicked.connect(clear_data)
        self.terminal_widget.setLayout(terminal_part_layout)

    def setup_plotting_tab(self):
        main_splitter = QSplitter(Qt.Vertical)

        # Chart Display Section
        self.chart_list = ChartList(self.plotting_tab, [{'name': 'temp'}])

        chart_layout = QGridLayout()

        chart_layout.addWidget(self.chart_list, 1, 0, 1, 6)
        chart_container = QWidget()
        chart_container.setLayout(chart_layout)

        main_splitter.addWidget(chart_container)

        plotting_layout = QVBoxLayout()
        plotting_layout.setContentsMargins(0, 0, 0, 0)  # each section has its own margin
        plotting_layout.addWidget(main_splitter)

        self.plotting_tab.setLayout(plotting_layout)

    def process_feedback(self, feedback: bytes):
        # Process received feedback from the device
        self.received_data += feedback.decode(encoding='utf-8')
        if '\n' in self.received_data:
            fine_data, self.received_data = self.received_data.rsplit('\n', 1)
            lines = fine_data.split('\n')
            for line in lines:
                tokens = line.split(",")
                if not tokens:
                    continue
                elif tokens[0] == '!fb':
                    self.chart_list.update_chart(tokens[2:])
                else:
                    self.update_terminal_display(line + '\n')

    def update_terminal_display(self, input_str: str):
        # Update the terminal display with new input
        cursor = self.terminal_display.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(input_str)
        self.terminal_display.setTextCursor(cursor)

    def send_msg(self, msg):
        # Send a message to the device
        try:
            self.communicate_manager.SendData(bytes(msg + '\r\n', encoding='utf-8'))
        except Exception as err:
            print(err)
            msg = 'Fail to send message!'
        self.update_terminal_display(msg + '\n')

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create a QApplication instance
    demo = Meta_UI()  # Instantiate the main window
    demo.show()  # Show the main window
    sys.exit(app.exec_())  # Execute the application's event loop
