import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from graph import Coordinatograph

class ChartList(QWidget):

    def __init__(self, parent: QWidget = None, motor_config: list = None):
        super(ChartList, self).__init__(parent=parent)
        
        # 1. Setup the massive dual-plot (all titles are handled inside Coordinatograph now)
        self.tuning_coord = Coordinatograph()
        
        # Force the graph to aggressively expand vertically and horizontally
        self.tuning_coord.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 2. Layout: Just the Graph with zero margins
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.tuning_coord)
        
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def update_tuning_chart(self, t_a: float, a_a: float, t_v: float, a_v: float):
        # Pipe all four data streams directly to the graph
        self.tuning_coord.update_value(t_a, a_a, t_v, a_v)