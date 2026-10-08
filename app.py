import sys  # Make sure sys is imported FIRST!
import os
import collections
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget
)
from PyQt6.QtCore import QTimer, Qt, QRectF
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPen
import pyqtgraph as pg

# Absolute path routing trick to bundle assets inside a compiled Linux binary safely
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(bundle_dir, "icon.png")

# Pull from your verified hardware_api backend lab script
from hardware_api import LaptopHardwareAPI
import sys
import collections
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QComboBox, QPushButton, QTabWidget
)
from PyQt6.QtCore import QTimer, Qt, QRectF
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPen
import pyqtgraph as pg

# Import your rock-solid, fully certified backend api module
from hardware_api import LaptopHardwareAPI

# =============================================================================
# UPGRADED STABLE COMPONENT: CIRCULAR PROGRESS GAUGE WITH CENTER METRIC TEXT
# =============================================================================
class CircularProgressRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0            # Active normalized scale (0 to 100)
        self.display_mhz = 800    # Raw live core clock frequency
        self.ring_color = "#007AFF" # Google Premium Electric Blue Accent
        self.setFixedSize(160, 160)

    def update_gauge_state(self, percentage, raw_mhz):
        """Updates internal numeric matrices and forces a safe canvas repaint."""
        self.value = max(0, min(100, percentage))
        self.display_mhz = raw_mhz
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing) # Max edge smoothing
        
        # Calculate rendering boundary box geometry inside padding limits
        rect = QRectF(12, 12, self.width() - 24, self.height() - 24)
        
        # 1. Paint the subtle background structural backing track ring line
        bg_pen = QPen(QColor("#1F1F24"), 11, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)
        
        # 2. Convert standard 0-100% metrics over to circular tracking degrees
        start_angle = 90 * 16
        span_angle = int(-self.value * 3.6 * 16)
        
        # 3. Paint the active colored performance indicator arc layer
        active_pen = QPen(QColor(self.ring_color), 11, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(active_pen)
        painter.drawArc(rect, start_angle, span_angle)
        
        # 4. Typography positioning math to render alphanumeric tags dead center
        painter.setPen(QColor("#FFFFFF"))
        
        # Draw the main live clock value string
        font_num = QFont("Ubuntu", 18, QFont.Weight.Bold)
        painter.setFont(font_num)
        text_num = f"{self.display_mhz}"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text_num)
        
        # Draw the secondary tracking unit label offset below the digits
        font_unit = QFont("Ubuntu", 9, QFont.Weight.Bold)
        painter.setFont(font_unit)
        painter.setPen(QColor("#6C6C78"))
        unit_rect = rect.adjusted(0, 36, 0, 0)
        painter.drawText(unit_rect, Qt.AlignmentFlag.AlignCenter, "MHz")
