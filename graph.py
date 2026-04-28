import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtGui import QFont
 
class Coordinatograph(QWidget):
    def __init__(self):
        super(Coordinatograph, self).__init__()
        pg.setConfigOptions(leftButtonPan=False)
        pg.setConfigOption('background', '#1e1e1e') 
        pg.setConfigOption('foreground', '#d3d3d3') 
        
        # --- Create Two Separate Plot Widgets ---
        self.pw_angle = pg.PlotWidget()
        self.pw_vel = pg.PlotWidget()
        
        # LINK THEIR X-AXES! Zooming one zooms the other automatically.
        self.pw_vel.setXLink(self.pw_angle)
        
        # Setup Styles
        labelStyle = {'color': '#d3d3d3', 'font-size': '11pt', 'bold': True}
        tick_font = QFont(); tick_font.setPointSize(10)
        
        # Format Angle Plot (Top)
        self.pw_angle.setTitle("A2V (Outer Loop: Angle)", color='#d3d3d3', size='11pt', bold=True)
        self.pw_angle.getAxis('left').setLabel('Degrees', **labelStyle)
        self.pw_angle.getAxis('left').setTickFont(tick_font)
        self.pw_angle.getAxis('bottom').setTickFont(tick_font)
        
        # Format Velocity Plot (Bottom)
        self.pw_vel.setTitle("V2I (Inner Loop: Velocity)", color='#d3d3d3', size='11pt', bold=True)
        self.pw_vel.getAxis('left').setLabel('Deg / Sec', **labelStyle)
        self.pw_vel.getAxis('bottom').setLabel('Time (s)', **labelStyle)
        self.pw_vel.getAxis('left').setTickFont(tick_font)
        self.pw_vel.getAxis('bottom').setTickFont(tick_font)

        # MATLAB Colors
        pen_target = pg.mkPen(color='#D95319', width=1.5) # Orange
        pen_actual = pg.mkPen(color='#0072BD', width=1.5) # Blue

        # Data Curves
        self.curve_t_a = self.pw_angle.plot(pen=pen_target)
        self.curve_a_a = self.pw_angle.plot(pen=pen_actual)
        self.curve_t_v = self.pw_vel.plot(pen=pen_target)
        self.curve_a_v = self.pw_vel.plot(pen=pen_actual)

        # Arrays
        self.arr_t_a = np.zeros(1000, dtype=np.float32)
        self.arr_a_a = np.zeros(1000, dtype=np.float32)
        self.arr_t_v = np.zeros(1000, dtype=np.float32)
        self.arr_a_v = np.zeros(1000, dtype=np.float32)
        self.x_axis = np.linspace(0, 10, 1000, endpoint=False)
        self.pause = False
 
        # Stack them vertically
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self.pw_angle)
        self.v_layout.addWidget(self.pw_vel)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.v_layout)
 
    def pause_plot(self): self.pause = True
    def start_plot(self): self.pause = False

    def update_value(self, t_a, a_a, t_v, a_v):
        if self.pause: return
        
        self.arr_t_a = np.append(self.arr_t_a[1:], t_a)
        self.arr_a_a = np.append(self.arr_a_a[1:], a_a)
        self.arr_t_v = np.append(self.arr_t_v[1:], t_v)
        self.arr_a_v = np.append(self.arr_a_v[1:], a_v)
        
        self.curve_t_a.setData(self.x_axis, self.arr_t_a)
        self.curve_a_a.setData(self.x_axis, self.arr_a_a)
        self.curve_t_v.setData(self.x_axis, self.arr_t_v)
        self.curve_a_v.setData(self.x_axis, self.arr_a_v)