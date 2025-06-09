import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QListWidget, 
                           QLineEdit, QLabel, QMessageBox, QHBoxLayout, QGroupBox)
from urllib.parse import urlparse

# Load or create parental controls settings
def load_parental_controls():
    try:
        with open('parental_controls.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create the file with default settings
        default_settings = {
            "blocked_websites": [],
            "allowed_websites": []
        }
        with open('parental_controls.json', 'w') as f:
            json.dump(default_settings, f, indent=2)
        return default_settings

# Save parental controls settings
def save_parental_controls(settings):
    with open('parental_controls.json', 'w') as f:
        json.dump(settings, f, indent=2)

# Global variables for blocked and allowed websites
settings = load_parental_controls()
blocked_websites = settings.get("blocked_websites", [])
allowed_websites = settings.get("allowed_websites", [])

def normalize_domain(url):
    """Convert any URL input to a normalized domain name."""
    # Remove any protocol prefix if present
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove 'www.' if present
        if domain.startswith('www.'):
            domain = domain[4:]
        # Remove any trailing slash
        domain = domain.rstrip('/')
        return domain
    except:
        # If URL parsing fails, try to clean the input manually
        url = url.lower()
        # Remove protocol if present
        if '://' in url:
            url = url.split('://')[1]
        # Remove www. if present
        if url.startswith('www.'):
            url = url[4:]
        # Remove any trailing slash
        url = url.rstrip('/')
        return url

class ParentalControlsDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Parental Controls")
        self.setGeometry(200, 200, 600, 400)
        
        self.history = history
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # PIN Change Section
        pin_group = QGroupBox("Change PIN")
        pin_layout = QVBoxLayout()
        
        # Current PIN
        current_pin_layout = QHBoxLayout()
        current_pin_label = QLabel("Current PIN:")
        self.current_pin_input = QLineEdit()
        self.current_pin_input.setEchoMode(QLineEdit.Password)
        self.current_pin_input.setMaxLength(4)
        current_pin_layout.addWidget(current_pin_label)
        current_pin_layout.addWidget(self.current_pin_input)
        pin_layout.addLayout(current_pin_layout)
        
        # New PIN
        new_pin_layout = QHBoxLayout()
        new_pin_label = QLabel("New PIN:")
        self.new_pin_input = QLineEdit()
        self.new_pin_input.setEchoMode(QLineEdit.Password)
        self.new_pin_input.setMaxLength(4)
        new_pin_layout.addWidget(new_pin_label)
        new_pin_layout.addWidget(self.new_pin_input)
        pin_layout.addLayout(new_pin_layout)
        
        # Confirm New PIN
        confirm_pin_layout = QHBoxLayout()
        confirm_pin_label = QLabel("Confirm PIN:")
        self.confirm_pin_input = QLineEdit()
        self.confirm_pin_input.setEchoMode(QLineEdit.Password)
        self.confirm_pin_input.setMaxLength(4)
        confirm_pin_layout.addWidget(confirm_pin_label)
        confirm_pin_layout.addWidget(self.confirm_pin_input)
        pin_layout.addLayout(confirm_pin_layout)
        
        # Change PIN Button
        self.change_pin_button = QPushButton("Change PIN")
        self.change_pin_button.clicked.connect(self.change_pin)
        pin_layout.addWidget(self.change_pin_button)
        
        pin_group.setLayout(pin_layout)
        main_layout.addWidget(pin_group)
        
        # Create two columns for blocked and allowed sites
        columns_layout = QHBoxLayout()
        
        # Blocked Websites Column
        blocked_group = QGroupBox("Blocked Websites")
        blocked_layout = QVBoxLayout()
        self.blocked_list = QListWidget()
        self.update_blocked_list()
        blocked_layout.addWidget(self.blocked_list)
        blocked_group.setLayout(blocked_layout)
        columns_layout.addWidget(blocked_group)
        
        # Allowed Websites Column
        allowed_group = QGroupBox("Allowed Websites")
        allowed_layout = QVBoxLayout()
        self.allowed_list = QListWidget()
        self.update_allowed_list()
        allowed_layout.addWidget(self.allowed_list)
        allowed_group.setLayout(allowed_layout)
        columns_layout.addWidget(allowed_group)
        
        main_layout.addLayout(columns_layout)
        
        # Website Input Section
        input_group = QGroupBox("Add Website")
        input_layout = QVBoxLayout()
        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Enter website (e.g., youtube.com, amazon.in)")
        input_layout.addWidget(self.block_input)
        
        button_layout = QHBoxLayout()
        self.block_button = QPushButton("Block Website")
        self.block_button.clicked.connect(self.block_website)
        self.allow_button = QPushButton("Allow Website")
        self.allow_button.clicked.connect(self.allow_website)
        button_layout.addWidget(self.block_button)
        button_layout.addWidget(self.allow_button)
        input_layout.addLayout(button_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Browsing History Section
        history_group = QGroupBox("Browsing History")
        history_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.update_history_list()
        history_layout.addWidget(self.history_list)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)
        
        self.setLayout(main_layout)
    
    def update_blocked_list(self):
        """Update the blocked websites list."""
        self.blocked_list.clear()
        for site in blocked_websites:
            self.blocked_list.addItem(site)
    
    def update_allowed_list(self):
        """Update the allowed websites list."""
        self.allowed_list.clear()
        for site in allowed_websites:
            self.allowed_list.addItem(site)
    
    def update_history_list(self):
        """Update the browsing history list."""
        self.history_list.clear()
        for entry in self.history:
            self.history_list.addItem(f"{entry['timestamp']} - {entry['title']} ({entry['url']})")
    
    def block_website(self):
        """Block a website."""
        url = self.block_input.text().strip()
        if url:
            normalized_domain = normalize_domain(url)
            if normalized_domain not in blocked_websites:
                blocked_websites.append(normalized_domain)
                save_parental_controls({
                    "blocked_websites": blocked_websites,
                    "allowed_websites": allowed_websites
                })
                self.update_blocked_list()
                QMessageBox.information(self, "Blocked", f"{normalized_domain} has been blocked.")
            else:
                QMessageBox.warning(self, "Already Blocked", f"{normalized_domain} is already blocked.")
        else:
            QMessageBox.warning(self, "Error", "Please enter a website domain.")
    
    def allow_website(self):
        """Allow a website."""
        url = self.block_input.text().strip()
        if url:
            normalized_domain = normalize_domain(url)
            if normalized_domain in blocked_websites:
                blocked_websites.remove(normalized_domain)
                save_parental_controls({
                    "blocked_websites": blocked_websites,
                    "allowed_websites": allowed_websites
                })
                self.update_blocked_list()
                QMessageBox.information(self, "Allowed", f"{normalized_domain} has been allowed.")
            else:
                QMessageBox.warning(self, "Not Blocked", f"{normalized_domain} is not in the blocked list.")
        else:
            QMessageBox.warning(self, "Error", "Please enter a website domain.")
    
    def change_pin(self):
        """Change the parental controls PIN."""
        current_pin = self.current_pin_input.text()
        new_pin = self.new_pin_input.text()
        confirm_pin = self.confirm_pin_input.text()
        
        # Load current PIN
        try:
            with open('parental_pin.json', 'r') as f:
                stored_pin = json.load(f).get('pin', '0000')
        except FileNotFoundError:
            stored_pin = '0000'
        
        # Validate inputs
        if not current_pin or not new_pin or not confirm_pin:
            QMessageBox.warning(self, "Error", "Please fill in all PIN fields.")
            return
        
        if current_pin != stored_pin:
            QMessageBox.warning(self, "Error", "Current PIN is incorrect.")
            return
        
        if new_pin != confirm_pin:
            QMessageBox.warning(self, "Error", "New PINs do not match.")
            return
        
        if not new_pin.isdigit() or len(new_pin) != 4:
            QMessageBox.warning(self, "Error", "PIN must be 4 digits.")
            return
        
        # Save new PIN
        with open('parental_pin.json', 'w') as f:
            json.dump({'pin': new_pin}, f)
        
        QMessageBox.information(self, "Success", "PIN has been changed successfully.")
        
        # Clear inputs
        self.current_pin_input.clear()
        self.new_pin_input.clear()
        self.confirm_pin_input.clear()