# =============================================================================
# MAIN SYSTEM APPLICATION WINDOW CONTROLLER
# =============================================================================
class TabbedHardwareCommander(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = LaptopHardwareAPI()
        
        # Configure High-End App Framework Geometry
        self.setWindowTitle("Elite Hardware Commander Pro")
        self.setFixedSize(500, 760)
        self.setStyleSheet("background-color: #0E0E10;") # Velvet obsidian canvas tone

        # Moving Historical Graph Profile Data Buffers
        self.max_datapoints = 40
        self.cpu_history = collections.deque(maxlen=self.max_datapoints)
        self.gpu_history = collections.deque(maxlen=self.max_datapoints)
        for _ in range(self.max_datapoints):
            self.cpu_history.append(0)
            self.gpu_history.append(0)
        self.timeline_x = list(range(self.max_datapoints))

        # Core Interface Structural Layout Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # App Identity Window Header Display Row
        header_layout = QHBoxLayout()
        header = QLabel("Latitude 5401")
        header.setFont(QFont("Ubuntu", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #FFFFFF; font-weight: 800; letter-spacing: -0.5px;")
        
        sub_badge = QLabel("PRODUCTION v1.0")
        sub_badge.setFont(QFont("Ubuntu", 8, QFont.Weight.Bold))
        sub_badge.setStyleSheet("color: #007AFF; background-color: #1A2F4C; padding: 4px 8px; border-radius: 6px; font-weight: bold;")
        
        header_layout.addWidget(header)
        header_layout.addWidget(sub_badge)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Master System Navigation Tab Control Bar
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::panel { background-color: transparent; border: none; }
            QTabBar::tab {
                background-color: #141416; color: #6C6C78; font-weight: bold; font-size: 11px;
                padding: 10px 16px; border-radius: 8px; margin-right: 6px; border: 1px solid #222226;
            }
            QTabBar::tab:selected { background-color: #1A1A1E; color: #FFFFFF; border: 1px solid #3A3A42; }
            QTabBar::tab:hover:!selected { background-color: #18181A; color: #A0A0AA; }
        """)
        main_layout.addWidget(self.tabs)

        # Allocate structural page view panel layers
        self.tab_cpu = QWidget()
        self.tab_gpu = QWidget()
        self.tab_fan = QWidget()
        # ---------------------------------------------------------------------
        # TAB 1 SETUP: CPU CORE WORKSPACE INTERFACE
        # ---------------------------------------------------------------------
        cpu_layout = QVBoxLayout(self.tab_cpu)
        cpu_layout.setContentsMargins(0, 16, 0, 0)
        cpu_layout.setSpacing(14)

        # 1. Circular Vector Gauge Housing Container
        gauge_container = QWidget()
        gauge_container.setStyleSheet("background-color: #141416; border-radius: 14px; border: 1px solid #222226;")
        gauge_layout = QVBoxLayout(gauge_container)
        gauge_layout.setContentsMargins(16, 20, 16, 20)
        
        self.cpu_circular_gauge = CircularProgressRing()
        gauge_layout.addWidget(self.cpu_circular_gauge, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.cpu_gauge_text = QLabel("Clock Scale: --%")
        self.cpu_gauge_text.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        self.cpu_gauge_text.setStyleSheet("color: #888892; border: none; margin-top: 8px;")
        gauge_layout.addWidget(self.cpu_gauge_text, alignment=Qt.AlignmentFlag.AlignCenter)
        cpu_layout.addWidget(gauge_container)

        # 2. Temperature & Frequency Data Pods
        cpu_metrics_box = QHBoxLayout()
        self.cpu_card_temp, self.cpu_temp_lbl, self.cpu_sub_clock = self.create_ui_metric_pod("CPU CORE THERMAL", "#FF4757", "Clock: -- MHz")
        cpu_metrics_box.addWidget(self.cpu_card_temp)
        cpu_layout.addLayout(cpu_metrics_box)

        # 3. PolicyKit Wrapped Core Controls Card
        cpu_ctrl_card = QWidget()
        cpu_ctrl_card.setStyleSheet("background-color: #141416; border-radius: 14px; border: 1px solid #222226; padding: 14px;")
        cpu_ctrl_layout = QVBoxLayout(cpu_ctrl_card)
        cpu_ctrl_layout.setSpacing(12)
        
        gov_box = QHBoxLayout()
        gov_lbl = QLabel("Performance Profile")
        gov_lbl.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        gov_lbl.setStyleSheet("color: #E2E2E2; border: none;")
        self.gov_select = QComboBox()
        self.gov_select.addItems(["powersave", "performance"])
        current_governor = self.api.get_current_governor()
        if current_governor in ["powersave", "performance"]:
            self.gov_select.setCurrentText(current_governor)
        else:
            self.gov_select.setCurrentIndex(0)
        self.gov_select.setStyleSheet("QComboBox { background-color: #202024; color: white; border: 1px solid #323238; border-radius: 8px; padding: 6px 12px; font-weight: bold; } QComboBox::drop-down { width: 0px; border: none; }")
        self.gov_select.currentIndexChanged.connect(self.handle_governor_switch)
        gov_box.addWidget(gov_lbl)
        gov_box.addStretch()
        gov_box.addWidget(self.gov_select)
        cpu_ctrl_layout.addLayout(gov_box)

        turbo_box = QHBoxLayout()
        turbo_lbl_sec = QVBoxLayout()
        turbo_title = QLabel("Intel Turbo Boost")
        turbo_title.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        turbo_title.setStyleSheet("color: #E2E2E2; border: none;")
        turbo_desc = QLabel("Dynamic Core Performance Boost Acceleration")
        turbo_desc.setStyleSheet("color: #6C6C78; font-size: 11px; border: none;")
        turbo_lbl_sec.addWidget(turbo_title)
        turbo_lbl_sec.addWidget(turbo_desc)
        self.turbo_btn = QPushButton()
        self.turbo_btn.setFixedSize(110, 34)
        self.turbo_btn.clicked.connect(self.handle_turbo_toggle)
        turbo_box.addLayout(turbo_lbl_sec)
        turbo_box.addStretch()
        turbo_box.addWidget(self.turbo_btn)
        cpu_ctrl_layout.addLayout(turbo_box)
        cpu_layout.addWidget(cpu_ctrl_card)
        # ---------------------------------------------------------------------
        # TAB 2 SETUP: NVIDIA MX150 DISCRETE GRAPHICS WORKSPACE
        # ---------------------------------------------------------------------
        gpu_layout = QVBoxLayout(self.tab_gpu)
        gpu_layout.setContentsMargins(0, 16, 0, 0)
        gpu_layout.setSpacing(14)

        # 1. Thermal Metric Pod Card Row
        gpu_metrics_box = QHBoxLayout()
        self.gpu_card_temp, self.gpu_temp_lbl, self.gpu_sub_load = self.create_ui_metric_pod("NVIDIA CORE THERMAL", "#2ED573", "Load: --%")
        gpu_metrics_box.addWidget(self.gpu_card_temp)
        gpu_layout.addLayout(gpu_metrics_box)

        # 2. VRAM Performance Matrix Utilization Container Card
        gpu_vram_card = QWidget()
        gpu_vram_card.setStyleSheet("background-color: #141416; border-radius: 14px; border: 1px solid #222226; padding: 16px;")
        vram_layout = QVBoxLayout(gpu_vram_card)
        
        vram_title = QLabel("Video Memory Allocation (VRAM)")
        vram_title.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        vram_title.setStyleSheet("color: #E2E2E2;")
        
        self.vram_lbl_value = QLabel("Allocated: -- MB / 2048 MB")
        self.vram_lbl_value.setFont(QFont("Ubuntu", 14, QFont.Weight.Bold))
        self.vram_lbl_value.setStyleSheet("color: #FFFFFF; margin-top: 4px;")
        
        vram_layout.addWidget(vram_title)
        vram_layout.addWidget(self.vram_lbl_value)
        gpu_layout.addWidget(gpu_vram_card)
        
        gpu_layout.addStretch()
        # ---------------------------------------------------------------------
        # TAB 3 SETUP: COOLING, POWER & OPTION C EXPANSION WORKSPACE
        # ---------------------------------------------------------------------
        fan_layout = QVBoxLayout(self.tab_fan)
        fan_layout.setContentsMargins(0, 16, 0, 0)
        fan_layout.setSpacing(14)

        # 1. Row 1: Fan RPM and Battery Storage Modules
        fan_row_one = QHBoxLayout()
        self.fan_card_rpm, self.fan_lbl_val, self.fan_sub_desc = self.create_ui_metric_pod("DELL COOLING VELOCITY", "#00D2D3", "Telemetry Active")
        self.bat_card_stat, self.bat_lbl_val, self.bat_sub_desc = self.create_ui_metric_pod("BATTERY UNIT", "#FF9F43", "Status: Unknown")
        fan_row_one.addWidget(self.fan_card_rpm)
        fan_row_one.addWidget(self.bat_card_stat)
        fan_layout.addLayout(fan_row_one)

        # 2. Row 2: Brand New Option C RAM and NVMe Thermal Display Modules
        fan_row_two = QHBoxLayout()
        self.ram_card, self.ram_lbl_val, self.ram_sub_desc = self.create_ui_metric_pod("SYSTEM RAM MEMORY", "#A55EEA", "Allocated: -- GB")
        self.ssd_card, self.ssd_lbl_val, self.ssd_sub_desc = self.create_ui_metric_pod("NVMe SSD TEMPERATURE", "#FA8231", "Storage Plane")
        fan_row_two.addWidget(self.ram_card)
        fan_row_two.addWidget(self.ssd_card)
        fan_layout.addLayout(fan_row_two)

        # 3. Dynamic Thermal Rules Summary Card
        fan_info_card = QWidget()
        fan_info_card.setStyleSheet("background-color: #141416; border-radius: 14px; border: 1px solid #222226; padding: 14px;")
        info_layout = QVBoxLayout(fan_info_card)
        info_title = QLabel("Cooling Loop Rules")
        info_title.setFont(QFont("Ubuntu", 11, QFont.Weight.Bold))
        info_title.setStyleSheet("color: #E2E2E2;")
        info_text = QLabel("The mechanical cooling array behaves strictly under the internal dynamic hardware rule tables managed directly by your Dell system BIOS layers.")
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #6C6C78; font-size: 11px; margin-top: 2px; line-height: 14px;")
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        fan_layout.addWidget(fan_info_card)
        fan_layout.addStretch()

        # Mount Finished Tab Panel Modules to the Navigator View Deck
        self.tabs.addTab(self.tab_cpu, "CPU CONTROL")
        self.tabs.addTab(self.tab_gpu, "NVIDIA GPU")
        self.tabs.addTab(self.tab_fan, "COOLING / POWER")
        # ---------------------------------------------------------------------
        # HISTORICAL TIMELINE GRAPH FOOTER COMPONENT
        # ---------------------------------------------------------------------
        self.graph_view = pg.PlotWidget()
        self.graph_view.setBackground('#141416')
        self.graph_view.setMouseEnabled(x=False, y=False)
        self.graph_view.hideAxis('bottom')
        self.graph_view.setStyleSheet("border-radius: 12px; border: 1px solid #222226;")
        self.graph_view.setFixedHeight(120)
        self.cpu_curve = self.graph_view.plot(pen=pg.mkPen(color='#FF4757', width=2.5))
        self.gpu_curve = self.graph_view.plot(pen=pg.mkPen(color='#2ED573', width=2.5))
        self.graph_view.setYRange(0, 100)
        main_layout.addWidget(self.graph_view)

        self.sync_turbo_button_ui(self.api.is_turbo_enabled())

        # Update Cycle Lifespans Background Thread Loop
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.refresh_dashboard_loop)
        self.ui_timer.start(1000)
        self.refresh_dashboard_loop()

    def create_ui_metric_pod(self, title_text, theme_color, sub_text_default):
        """Generates modular dark layout content cells across separate panes."""
        card = QWidget()
        card.setStyleSheet("background-color: #141416; border: 1px solid #222226; border-radius: 14px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        title = QLabel(title_text)
        title.setFont(QFont("Ubuntu", 8, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {theme_color}; letter-spacing: 0.8px; border: none;")
        value = QLabel("--")
        value.setFont(QFont("Ubuntu", 24, QFont.Weight.Bold))
        value.setStyleSheet("color: #FFFFFF; font-weight: 800; border: none; margin-top: 2px;")
        sub_info = QLabel(sub_text_default)
        sub_info.setFont(QFont("Ubuntu", 10))
        sub_info.setStyleSheet("color: #6C6C78; border: none; margin-top: 1px;")
        layout.addWidget(title)
        layout.addWidget(value)
        layout.addWidget(sub_info)
        return card, value, sub_info

    def sync_turbo_button_ui(self, is_on):
        if is_on:
            self.turbo_btn.setText("BOOST ACTIVE")
            self.turbo_btn.setStyleSheet("QPushButton { background-color: #007AFF; color: white; border-radius: 8px; font-weight: bold; border: none; font-size: 11px; }")
        else:
            self.turbo_btn.setText("BOOST MUTED")
            self.turbo_btn.setStyleSheet("QPushButton { background-color: #202024; color: #6C6C78; border-radius: 8px; font-weight: bold; border: 1px solid #323238; font-size: 11px; }")

    def refresh_dashboard_loop(self):
        """Pulls information from backend nodes and pipes them straight to visual elements."""
        cpu_temp = self.api.get_cpu_temperature()
        cpu_freq = self.api.get_cpu_frequency()
        cpu_scale = self.api.get_cpu_clock_percentage()
        
        gpu = self.api.get_gpu_telemetry()
        bat = self.api.get_battery_telemetry()
        fan_rpm = self.api.get_dell_fan_speed()
        ram = self.api.get_ram_utilization()
        ssd_temp = self.api.get_storage_temperature()

        # 1. Synchronize Tab 1 CPU Metrics (Circular Gauge + Details)
        self.cpu_circular_gauge.update_gauge_state(cpu_scale, cpu_freq)
        self.cpu_gauge_text.setText(f"Clock Scale: {cpu_scale}%")
        self.cpu_temp_lbl.setText(f"{cpu_temp}°C" if cpu_temp > 0 else "N/A")
        self.cpu_sub_clock.setText(f"Core Clock Speed: {cpu_freq} MHz")

        # 2. Synchronize Tab 2 Nvidia Hybrid GPU Performance Readouts
        if gpu["status"] == "Active":
            self.gpu_temp_lbl.setText(f"{gpu['temp']}°C")
            self.gpu_sub_load.setText(f"Core Activity Load: {gpu['utilization']}%")
            self.vram_lbl_value.setText(f"Allocated VRAM: {gpu['vram_used']} MB / {gpu['vram_total']} MB")
        else:
            self.gpu_temp_lbl.setText("IDLE")
            self.gpu_sub_load.setText("MX150 Suspended / Sleeping")
            self.vram_lbl_value.setText("Allocated VRAM: 0 MB / 2048 MB")

        # 3. Synchronize Tab 3 Mechanical Cooling & Expanded Option C Values
        self.fan_lbl_val.setText(f"{fan_rpm} RPM" if fan_rpm > 0 else "0 RPM")
        self.fan_sub_desc.setText("BIOS Automatic Control" if fan_rpm > 0 else "Fan Silenced / Resting")
        
        self.bat_lbl_val.setText(f"{bat['percentage']}%")
        self.bat_sub_desc.setText(f"Status: {bat['status']}")
        
        self.ram_lbl_val.setText(f"{ram['percentage']}%")
        self.ram_sub_desc.setText(f"Allocated: {ram['used_gb']} GB / {ram['total_gb']} GB")
        
        self.ssd_lbl_val.setText(f"{ssd_temp}°C")
        self.ssd_sub_desc.setText("NVMe Device Target")

        # 4. Stream data coordinates onto historical bottom timeline curves
        self.cpu_history.append(cpu_temp)
        self.gpu_history.append(gpu["temp"])
        self.cpu_curve.setData(self.timeline_x, list(self.cpu_history))
        self.gpu_curve.setData(self.timeline_x, list(self.gpu_history))

    def handle_governor_switch(self, _index=None):
        """Apply the selected CPU performance profile to the backend."""
        governor = self.gov_select.currentText().strip().lower()
        if governor:
            self.api.set_cpu_governor(governor)

    def handle_turbo_toggle(self):
        new_state = not self.api.is_turbo_enabled()
        if self.api.set_turbo_boost(new_state):
            self.sync_turbo_button_ui(new_state)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    commander = TabbedHardwareCommander()
    commander.show()
    sys.exit(app.exec())