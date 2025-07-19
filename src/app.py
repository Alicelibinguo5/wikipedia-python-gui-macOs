from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QLineEdit, QPushButton, QLabel, QComboBox, 
                           QTableWidget, QFrame, QHBoxLayout, QProgressBar,
                           QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QCursor, QDesktopServices
import sys
import requests
import webbrowser
import threading

class SearchThread(QThread):
    finished = pyqtSignal(list, str)
    error = pyqtSignal(str)
    
    def __init__(self, query, limit):
        super().__init__()
        self.query = query
        self.limit = limit
        
    def run(self):
        try:
            # Add proper headers
            headers = {
                'User-Agent': 'WikiSearchApp/1.0 (your@email.com)',  # Replace with your email
                'Accept': 'application/json'
            }
            
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                'action': 'opensearch',
                'search': self.query,
                'limit': self.limit,
                'format': 'json',
                'namespace': '0'
            }
            
            response = requests.get(
                search_url, 
                params=search_params, 
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 429:
                self.error.emit("Rate limit reached. Please wait a few seconds and try again.")
                return
            
            response.raise_for_status()
            
            data = response.json()
            
            if len(data) < 4:
                self.error.emit("Invalid response format from Wikipedia API")
                return
                
            titles = data[1] if len(data) > 1 else []
            descriptions = data[2] if len(data) > 2 else []
            urls = data[3] if len(data) > 3 else []
            
            articles = []
            for i, title in enumerate(titles):
                articles.append({
                    'title': title,
                    'description': descriptions[i] if i < len(descriptions) else 'No description',
                    'url': urls[i] if i < len(urls) else '',
                })
            
            self.finished.emit(articles, self.query)
            
        except requests.exceptions.RequestException as e:
            self.error.emit(f"Network error: {str(e)}")
        except Exception as e:
            self.error.emit(str(e))

class WikipediaSearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wikipedia Article Search")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Wikipedia Search Tool")
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: navy;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Search section
        search_frame = QFrame()
        search_frame.setStyleSheet("QFrame { background-color: lightblue; border: 2px solid gray; }")
        search_layout = QVBoxLayout(search_frame)
        
        # Search label
        search_label = QLabel("🔍 Enter your search term below:")
        search_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        search_label.setStyleSheet("color: darkblue;")
        search_layout.addWidget(search_label)
        
        # Search input area
        input_layout = QHBoxLayout()
        
        # Search entry with modern styling
        self.search_entry = QLineEdit()
        self.search_entry.setStyleSheet("""
            QLineEdit {
                background-color: #1A237E;
                color: white;
                padding: 12px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
            }
            QLineEdit:focus {
                background-color: #283593;
                border: 2px solid #3949AB;
            }
            QLineEdit::placeholder {
                color: #9FA8DA;
            }
        """)
        self.search_entry.setPlaceholderText("Search Wikipedia...")
        input_layout.addWidget(self.search_entry)
        
        # Results limit combo
        limit_label = QLabel("Results:")
        limit_label.setFont(QFont("Arial", 12))
        input_layout.addWidget(limit_label)
        
        self.limit_combo = QComboBox()
        self.limit_combo.addItems(["5", "10", "15", "20"])
        self.limit_combo.setCurrentText("10")
        self.limit_combo.setFont(QFont("Arial", 12))
        input_layout.addWidget(self.limit_combo)
        
        search_layout.addLayout(input_layout)
        
        # Search button with modern styling
        self.search_btn = QPushButton("Search")
        self.search_btn.setFont(QFont("Arial", 14))
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2471A3;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        search_layout.addWidget(self.search_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        search_layout.addWidget(self.progress)
        
        # Status label with modern styling
        self.status_label = QLabel("Enter your search term above")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: #7F8C8D;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_layout.addWidget(self.status_label)
        
        main_layout.addWidget(search_frame)
        
        # Results area
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(['Title', 'Description', 'Link'])
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: #F8F9FA;
                border-radius: 8px;
                padding: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:hover {
                background-color: #E9ECEF;
            }
        """)
        main_layout.addWidget(self.results_table)
        
        # Connect signals
        self.search_btn.clicked.connect(self.search_articles)
        self.search_entry.returnPressed.connect(self.search_articles)
        
        # Show initial instructions
        self.show_instructions()
        
    def show_instructions(self):
        self.results_table.setRowCount(0)  # Clear table
        self.status_label.setText("Start typing to search Wikipedia articles")

    def search_articles(self):
        query = self.search_entry.text().strip()
        if not query:
            self.status_label.setText("❌ Please enter a search term!")
            return
            
        # Add a small delay before starting new search
        QThread.msleep(1000)  # 1 second delay
            
        self.search_btn.setEnabled(False)
        self.search_btn.setText("🔍 Searching...")
        self.progress.setVisible(True)
        self.status_label.setText("🔍 Searching Wikipedia...")
        self.results_table.setRowCount(0)
        
        self.search_thread = SearchThread(query, int(self.limit_combo.currentText()))
        self.search_thread.finished.connect(self.display_results)
        self.search_thread.error.connect(self.show_error)
        self.search_thread.start()
        
    def display_results(self, articles, query):
        try:
            self.search_btn.setEnabled(True)
            self.search_btn.setText("🔍 Search")
            self.progress.setVisible(False)
            
            if not articles:
                self.status_label.setText("❌ No results found")
                self.results_table.setRowCount(0)
                return
                    
            self.status_label.setText(f"✅ Found {len(articles)} articles")
            self.results_table.setRowCount(len(articles))
            
            for i, article in enumerate(articles):
                # Title
                title_item = QTableWidgetItem(article.get('title', 'No title'))
                title_item.setFlags(title_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.results_table.setItem(i, 0, title_item)
                
                # Description
                desc_item = QTableWidgetItem(article.get('description', 'No description'))
                desc_item.setFlags(desc_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.results_table.setItem(i, 1, desc_item)
                
                # Link - Updated implementation
                url = article.get('url', '')
                link_item = QPushButton("🔗 Open")
                link_item.setStyleSheet("""
                    QPushButton {
                        background-color: #3498DB;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #2980B9;
                    }
                """)
                
                if url:
                    # Use a lambda with default argument to capture the current URL
                    link_item.clicked.connect(lambda checked, u=url: self.open_url(u))
                else:
                    link_item.setEnabled(False)
                    
                self.results_table.setCellWidget(i, 2, link_item)
                
            # Adjust column widths
            self.results_table.setColumnWidth(0, 200)
            self.results_table.setColumnWidth(2, 100)
            
        except Exception as e:
            self.show_error(f"Failed to display results: {str(e)}")
            
    def show_error(self, error_msg):
        self.search_btn.setEnabled(True)
        self.search_btn.setText("🔍 Search")
        self.progress.setVisible(False)
        self.status_label.setText(f"❌ Error: {error_msg}")
        print(f"Error occurred: {error_msg}")  # Debug output
        self.results_table.setRowCount(0)

    def open_url(self, url):
        """Helper method to open URLs safely"""
        try:
            QDesktopServices.openUrl(QUrl(url))
        except Exception as e:
            self.show_error(f"Failed to open URL: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WikipediaSearchGUI()
    window.show()
    sys.exit(app.exec())