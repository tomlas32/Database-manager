import numpy as np
import pyqtgraph as pgt
from PyQt5.QtCore import QTimer, QObject, Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QMainWindow, QWidget, QPushButton, QComboBox, QMessageBox, QLabel, QLineEdit
from PyQt5.QtWidgets import QSizePolicy, QSpacerItem, QTextEdit, QTableView
from PyQt5.QtGui import QIcon
import credentials as cr

class DatabaseManager(QMainWindow):
    def __init__(self):
        super().__init__()


        ######################## specify basic resources
        main_icon = QIcon("D:\Projects\Work projects\Database-manager\\assets\main-icon.ico")
        
        ######################## specify basic main window configurations
        self.setWindowTitle("Database Manager")
        self.setWindowIcon(main_icon)
        self.setFixedSize(1024, 500)

        ######################## specify layouts
        self.main_layout = QVBoxLayout()
        self.db_layout = QHBoxLayout()
        self.query_layout = QHBoxLayout()
        self.result_layout = QHBoxLayout()
        self.buttons_layout = QHBoxLayout()

        ######################## specify widgets and add to layouts

        
        # create spacers
        self.spacer_1 = QSpacerItem(800, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.spacer_2 = QSpacerItem(800, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.spacer_3 = QSpacerItem(800, 50, QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.spacer_4 = QSpacerItem(800, 50, QSizePolicy.Fixed, QSizePolicy.Fixed)
        # main widget and layouts
        self.window = QWidget()
        self.window.setLayout(self.main_layout)
        self.setCentralWidget(self.window)
        self.main_layout.addLayout(self.db_layout)
        self.main_layout.addSpacerItem(self.spacer_1)
        self.main_layout.addLayout(self.query_layout)
        self.main_layout.addSpacerItem(self.spacer_2)
        self.main_layout.addLayout(self.result_layout)
        self.main_layout.addSpacerItem(self.spacer_3)
        self.main_layout.addLayout(self.buttons_layout)

        # create db widgets and add to layouts
        self.url_label = QLabel("Database URL:")
        self.url_input = QComboBox()
        self.url_input.setFixedWidth(510)
        self.url_input.addItems(cr.MONGO_URL)
        self.db_label = QLabel("Database:")
        self.db_input = QComboBox()
        self.db_input.setFixedWidth(140)
        self.collection_label = QLabel("Collection:")
        self.collection_input = QComboBox()
        self.collection_input.setFixedWidth(140)
        self.db_layout.addWidget(self.url_label)
        self.db_layout.addWidget(self.url_input)
        self.db_layout.addWidget(self.db_label)
        self.db_layout.addWidget(self.db_input)
        self.db_layout.addWidget(self.collection_label)
        self.db_layout.addWidget(self.collection_input)

        # create query widgets and add to layouts
        self.query_label = QLabel("Query:")
        self.query_input = QTextEdit()
        self.query_input.setFixedWidth(500)
        self.query_input.setFixedHeight(80)
        self.query_button = QPushButton("Search")
        self.query_button.setFixedWidth(50)
        self.query_layout.addWidget(self.query_label)
        self.query_layout.addWidget(self.query_input)
        self.query_layout.addWidget(self.query_button)
        self.query_layout.addStretch(1)

        # create table view widget and add to the corresponding layout
        self.table_view = QTableView()
        self.table_view.setFixedWidth(1000)
        self.table_view.setFixedHeight(270)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.result_layout.addWidget(self.table_view)

        # create buttons and add to the corresponding layout
        self.ok_button = QPushButton("OK")
        self.export_button = QPushButton("Export")
        self.clear_button = QPushButton("Clear")
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.export_button)
        self.buttons_layout.addSpacerItem(self.spacer_4)
        self.buttons_layout.addWidget(self.clear_button)
        self.buttons_layout.addStretch(1)




