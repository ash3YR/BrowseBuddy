from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                           QLabel, QPushButton, QHBoxLayout)
from datetime import datetime, timedelta

class ScreenTimeDialog(QDialog):
    def __init__(self, screen_time_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Screen Time Details")
        self.setGeometry(200, 200, 600, 400)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add total screen time label
        total_time = sum(screen_time_data.values())
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        total_label = QLabel(f"Total Screen Time: {hours} hours {minutes} minutes")
        layout.addWidget(total_label)
        
        # Create table for detailed breakdown
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Website", "Time Spent"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Add data to table
        self.update_table(screen_time_data)
        
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def update_table(self, screen_time_data):
        """Update the table with screen time data."""
        self.table.setRowCount(len(screen_time_data))
        
        for row, (site, seconds) in enumerate(screen_time_data.items()):
            # Website name
            site_item = QTableWidgetItem(site)
            self.table.setItem(row, 0, site_item)
            
            # Time spent
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            time_str = f"{hours}h {minutes}m"
            time_item = QTableWidgetItem(time_str)
            self.table.setItem(row, 1, time_item)
        
        self.table.resizeColumnsToContents() 