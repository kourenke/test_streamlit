import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                           QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QGroupBox, QTabWidget, QTextEdit, QComboBox, QFrame,
                           QScrollArea, QSizePolicy)  # 添加滚动条支持
from PyQt5.QtGui import QDoubleValidator, QFont
from PyQt5.QtCore import Qt
from scipy.integrate import quad
from matplotlib import rcParams
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']  # 设置中文字体列表

class AircraftRadiationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("飞机红外辐射特性分析系统")
        self.setGeometry(100, 100, 1280, 900)  # 增加高度以适应新内容
        
        # 应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
            }
            QTabWidget::pane {
                border: 1px solid #3F3F46;
                background: #2D2D30;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #252526;
                color: #DCDCDC;
                padding: 8px 20px;
                border: 1px solid #3F3F46;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #1E1E1E;
                border-bottom: 2px solid #0078D7;
            }
            QGroupBox {
                border: 1px solid #3F3F46;
                border-radius: 5px;
                margin-top: 1.5em;
                padding-top: 10px;
                color: #DCDCDC;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #DCDCDC;
            }
            QPushButton {
                background-color: #3E3E40;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                padding: 5px 15px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0078D7;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #1E1E1E;
                color: #DCDCDC;
                border: 1px solid #3F3F46;
                padding: 5px;
                border-radius: 4px;
            }
            QTextEdit {
                font-family: Consolas, Courier New;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E1E1E;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3E3E40;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 创建主滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)
        
        # 创建主内容部件
        self.main_widget = QWidget()
        self.scroll_area.setWidget(self.main_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建主选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建主分析选项卡
        self.create_main_tab()
        
        # 添加其他选项卡（预留）
        self.add_placeholder_tabs()
    
    def add_placeholder_tabs(self):
        """添加占位选项卡"""
        # 数据管理选项卡
        data_tab = QWidget()
        data_layout = QVBoxLayout()
        placeholder = QLabel("数据管理功能开发中...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 24px; color: #AAAAAA;")
        data_layout.addWidget(placeholder)
        data_tab.setLayout(data_layout)
        self.tab_widget.addTab(data_tab, "数据管理")
        
        # 报告生成选项卡
        report_tab = QWidget()
        report_layout = QVBoxLayout()
        placeholder = QLabel("报告生成功能开发中...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 24px; color: #AAAAAA;")
        report_layout.addWidget(placeholder)
        report_tab.setLayout(report_layout)
        self.tab_widget.addTab(report_tab, "报告生成")
        
        # 系统设置选项卡
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        placeholder = QLabel("系统设置功能开发中...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("font-size: 24px; color: #AAAAAA;")
        settings_layout.addWidget(placeholder)
        settings_tab.setLayout(settings_layout)
        self.tab_widget.addTab(settings_tab, "系统设置")
    
    def create_main_tab(self):
        """创建主分析选项卡"""
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("目标红外辐射特性仿真评估")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建参数区域
        self.create_parameters_section(main_layout)
        
        # 创建绘图区域
        self.create_plot_sections(main_layout)
        
        # 创建结果区域
        self.create_results_section(main_layout)
        
        # 创建作用距离区域
        self.create_range_section(main_layout)
        
        # 添加底部按钮
        self.create_bottom_buttons(main_layout)
        
        self.tab_widget.addTab(main_tab, "目标红外辐射特性仿真评估")
        self.set_default_values()
    
    def create_range_section(self, layout):
        """创建作用距离区域 - 修改为双图布局"""
        # 作用距离分组
        range_group = QGroupBox("作用距离包线")
        range_layout = QVBoxLayout(range_group)
        
        # 创建双图布局
        fig_layout = QHBoxLayout()
        
        # 创建水平方向作用距离图
        self.fig_horizontal_range = plt.figure()
        self.canvas_horizontal_range = FigureCanvas(self.fig_horizontal_range)
        self.canvas_horizontal_range.setMinimumHeight(300)
        fig_layout.addWidget(self.canvas_horizontal_range)
        
        # 创建垂直方向作用距离图
        self.fig_vertical_range = plt.figure()
        self.canvas_vertical_range = FigureCanvas(self.fig_vertical_range)
        self.canvas_vertical_range.setMinimumHeight(300)
        fig_layout.addWidget(self.canvas_vertical_range)
        
        # 连接鼠标移动事件
        self.canvas_horizontal_range.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event, 'horizontal'))
        self.canvas_vertical_range.mpl_connect('motion_notify_event', lambda event: self.on_mouse_move(event, 'vertical'))
        
        self.current_angle_label = QLabel("鼠标悬停查看角度详情")
        self.current_angle_label.setStyleSheet("color: #DCDCDC; font-size: 10px;")
        self.current_angle_label.setAlignment(Qt.AlignCenter)
        
        range_layout.addLayout(fig_layout)
        range_layout.addWidget(self.current_angle_label)
        
        # 添加计算按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_calc_range = QPushButton("计算作用距离包线")
        self.btn_calc_range.clicked.connect(self.calc_range)
        btn_layout.addWidget(self.btn_calc_range)
        btn_layout.addStretch()
        range_layout.addLayout(btn_layout)
        
        layout.addWidget(range_group)
    
    def create_bottom_buttons(self, layout):
        """创建底部按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 计算按钮
        self.btn_calculate = QPushButton("计算辐射特性")
        self.btn_calculate.setFixedHeight(40)
        self.btn_calculate.setStyleSheet("font-weight: bold; background-color: #0078D7;")
        self.btn_calculate.clicked.connect(self.calculate_all)
        button_layout.addWidget(self.btn_calculate)
        
        # 导出按钮
        btn_export = QPushButton("导出结果")
        btn_export.setFixedHeight(40)
        btn_export.setStyleSheet("background-color: #388E3C;")
        button_layout.addWidget(btn_export)
        
        # 关闭按钮
        btn_close = QPushButton("关闭")
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet("background-color: #D32F2F;")
        btn_close.clicked.connect(self.close)
        button_layout.addWidget(btn_close)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def calculate_all(self):
        """执行所有计算"""
        self.plot_horizontal()
        self.plot_vertical()
        self.calc_horizontal()
        self.calc_vertical()
        self.calc_range()
    
    def create_parameters_section(self, main_layout):
        """创建参数输入区域"""
        # 参数分组
        params_group = QGroupBox("目标参数设置")
        main_layout.addWidget(params_group)
        
        self.params_layout = QGridLayout(params_group)
        self.params_layout.setVerticalSpacing(12)
        self.params_layout.setHorizontalSpacing(15)
        self.params_layout.setColumnMinimumWidth(1, 100)
        self.params_layout.setColumnMinimumWidth(3, 100)
        
        # 第一列参数
        row = 0
        self.add_parameter("Gamma (γ):", "txt_gama", row, 0)
        self.add_parameter("r:", "txt_r", row, 2)
        row += 1
        
        self.add_parameter("S1 (m²):", "txt_s1", row, 0)
        self.add_parameter("S2 (m²):", "txt_s2", row, 2)
        row += 1
        
        self.add_parameter("S3 (m²):", "txt_s3", row, 0)
        self.add_parameter("Rp (m):", "txt_Rp", row, 2)
        row += 1
        
        self.add_parameter("尾焰长度 (lwy):", "txt_lwy", row, 0)
        row += 1
        
        # 波长范围单独处理
        lbl_l1 = QLabel("波长范围 (μm):")
        self.txt_l1 = QLineEdit()
        self.txt_l1.setValidator(QDoubleValidator())
        self.params_layout.addWidget(lbl_l1, row, 0)
        self.params_layout.addWidget(self.txt_l1, row, 1)
        
        lbl_to = QLabel("到")
        self.params_layout.addWidget(lbl_to, row, 2)
        
        self.txt_l2 = QLineEdit()
        self.txt_l2.setValidator(QDoubleValidator())
        self.params_layout.addWidget(self.txt_l2, row, 3)
        
        row += 1
        
        # 第二列参数
        self.add_parameter("高度 H (m):", "txt_H", row, 0)
        self.add_parameter("马赫数 (Ma):", "txt_Ma", row, 2)
        row += 1
        
        lbl_engine = QLabel("发动机类型:")
        self.cmb_engine = QComboBox()
        self.cmb_engine.addItems(["常规模式", "加力模式"])
        self.cmb_engine.setStyleSheet("combobox-popup: 0;")
        self.params_layout.addWidget(lbl_engine, row, 0)
        self.params_layout.addWidget(self.cmb_engine, row, 1)
        
        self.add_parameter("方位角 (deg):", "txt_fw", row, 2)
        row += 1
        
        self.add_parameter("俯仰角 (deg):", "txt_fy", row, 0)
        row += 1
        
        # 辐射参数分组
        radiation_group = QGroupBox("辐射特性参数")
        self.params_layout.addWidget(radiation_group, row, 0, 2, 4)
        radiation_layout = QGridLayout(radiation_group)
        radiation_layout.setVerticalSpacing(10)
        radiation_layout.setHorizontalSpacing(15)
        
        r_row = 0
        self.add_parameter("蒙皮发射率:", "txt_emissivity_skin", r_row, 0, layout=radiation_layout)
        self.add_parameter("喷口发射率:", "txt_emissivity_nozzle", r_row, 2, layout=radiation_layout)
        r_row += 1
        
        self.add_parameter("尾焰发射率:", "txt_emissivity_flame", r_row, 0, layout=radiation_layout)
        self.add_parameter("尾焰基温 (K):", "txt_tw_base", r_row, 2, layout=radiation_layout)
        r_row += 1
        
        self.add_parameter("常规温度 (K):", "txt_tp_normal", r_row, 0, layout=radiation_layout)
        self.add_parameter("加力温度 (K):", "txt_tp_afterburner", r_row, 2, layout=radiation_layout)
        
        # 大气和探测器参数分组
        row += 2
        detector_group = QGroupBox("大气与探测器参数")
        # 增加行数
        self.params_layout.addWidget(detector_group, row, 0, 3, 4)  # 修改为3行
        detector_layout = QGridLayout(detector_group)
        detector_layout.setVerticalSpacing(10)
        detector_layout.setHorizontalSpacing(15)
        
        d_row = 0
        # 添加探测波段选择
        lbl_band = QLabel("探测波段:")
        self.cmb_band = QComboBox()
        self.cmb_band.addItems(["中波 (3-5μm)", "长波 (8-12μm)"])
        detector_layout.addWidget(lbl_band, d_row, 0)
        detector_layout.addWidget(self.cmb_band, d_row, 1)
        
        # 添加气象条件选择
        lbl_weather = QLabel("气象条件:")
        self.cmb_weather = QComboBox()
        self.cmb_weather.addItems(["晴天", "多云", "阴天", "雨天"])
        detector_layout.addWidget(lbl_weather, d_row, 2)
        detector_layout.addWidget(self.cmb_weather, d_row, 3)
        d_row += 1
        
        # 原有参数
        self.add_parameter("探测器孔径 (m):", "txt_detector_aperture", d_row, 0, layout=detector_layout)
        self.add_parameter("信噪比阈值:", "txt_snr_threshold", d_row, 2, layout=detector_layout)
        d_row += 1
        
        # 新增参数
        self.add_parameter("光学系统F数:", "txt_f_number", d_row, 0, layout=detector_layout)
        self.add_parameter("光学透过率:", "txt_optical_trans", d_row, 2, layout=detector_layout)
        d_row += 1
        
        self.add_parameter("NETD (mK):", "txt_netd", d_row, 0, layout=detector_layout)
        self.add_parameter("系统带宽 (Hz):", "txt_system_bandwidth", d_row, 2, layout=detector_layout)
        d_row += 1
        
        self.add_parameter("探测器响应率 (A/W):", "txt_detector_resp", d_row, 0, layout=detector_layout)
        self.add_parameter("比探测率 D* (cm√Hz/W):", "txt_d_star", d_row, 2, layout=detector_layout)
        d_row += 1
        
        self.add_parameter("敏感元尺寸 (μm):", "txt_pixel_size", d_row, 0, layout=detector_layout)
        self.add_parameter("积分时间 (ms):", "txt_integration_time", d_row, 2, layout=detector_layout)
        d_row += 1

        self.add_parameter("背景温度 (K):", "txt_bg_temp", d_row, 0, layout=detector_layout)
    
    def add_parameter(self, label, widget_name, row, col, layout=None):
        """添加参数控件到布局"""
        if layout is None:
            layout = self.params_layout
        
        lbl = QLabel(label)
        widget = QLineEdit()
        widget.setValidator(QDoubleValidator())
        setattr(self, widget_name, widget)
        
        layout.addWidget(lbl, row, col)
        layout.addWidget(widget, row, col + 1)
    
    def create_plot_sections(self, main_layout):
        """创建绘图区域"""
        plot_layout = QHBoxLayout()
        plot_layout.setSpacing(20)
        
        # 水平方向绘图组
        horizontal_group = QGroupBox("水平方向辐射模式")
        horizontal_layout = QVBoxLayout(horizontal_group)
        horizontal_layout.setContentsMargins(10, 15, 10, 10)
        
        self.fig_horizontal = plt.figure()
        self.canvas_horizontal = FigureCanvas(self.fig_horizontal)
        self.canvas_horizontal.setMinimumHeight(300)
        horizontal_layout.addWidget(self.canvas_horizontal)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_plot_horizontal = QPushButton("绘制水平方向")
        btn_plot_horizontal.clicked.connect(self.plot_horizontal)
        btn_layout.addWidget(btn_plot_horizontal)
        btn_layout.addStretch()
        horizontal_layout.addLayout(btn_layout)
        
        plot_layout.addWidget(horizontal_group)
        
        # 垂直方向绘图组
        vertical_group = QGroupBox("垂直方向辐射模式")
        vertical_layout = QVBoxLayout(vertical_group)
        vertical_layout.setContentsMargins(10, 15, 10, 10)
        
        self.fig_vertical = plt.figure()
        self.canvas_vertical = FigureCanvas(self.fig_vertical)
        self.canvas_vertical.setMinimumHeight(300)
        vertical_layout.addWidget(self.canvas_vertical)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_plot_vertical = QPushButton("绘制垂直方向")
        btn_plot_vertical.clicked.connect(self.plot_vertical)
        btn_layout.addWidget(btn_plot_vertical)
        btn_layout.addStretch()
        vertical_layout.addLayout(btn_layout)
        
        plot_layout.addWidget(vertical_group)
        
        main_layout.addLayout(plot_layout)
    
    def create_results_section(self, main_layout):
        """创建结果区域"""
        results_layout = QHBoxLayout()
        results_layout.setSpacing(20)
        
        # 水平方向结果
        horizontal_result_group = QGroupBox("水平方向计算结果")
        horizontal_result_layout = QVBoxLayout(horizontal_result_group)
        horizontal_result_layout.setContentsMargins(10, 15, 10, 10)
        
        lbl_heading = QLabel("在指定方位角下:")
        lbl_heading.setStyleSheet("font-weight: bold;")
        horizontal_result_layout.addWidget(lbl_heading)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_calc_horizontal = QPushButton("计算水平方向")
        btn_calc_horizontal.clicked.connect(self.calc_horizontal)
        btn_layout.addWidget(btn_calc_horizontal)
        btn_layout.addStretch()
        horizontal_result_layout.addLayout(btn_layout)
        
        self.txt_horizontal_result = QTextEdit()
        self.txt_horizontal_result.setReadOnly(True)
        self.txt_horizontal_result.setMinimumHeight(150)
        horizontal_result_layout.addWidget(self.txt_horizontal_result)
        
        results_layout.addWidget(horizontal_result_group)
        
        # 垂直方向结果
        vertical_result_group = QGroupBox("垂直方向计算结果")
        vertical_result_layout = QVBoxLayout(vertical_result_group)
        vertical_result_layout.setContentsMargins(10, 15, 10, 10)

        
        lbl_heading2 = QLabel("在指定俯仰角下:")
        lbl_heading2.setStyleSheet("font-weight: bold;")
        vertical_result_layout.addWidget(lbl_heading2)
        
        btn_layout2 = QHBoxLayout()
        btn_layout2.addStretch()
        btn_calc_vertical = QPushButton("计算垂直方向")
        btn_calc_vertical.clicked.connect(self.calc_vertical)
        btn_layout2.addWidget(btn_calc_vertical)
        btn_layout2.addStretch()
        vertical_result_layout.addLayout(btn_layout2)
        
        self.txt_vertical_result = QTextEdit()
        self.txt_vertical_result.setReadOnly(True)
        self.txt_vertical_result.setMinimumHeight(150)
        vertical_result_layout.addWidget(self.txt_vertical_result)
        
        results_layout.addWidget(vertical_result_group)
        
        main_layout.addLayout(results_layout)
    
    def set_default_values(self):
        """设置默认参数值"""
        self.txt_gama.setText("1.4")
        self.txt_r.setText("0.82")
        self.txt_s1.setText("8.3")
        self.txt_s2.setText("26.61")
        self.txt_s3.setText("96.37")
        self.txt_Rp.setText("1")
        self.txt_lwy.setText("5")
        self.txt_l1.setText("3")
        self.txt_l2.setText("5")
        self.txt_H.setText("12000")
        self.txt_Ma.setText("2")
        self.txt_fw.setText("75")
        self.txt_fy.setText("75")
        
        # 设置辐射参数默认值
        self.txt_emissivity_skin.setText("0.7")
        self.txt_emissivity_nozzle.setText("0.8")
        self.txt_emissivity_flame.setText("0.2")
        self.txt_tw_base.setText("750")
        self.txt_tp_normal.setText("600")
        self.txt_tp_afterburner.setText("1000")
        
        # 设置大气和探测器参数默认值
        self.cmb_band.setCurrentIndex(0)  # 默认为中波
        self.cmb_weather.setCurrentIndex(0)  # 默认为晴天
        self.txt_bg_temp.setText("300")
        self.txt_detector_aperture.setText("0.1")
        self.txt_snr_threshold.setText("5")
        self.txt_f_number.setText("4.0")
        self.txt_optical_trans.setText("0.85")
        self.txt_netd.setText("20")  # 20mK
        self.txt_system_bandwidth.setText("100")
        self.txt_detector_resp.setText("1.0")
        self.txt_d_star.setText("1e10")
        self.txt_pixel_size.setText("15")
        self.txt_integration_time.setText("10")
    
    def get_parameters(self):
        """获取所有参数值"""
        params = {
            'gama': float(self.txt_gama.text()),
            'r': float(self.txt_r.text()),
            's1': float(self.txt_s1.text()),
            's2': float(self.txt_s2.text()),
            's3': float(self.txt_s3.text()),
            'Rp': float(self.txt_Rp.text()),
            'lwy': float(self.txt_lwy.text()),
            'l1': float(self.txt_l1.text()),
            'l2': float(self.txt_l2.text()),
            'H': float(self.txt_H.text()),
            'Ma': float(self.txt_Ma.text()),
            'jl': 1 if self.cmb_engine.currentText() == "加力模式" else 0,
            'fdj': 1 if self.cmb_engine.currentText() == "常规模式" else 2,
            'fwjiaodu': float(self.txt_fw.text()),
            'fyjiaodu': float(self.txt_fy.text()),
            
            # 辐射参数
            'emissivity_skin': float(self.txt_emissivity_skin.text()),
            'emissivity_nozzle': float(self.txt_emissivity_nozzle.text()),
            'emissivity_flame': float(self.txt_emissivity_flame.text()),
            'tw_base': float(self.txt_tw_base.text()),
            'tp_normal': float(self.txt_tp_normal.text()),
            'tp_afterburner': float(self.txt_tp_afterburner.text()),

            # 大气和探测器参数
            'band': self.cmb_band.currentText(),
            'weather': self.cmb_weather.currentText(),
            'bg_temp': float(self.txt_bg_temp.text()),
            'detector_aperture': float(self.txt_detector_aperture.text()),
            'snr_threshold': float(self.txt_snr_threshold.text()),
            'f_number': float(self.txt_f_number.text()),
            'optical_trans': float(self.txt_optical_trans.text()),
            'netd': float(self.txt_netd.text()) / 1000.0,  # 转换为K
            'system_bandwidth': float(self.txt_system_bandwidth.text()),
            'detector_resp': float(self.txt_detector_resp.text()),
            'd_star': float(self.txt_d_star.text()),
            'pixel_size': float(self.txt_pixel_size.text()),
            'integration_time': float(self.txt_integration_time.text())

        }
        return params
    
    def radiation_calculations(self, s_value, angle_mode='horizontal'):
        """执行辐射计算"""
        params = self.get_parameters()
        
        # 物理常数
        c1 = 3.7415e-16
        c2 = 1.438e-2
        s4 = np.pi * params['Rp']**2
        
        # 1. 蒙皮辐射计算
        if params['H'] <= 11000:
            T0 = 288.2 - 0.0065 * params['H']
        elif params['H'] <= 20000:
            T0 = 216.7
        elif params['H'] <= 32000:
            T0 = 216.7 + 0.001 * (params['H'] - 20000)
        else:
            T0 = 216.7
        
        Tm = T0 * (1 + params['r'] * (params['gama'] - 1) / 2 * params['Ma']**2)
        
        def M(x):
            return c1 / x**5 / (np.exp(c2 / (x * Tm)) - 1)
        
        L = params['emissivity_skin'] / np.pi * quad(M, params['l1']/1e6, params['l2']/1e6)[0]
        
        # 2. 发动机喷口辐射
        Tp = params['tp_afterburner'] if params['jl'] == 1 else params['tp_normal']
        
        def Mp(x):
            return c1 / x**5 / (np.exp(c2 / (x * Tp)) - 1)
        
        Lp = params['emissivity_nozzle'] / np.pi * quad(Mp, params['l1']/1e6, params['l2']/1e6)[0]
        
        # 3. 尾焰辐射
        Tw = params['tw_base']
        if params['fdj'] == 1:
            Tw = 0.85 * Tw
        else:
            Tw = 0.9 * Tw
        
        def Mw(x):
            return c1 / x**5 / (np.exp(c2 / (x * Tw)) - 1)
        
        Lw = params['emissivity_flame'] / np.pi * quad(Mw, params['l1']/1e6, params['l2']/1e6)[0]
        
        # 准备角度数据
        myBeta = np.linspace(0, 2*np.pi, 360)
        results = np.zeros_like(myBeta)
        Im_arr = np.zeros_like(myBeta)
        Ip_arr = np.zeros_like(myBeta)
        Iw_arr = np.zeros_like(myBeta)
        
        # 角度分区计算
        for i, beta in enumerate(myBeta):
            if 0 <= beta < np.arctan(1/5):
                z = 0
            elif beta < np.pi/2:
                z = 1
            elif beta < (np.pi - np.arctan(0.2)):
                z = 2
            elif beta < (np.pi + np.arctan(0.2)):
                z = 3
            elif beta < 3*np.pi/2:
                z = 4
            elif beta < (2*np.pi - np.arctan(0.2)):
                z = 5
            else:
                z = 6
                
            s = params['s1'] * np.abs(np.cos(beta)) + s_value * np.abs(np.sin(beta))
            Im = s * L
            Im_arr[i] = Im
            
            # 根据不同区域计算辐射
            if z == 0:
                Sw = 0
                Ip = 0
            elif z == 1:
                Sw = (params['lwy'] * np.sin(beta) - np.cos(beta))**2 / (params['lwy'] * np.sin(beta))
                Ip = 0
            elif z == 2:
                Sw = (params['lwy'] * np.sin(beta) - np.abs(np.cos(beta)))**2 / (params['lwy'] * np.sin(beta)) + s4 * np.abs(np.cos(beta))
                Sp = np.pi * np.abs(np.cos(beta))**2
                Ip = Lp * Sp
            elif z == 3:
                Sw = s4 * np.abs(np.cos(beta))
                Sp = np.pi * np.abs(np.cos(beta))**2
                Ip = Lp * Sp
            elif z == 4:
                Sw = (params['lwy'] * np.abs(np.sin(beta)) - np.abs(np.cos(beta)))**2 / (params['lwy'] * np.abs(np.sin(beta))) + s4 * np.abs(np.cos(beta))
                Sp = np.pi * np.abs(np.cos(beta))**2
                Ip = Lp * Sp
            elif z == 5:
                Sw = (params['lwy'] * np.abs(np.sin(beta)) - np.abs(np.cos(beta)))**2 / (params['lwy'] * np.abs(np.sin(beta)))
                Ip = 0
            else:  # z == 6
                Sw = 0
                Ip = 0
                
            Iw = Lw * Sw
            Iw_arr[i] = Iw
            Ip_arr[i] = Ip
            
            # 总辐射强度
            if z in [2, 3, 4]:
                I = Im + Iw + Ip
            else:
                I = Im + Iw
                
            results[i] = I
            
        return myBeta, results, np.max(results), Im_arr, Iw_arr, Ip_arr
    
    def plot_horizontal(self):
        """绘制水平方向辐射模式"""
        beta, results, max_I, Im_arr, Iw_arr, Ip_arr = self.radiation_calculations(
            s_value=float(self.txt_s2.text()), 
            angle_mode='horizontal'
        )
        
        self.fig_horizontal.clf()
        ax = self.fig_horizontal.add_subplot(111, projection='polar')
        
        # 绘制所有辐射分量
        ax.plot(beta, results, 'r-', linewidth=2, label='总辐射')
        ax.plot(beta, Im_arr, 'b--', label='蒙皮辐射')
        ax.plot(beta, Iw_arr, 'g:', label='尾焰辐射')
        ax.plot(beta, Ip_arr, 'm-.', label='喷口辐射')
        
        ax.set_rlabel_position(22.5)
        ax.grid(True)
        
        # 将图例放在图的右侧
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.15))
        
        # 调整布局
        self.fig_horizontal.tight_layout(rect=[0, 0, 1, 0.95])
        
        self.canvas_horizontal.draw()
        self.txt_horizontal_result.setText(
            f"最大辐射强度: {max_I:.4f} W/sr\n"
            f"蒙皮辐射最大值: {np.max(Im_arr):.4f} W/sr\n"
            f"尾焰辐射最大值: {np.max(Iw_arr):.4f} W/sr\n"
            f"喷口辐射最大值: {np.max(Ip_arr):.4f} W/sr"
        )
    
    def plot_vertical(self):
        """绘制垂直方向辐射模式"""
        beta, results, max_I, Im_arr, Iw_arr, Ip_arr = self.radiation_calculations(
            s_value=float(self.txt_s3.text()), 
            angle_mode='vertical'
        )
        
        self.fig_vertical.clf()
        ax = self.fig_vertical.add_subplot(111, projection='polar')
        
        # 绘制所有辐射分量
        ax.plot(beta, results, 'r-', linewidth=2, label='总辐射')
        ax.plot(beta, Im_arr, 'b--', label='蒙皮辐射')
        ax.plot(beta, Iw_arr, 'g:', label='尾焰辐射')
        ax.plot(beta, Ip_arr, 'm-.', label='喷口辐射')
        
        ax.set_rlabel_position(22.5)
        ax.grid(True)
        
        # 将图例放在图的右侧
        ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1.15))
        
        # 调整布局
        self.fig_vertical.tight_layout(rect=[0, 0, 1, 0.95])
        
        self.canvas_vertical.draw()
        self.txt_vertical_result.setText(
            f"最大辐射强度: {max_I:.4f} W/sr\n"
            f"蒙皮辐射最大值: {np.max(Im_arr):.4f} W/sr\n"
            f"尾焰辐射最大值: {np.max(Iw_arr):.4f} W/sr\n"
            f"喷口辐射最大值: {np.max(Ip_arr):.4f} W/sr"
        )
    
    def calc_horizontal(self):
        """计算指定方位角的辐射"""
        params = self.get_parameters()
        detector_info = (
            f"\n探测器参数:\n"
            f"孔径: {params['detector_aperture']*1000:.1f} mm | F数: {params['f_number']}\n"
            f"光学透过率: {params['optical_trans']} | NETD: {params['netd']*1000:.1f} mK\n"
            f"D*: {params['d_star']:.2e} cm√Hz/W | 积分时间: {params['integration_time']} ms"
        )
        
        # 找到最接近指定角度的索引
        beta = np.linspace(0, 2*np.pi, 360)
        idx = int(round(params['fwjiaodu'] * len(beta) / 360))
        idx = min(idx, len(beta)-1)
        
        _, results, _, Im_arr, Iw_arr, Ip_arr = self.radiation_calculations(
            s_value=float(self.txt_s2.text()), 
            angle_mode='horizontal'
        )
        
        I_total = results[idx]
        I_skin = Im_arr[idx]
        I_flame = Iw_arr[idx]
        I_nozzle = Ip_arr[idx]
        
        # 计算作用距离
        R_range = self.calc_range_at_angle(I_total, params['fwjiaodu'], 'horizontal')
        
        self.txt_horizontal_result.setText(
            f"在方位角 {params['fwjiaodu']}° 的辐射强度:\n\n"
            f"总辐射: {I_total:.6f} W/sr\n"
            f"蒙皮辐射: {I_skin:.6f} W/sr\n"
            f"尾焰辐射: {I_flame:.6f} W/sr\n"
            f"喷口辐射: {I_nozzle:.6f} W/sr\n\n"
            f"作用距离: {R_range:.2f} km" + 
            detector_info
        )
    
    def calc_vertical(self):
        """计算指定俯仰角的辐射"""
        params = self.get_parameters()
        
        # 找到最接近指定角度的索引
        beta = np.linspace(0, 2*np.pi, 360)
        idx = int(round(params['fyjiaodu'] * len(beta) / 360))
        idx = min(idx, len(beta)-1)
        
        _, results, _, Im_arr, Iw_arr, Ip_arr = self.radiation_calculations(
            s_value=float(self.txt_s3.text()), 
            angle_mode='vertical'
        )
        
        I_total = results[idx]
        I_skin = Im_arr[idx]
        I_flame = Iw_arr[idx]
        I_nozzle = Ip_arr[idx]
        
        # 计算作用距离
        R_range = self.calc_range_at_angle(I_total, params['fyjiaodu'], 'vertical')
        
        self.txt_vertical_result.setText(
            f"在俯仰角 {params['fyjiaodu']}° 的辐射强度:\n\n"
            f"总辐射: {I_total:.6f} W/sr\n"
            f"蒙皮辐射: {I_skin:.6f} W/sr\n"
            f"尾焰辐射: {I_flame:.6f} W/sr\n"
            f"喷口辐射: {I_nozzle:.6f} W/sr\n\n"
            f"作用距离: {R_range:.2f} km"
        )
    
    def calc_range_at_angle(self, intensity, angle, angle_type):
        """计算特定角度下的作用距离"""
        params = self.get_parameters()
        
        # 获取高度（转换为km）
        H_km = params['H'] / 1000.0
        
        # 确定波段（中波或长波）
        if "中波" in params['band']:
            # 中波红外大气透过率模型
            # 基础衰减系数 (km⁻¹)
            k_base = 0.2
            
            # 高度修正因子 (高度增加，透过率增加)
            h_factor = np.exp(-H_km / 10.0)  # 10km为特征高度
            
            # 气象条件修正因子
            weather_factors = {
                "晴天": 1.0,
                "多云": 0.8,
                "阴天": 0.6,
                "雨天": 0.2  # 雨天对长波影响更大
            }
            w_factor = weather_factors.get(params['weather'], 1.0)
            
            # 综合衰减系数
            k = k_base * h_factor * w_factor
        else:
            # 长波红外大气透过率模型
            # 基础衰减系数 (km⁻¹)
            k_base = 0.15
            
            # 高度修正因子
            h_factor = np.exp(-H_km / 8.0)  # 8km为特征高度
            
            # 气象条件修正因子
            weather_factors = {
                "晴天": 1.0,
                "多云": 0.8,
                "阴天": 0.6,
                "雨天": 0.2  # 雨天对长波影响更大
            }
            w_factor = weather_factors.get(params['weather'], 1.0)
            
            # 综合衰减系数
            k = k_base * h_factor * w_factor
        
        # 探测器参数
        D = params['detector_aperture']  # 探测器孔径(m)
        SNR_min = params['snr_threshold']  # 最小信噪比
        
        # 光学系统参数
        f_number = params['f_number']  # F数
        τ0 = params['optical_trans']  # 光学透过率
        
        # 探测器性能参数
        NETD = params['netd']  # 噪声等效温差(K)
        Δf = params['system_bandwidth']  # 系统带宽(Hz)
        # D_ratio = params['detector_resp']  # 探测器响应率(A/W)
        D_star = params['d_star']  # 比探测率(cm√Hz/W)
        pixel_size = params['pixel_size'] * 1e-6  # 敏感元尺寸(m)
        # t_int = params['integration_time'] / 1000.0  # 积分时间(s)
        
        # 计算探测器敏感元面积
        A_d = (pixel_size)**2  # m²
        
        # 计算接收面积
        A0 = np.pi * (D/2)**2  # 接收面积(m²)
        
        # 计算dW/dT (温度对辐射的变化率)
        # 使用简化模型：dW/dT ≈ 4σT^3，其中σ是Stefan-Boltzmann常数
        σ = 5.67e-8  # W/m²K⁴⁴
        T_bg = params['bg_temp']  # 背景温度(K) - 假设为300K
        dWdT = 4 * σ * T_bg**3  # W/m²K
        
        try:
            range_netd = np.sqrt(
                (intensity * τ0 * A0 * D_star * np.sqrt(A_d * Δf * 1e4)) /  # 注意单位转换
                (NETD * np.sqrt(4*f_number**2 + 1) * dWdT * SNR_min)
            ) / 1000.0  # 转换为km
            
            R_prev = range_netd
            for _ in range(5):  # 进行5次迭代
                τ_atm = np.exp(-k * R_prev)
                R = np.sqrt(
                    (intensity * τ0 * τ_atm * A0 * D_star * np.sqrt(A_d * Δf * 1e4)) / 
                    (NETD * np.sqrt(4*f_number**2 + 1) * dWdT * SNR_min)
                ) / 1000.0
                R_prev = R  # 更新迭代值
                
        except Exception as e:
            print(f"作用距离计算错误: {e}")
            # 使用简单的经验公式作为后备
            R = np.sqrt(intensity * τ0 * A0 * 1e6) / 1000.0  # km
        
        return R
        
    def calc_range(self):
        """计算作用距离包线 - 同时计算水平和垂直方向"""
        # 获取辐射数据
        beta_h, results_h, _, _, _, _ = self.radiation_calculations(
            s_value=float(self.txt_s2.text()), 
            angle_mode='horizontal'
        )
        
        beta_v, results_v, _, _, _, _ = self.radiation_calculations(
            s_value=float(self.txt_s3.text()), 
            angle_mode='vertical'
        )
        
        # 存储数据用于鼠标交互
        self.range_data = {
            'horizontal': {
                'beta': beta_h,
                'range_values': [],
                'intensities': results_h
            },
            'vertical': {
                'beta': beta_v,
                'range_values': [],
                'intensities': results_v
            }
        }
        
        # 计算各角度对应的作用距离
        for i, intensity in enumerate(results_h):
            self.range_data['horizontal']['range_values'].append(
                self.calc_range_at_angle(intensity, np.degrees(beta_h[i]), 'horizontal')
            )
        
        for i, intensity in enumerate(results_v):
            self.range_data['vertical']['range_values'].append(
                self.calc_range_at_angle(intensity, np.degrees(beta_v[i]), 'vertical')
            )
        
        # 绘制水平方向作用距离图
        self.fig_horizontal_range.clf()
        ax_h = self.fig_horizontal_range.add_subplot(111, projection='polar')
        
        # 绘制作用距离包线
        ax_h.plot(beta_h, self.range_data['horizontal']['range_values'], 'c-', linewidth=2, label='作用距离包线')
        
        # 标记最大作用距离点
        range_values_h = self.range_data['horizontal']['range_values']
        max_range_idx_h = np.argmax(range_values_h)
        max_range_h = range_values_h[max_range_idx_h]
        max_range_angle_h = np.degrees(beta_h[max_range_idx_h])
        ax_h.plot([beta_h[max_range_idx_h]], [max_range_h], 'ro', markersize=8)
        ax_h.annotate(f'最大: {max_range_h:.1f}km', 
                     xy=(beta_h[max_range_idx_h], max_range_h),
                     xytext=(beta_h[max_range_idx_h] + 0.3, max_range_h * 1.1),
                     arrowprops=dict(facecolor='red', shrink=0.05),
                     color='black')
        
        # 设置标题和标签
        ax_h.set_title("水平方向作用距离包线", fontsize=12, pad=15)
        ax_h.set_rlabel_position(22.5)
        ax_h.grid(True)
        ax_h.legend(loc='upper right')
        
        # 添加表格信息
        table_text_h = (
            f"最大作用距离: {max_range_h:.1f} km @ {max_range_angle_h:.1f}°\n"
            f"平均作用距离: {np.mean(range_values_h):.1f} km\n"
            f"最小作用距离: {np.min(range_values_h):.1f} km"
        )
        ax_h.text(0.5, -0.3, table_text_h, transform=ax_h.transAxes, 
                fontsize=10, ha='center', va='top', 
                bbox=dict(boxstyle='round', facecolor='#2D2D30', alpha=0.7, edgecolor='none'))
        
        # 绘制垂直方向作用距离图
        self.fig_vertical_range.clf()
        ax_v = self.fig_vertical_range.add_subplot(111, projection='polar')
        
        # 绘制作用距离包线
        ax_v.plot(beta_v, self.range_data['vertical']['range_values'], 'm-', linewidth=2, label='作用距离包线')
        
        # 标记最大作用距离点
        range_values_v = self.range_data['vertical']['range_values']
        max_range_idx_v = np.argmax(range_values_v)
        max_range_v = range_values_v[max_range_idx_v]
        max_range_angle_v = np.degrees(beta_v[max_range_idx_v])
        ax_v.plot([beta_v[max_range_idx_v]], [max_range_v], 'ro', markersize=8)
        ax_v.annotate(f'最大: {max_range_v:.1f}km', 
                     xy=(beta_v[max_range_idx_v], max_range_v),
                     xytext=(beta_v[max_range_idx_v] + 0.3, max_range_v * 1.1),
                     arrowprops=dict(facecolor='red', shrink=0.05),
                     color='black')
        
        # 设置标题和标签
        ax_v.set_title("垂直方向作用距离包线", fontsize=12, pad=15)
        ax_v.set_rlabel_position(22.5)
        ax_v.grid(True)
        ax_v.legend(loc='upper right')
        
        # 添加表格信息
        table_text_v = (
            f"最大作用距离: {max_range_v:.1f} km @ {max_range_angle_v:.1f}°\n"
            f"平均作用距离: {np.mean(range_values_v):.1f} km\n"
            f"最小作用距离: {np.min(range_values_v):.1f} km"
        )
        ax_v.text(0.5, -0.3, table_text_v, transform=ax_v.transAxes, 
                fontsize=10, ha='center', va='top', 
                bbox=dict(boxstyle='round', facecolor='#2D2D30', alpha=0.7, edgecolor='none'))
        
        self.canvas_horizontal_range.draw()
        self.canvas_vertical_range.draw()
        self.current_angle_label.setText("鼠标悬停查看角度详情")


    def on_mouse_move(self, event, direction):
        """鼠标移动事件处理 - 支持双图"""
        if not event.inaxes or not hasattr(self, 'range_data') or direction not in self.range_data:
            return
            
        # 获取鼠标位置对应的角度和距离
        angle_rad = event.xdata
        r = event.ydata
        
        # 转换为角度
        angle_deg = np.degrees(angle_rad) % 360
        
        # 找到最接近的角度索引
        beta = self.range_data[direction]['beta']
        idx = np.argmin(np.abs(beta - angle_rad))
        
        # 获取该角度的距离和辐射强度
        range_value = self.range_data[direction]['range_values'][idx]
        intensity = self.range_data[direction]['intensities'][idx]
        dir_name = "水平" if direction == 'horizontal' else "垂直"
        
        # 获取当前大气参数
        params = self.get_parameters()
        band = params['band'].split()[0]  # 取第一个词
        weather = params['weather']
        H_km = params['H'] / 1000.0
        
        # 更新标签显示
        self.current_angle_label.setText(
            f"方向: {dir_name} | 角度: {angle_deg:.1f}° | 作用距离: {range_value:.1f} km | "
            f"辐射强度: {intensity:.4f} W/sr | "
            f"波段: {band} | 气象: {weather} | 高度: {H_km:.1f} km"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用字体
    font = QFont("Microsoft YaHei UI", 9)
    app.setFont(font)
    
    window = AircraftRadiationApp()
    window.show()
    sys.exit(app.exec_())