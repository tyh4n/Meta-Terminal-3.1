import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from graph import Coordinatograph

class ChartList(QListWidget):

    def __init__(self, parent: QWidget = None, motor_config: list = None):
        super(ChartList, self).__init__(parent=parent)
        self.name2idx = {}
        if motor_config is not None:
            self.setup_list_rows(motor_config)

    def setup_list_rows(self, motor_config: list):
        self.clear()
        self.name2idx = {}
        for i, motor_dict in enumerate(motor_config):
            chart_row_item = ChartRowItem(self, title=motor_dict['name'])
            self.addItem(chart_row_item)
            self.setItemWidget(chart_row_item, chart_row_item.widget)
            self.name2idx[motor_dict['name']] = i

    def update_tuning_chart(self, target: float, actual: float):
        # We only have one chart for tuning now, so we just update the first item
        if self.count() > 0:
            item = self.item(0)
            item.update_row(target, actual)

class ChartRowItem(QListWidgetItem):

    def __init__(self, parent: QListWidget = None, title: str = 'PID Tuning Telemetry'):
        super(ChartRowItem, self).__init__(parent=parent)
        self.title = QLabel(title)
        self.title.setFixedWidth(100)
        
        # Single large coordinatograph for Target vs Actual
        self.tuning_coord = Coordinatograph(title='Target vs Actual', xLabel='time', xUnit='s', yLabel='value', yUnit='')
        
        widget_layout = QHBoxLayout()
        widget_layout.addWidget(self.title)
        widget_layout.addWidget(self.tuning_coord)
        
        self.widget = QWidget()
        self.widget.setObjectName(title)
        self.widget.setLayout(widget_layout)
        self.widget.setFixedHeight(400) # Made it taller for better viewing
        self.setSizeHint(self.widget.size())

    def update_row(self, target: float, actual: float):
        # graph.py update_value expects (new_data, new_target)
        self.tuning_coord.update_value(actual, target)