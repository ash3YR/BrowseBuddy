import sys
import psutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit, QToolBar, 
                           QAction, QStatusBar, QMessageBox, QLabel, QVBoxLayout, 
                           QWidget, QStyle, QDialog, QPushButton, QHBoxLayout,
                           QProgressBar, QGroupBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, pyqtSlot, QTimer, Qt, QSize
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
from datetime import datetime
import json
import os

# Import utility modules
from utils.content_filter import is_safe_url, profanity
from utils.history_manager import load_history, save_history
from utils.parental_controls import ParentalControlsDialog
from utils.screen_time import ScreenTimeDialog

def load_screen_time():
    """Load screen time data from file."""
    try:
        with open('screen_time.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_screen_time(data):
    """Save screen time data to file."""
    with open('screen_time.json', 'w') as f:
        json.dump(data, f, indent=2)

class SafeWebPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if not is_safe_url(url.toString(), self.parent().parent().safe_mode):
                QMessageBox.warning(None, "Access Denied", 
                    "This website is not safe for children!")
                return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

    def navigate_to_url(self):
        url = self.url_bar.text()
        
        # Add http if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check URL safety before loading
        if is_safe_url(url, self.safe_mode):
            self.browser.setUrl(QUrl(url))
        else:
            QMessageBox.warning(self, "Safety Alert",
                "This website might not be safe for children!")
            self.url_bar.setText('')

class PinDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parental Controls PIN")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        # Load PIN from settings
        self.pin = self.load_pin()
        
        layout = QVBoxLayout()
        
        # PIN input
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter PIN")
        self.pin_input.setEchoMode(QLineEdit.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setAlignment(Qt.AlignCenter)
        self.pin_input.setFont(QFont('Arial', 16))
        layout.addWidget(self.pin_input)
        
        # Error message
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.verify_pin)
        button_layout.addWidget(submit_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Set style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 8px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
    
    def load_pin(self):
        try:
            with open('parental_pin.json', 'r') as f:
                return json.load(f).get('pin', '0000')
        except FileNotFoundError:
            # Default PIN if no file exists
            default_pin = '0000'
            self.save_pin(default_pin)
            return default_pin
    
    def save_pin(self, pin):
        with open('parental_pin.json', 'w') as f:
            json.dump({'pin': pin}, f)
    
    def verify_pin(self):
        entered_pin = self.pin_input.text()
        if entered_pin == self.pin:
            self.accept()
        else:
            self.error_label.setText("Incorrect PIN")
            self.pin_input.clear()

class PerformanceMetricsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Performance Metrics")
        self.setGeometry(200, 200, 400, 500)
        
        # Main layout
        layout = QVBoxLayout()
        
        # System Resources Group
        system_group = QGroupBox("System Resources")
        system_layout = QVBoxLayout()
        
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU Usage:")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        system_layout.addLayout(cpu_layout)
        
        # Memory Usage
        memory_layout = QHBoxLayout()
        memory_label = QLabel("Browser Memory:")
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_bar)
        system_layout.addLayout(memory_layout)
        
        # Memory Details
        self.memory_details = QLabel()
        system_layout.addWidget(self.memory_details)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Network Stats Group
        network_group = QGroupBox("Network Statistics")
        network_layout = QVBoxLayout()
        
        # Data Sent
        sent_layout = QHBoxLayout()
        sent_label = QLabel("Data Sent:")
        self.sent_value = QLabel("0 MB")
        sent_layout.addWidget(sent_label)
        sent_layout.addWidget(self.sent_value)
        network_layout.addLayout(sent_layout)
        
        # Data Received
        received_layout = QHBoxLayout()
        received_label = QLabel("Data Received:")
        self.received_value = QLabel("0 MB")
        received_layout.addWidget(received_label)
        received_layout.addWidget(self.received_value)
        network_layout.addLayout(received_layout)
        
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)
        
        # Browser Stats Group
        browser_group = QGroupBox("Browser Statistics")
        browser_layout = QVBoxLayout()
        
        # Page Load Time
        load_time_layout = QHBoxLayout()
        load_time_label = QLabel("Last Page Load Time:")
        self.load_time_value = QLabel("0 ms")
        load_time_layout.addWidget(load_time_label)
        load_time_layout.addWidget(self.load_time_value)
        browser_layout.addLayout(load_time_layout)
        
        # History Count
        history_layout = QHBoxLayout()
        history_label = QLabel("History Entries:")
        self.history_count = QLabel("0")
        history_layout.addWidget(history_label)
        history_layout.addWidget(self.history_count)
        browser_layout.addLayout(history_layout)
        
        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)
        
        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        
        # Set style
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
            QPushButton {
                padding: 8px;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000)  # Update every second
        
        # Initialize network stats
        self.last_net_io = psutil.net_io_counters()
        self.start_time = datetime.now()
        
        # Get the current process
        self.process = psutil.Process()
    
    def update_metrics(self):
        try:
            # Update CPU and Memory for the browser process
            cpu_percent = int(self.process.cpu_percent())
            memory_info = self.process.memory_info()
            memory_percent = int(self.process.memory_percent())
            
            self.cpu_bar.setValue(cpu_percent)
            self.memory_bar.setValue(memory_percent)
            self.memory_details.setText(f"Used: {memory_info.rss / (1024*1024):.2f} MB")
            
            # Update Network Stats
            current_net_io = psutil.net_io_counters()
            bytes_sent = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / (1024*1024)
            bytes_recv = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / (1024*1024)
            
            self.sent_value.setText(f"{bytes_sent:.2f} MB")
            self.received_value.setText(f"{bytes_recv:.2f} MB")
            
            self.last_net_io = current_net_io
            
            # Update Browser Stats
            if hasattr(self.parent(), 'history'):
                self.history_count.setText(str(len(self.parent().history)))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Handle case where process is no longer accessible
            self.close()

class SafeBrowseJunior(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SafeBrowse Junior - AI Safe Internet Companion')
        self.setGeometry(100, 100, 1024, 768)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: f5f5f5#;
            }
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
                background-color: #ffffff;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
            QStatusBar {
                background-color: #ffffff;
                color: #666666;
                border-top: 1px solid #e0e0e0;
            }
            QLabel {
                color: #666666;
                font-size: 12px;
            }
        """)
        
        # Initialize browsing history and screen time
        self.history = load_history()
        self.screen_time = load_screen_time()
        self.current_site_start_time = None
        self.current_site = None
        
        # Initialize safe mode state
        self.safe_mode = True
        
        # Create main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create the safe web view
        self.browser = QWebEngineView()
        safe_page = SafeWebPage(self.browser)
        self.browser.setPage(safe_page)
        self.browser.setUrl(QUrl('https://www.kiddle.co'))  # Kid-safe search engine
        
        # Create child-friendly toolbar
        self.create_toolbar()
        
        # Add browser to layout
        layout.addWidget(self.browser)
        
        # Setup status bar
        self.setup_status_bar()
        
        # Connect signals
        self.browser.loadFinished.connect(self.on_load_finished)
        self.browser.urlChanged.connect(self.on_url_changed)
        
        # Setup screen time timer
        self.screen_time_timer = QTimer()
        self.screen_time_timer.timeout.connect(self.update_screen_time)
        self.screen_time_timer.start(1000)  # Update every second

    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Add child-friendly navigation buttons with icons
        

        back_btn = QAction(QIcon("browser\resources\icons\back.png"), 'Back', self)

        back_btn.setToolTip('Go Back')
        back_btn.triggered.connect(self.browser.back)
        toolbar.addAction(back_btn)

        forward_btn = QAction(self.style().standardIcon(QStyle.SP_ArrowForward), 'Forward', self)
        forward_btn.setToolTip('Go Forward')
        forward_btn.triggered.connect(self.browser.forward)
        toolbar.addAction(forward_btn)

        home_btn = QAction(self.style().standardIcon(QStyle.SP_ComputerIcon), 'Home', self)
        home_btn.setToolTip('Go Home')
        home_btn.triggered.connect(self.go_home)
        toolbar.addAction(home_btn)

        # Add URL bar with content filtering
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Type a website address')
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setMinimumWidth(400)
        toolbar.addWidget(self.url_bar)

        # Add Parental Controls Button
        parental_controls_btn = QAction(self.style().standardIcon(QStyle.SP_FileDialogDetailedView), 'Parental Controls', self)
        parental_controls_btn.setToolTip('Open Parental Controls')
        parental_controls_btn.triggered.connect(self.open_parental_controls)
        toolbar.addAction(parental_controls_btn)

    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add screen time tracker
        self.time_label = QLabel('Screen Time: 0 minutes')
        self.time_label.setFont(QFont('Arial', 10))
        self.time_label.mousePressEvent = self.show_screen_time_details
        self.status_bar.addPermanentWidget(self.time_label)
        
        # Add safety indicator
        self.safety_indicator = QLabel('🛡️ Safe Mode Active')
        self.safety_indicator.setFont(QFont('Arial', 10))
        self.safety_indicator.mousePressEvent = self.toggle_safe_mode
        self.status_bar.addPermanentWidget(self.safety_indicator)
        
        # Add Performance Metrics Button
        self.metrics_btn = QPushButton('📊')
        self.metrics_btn.setToolTip('Performance Metrics')
        self.metrics_btn.setFlat(True)
        self.metrics_btn.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 2px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-radius: 2px;
            }
        """)
        self.metrics_btn.clicked.connect(self.show_performance_metrics)
        self.status_bar.addPermanentWidget(self.metrics_btn)

    def update_screen_time(self):
        """Update the screen time display and tracking."""
        if self.current_site and self.current_site_start_time:
            current_time = datetime.now()
            time_diff = (current_time - self.current_site_start_time).total_seconds()
            
            # Update the display
            total_minutes = sum(self.screen_time.values()) // 60
            self.time_label.setText(f'Screen Time: {total_minutes} minutes')
            
            # Update the stored time
            self.screen_time[self.current_site] = self.screen_time.get(self.current_site, 0) + 1
            save_screen_time(self.screen_time)

    def show_screen_time_details(self, event):
        """Show the screen time details dialog."""
        dialog = ScreenTimeDialog(self.screen_time, self)
        dialog.exec_()

    def navigate_to_url(self):
        url = self.url_bar.text()
        
        # Add http if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check URL safety before loading
        if is_safe_url(url, self.safe_mode):
            self.browser.setUrl(QUrl(url))
        else:
            QMessageBox.warning(self, "Safety Alert",
                "This website might not be safe for children!")
            self.url_bar.setText('')

    def go_home(self):
        self.browser.setUrl(QUrl('https://www.kiddle.co'))

    @pyqtSlot(bool)
    def on_load_finished(self, ok):
        if ok:
            # Log browsing activity
            self.log_activity()
            
            # Update screen time tracking
            current_url = self.browser.url().toString()
            if current_url != self.current_site:
                self.current_site = current_url
                self.current_site_start_time = datetime.now()

    def log_activity(self):
        activity = {
            'timestamp': datetime.now().isoformat(),
            'url': self.browser.url().toString(),
            'title': self.browser.page().title()
        }
        self.history.append(activity)
        save_history(self.history)

    def on_url_changed(self, url):
        self.url_bar.setText(url.toString())
        # Update screen time tracking for new URL
        self.current_site = url.toString()
        self.current_site_start_time = datetime.now()

    def open_parental_controls(self):
        """Open the parental controls dialog with PIN verification."""
        pin_dialog = PinDialog(self)
        if pin_dialog.exec_() == QDialog.Accepted:
            dialog = ParentalControlsDialog(self.history, self)
            dialog.exec_()

    def show_performance_metrics(self):
        """Show the performance metrics dialog."""
        dialog = PerformanceMetricsDialog(self)
        dialog.exec_()

    def toggle_safe_mode(self, event):
        """Toggle safe mode after PIN verification."""
        if self.safe_mode:
            # Only ask for PIN when disabling safe mode
            pin_dialog = PinDialog(self)
            if pin_dialog.exec_() == QDialog.Accepted:
                self.safe_mode = False
                self.safety_indicator.setText('⚠️ Safe Mode Disabled')
                self.safety_indicator.setStyleSheet("color: red;")
                QMessageBox.information(self, "Safe Mode", 
                    "Safe mode has been disabled. Content filtering is now turned off.")
        else:
            # No PIN needed to enable safe mode
            self.safe_mode = True
            self.safety_indicator.setText('🛡️ Safe Mode Active')
            self.safety_indicator.setStyleSheet("")
            QMessageBox.information(self, "Safe Mode", 
                "Safe mode has been enabled. Content filtering is now active.")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('SafeBrowse Junior')
    
    window = SafeBrowseJunior()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()