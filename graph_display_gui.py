import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QMainWindow, QWidget, QPushButton, QComboBox, QMessageBox, QLabel, QLineEdit
from PyQt5.QtWidgets import QSizePolicy, QSpacerItem, QTextEdit, QTableView, QAbstractItemView, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
import credentials as cr
import database as db
import sys
import pyqtgraph as pg


class LineGraphWindow(QMainWindow):
    def __init__(self, measurements_list):
        super().__init__()


        ######################## specify basic resources
        data_icon = QIcon("D:\Projects\Work projects\Database-manager\\assets\graph.ico")

        self.setWindowTitle("Data Visualization")
        self.setFixedSize(1024, 500)
        self.setWindowIcon(data_icon)

        ######################## specify layouts
        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)

        ######################## specify widgets
        self.window = QWidget()
        self.window.setLayout(self.main_layout)
        self.setCentralWidget(self.window)

        ######################## configure plotting area
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("#000000")
        self.graph_widget.setLabel("left", "Value")
        self.graph_widget.setLabel("bottom", "Time")
        self.graph_widget.showGrid(True, True)
        self.graph_widget.setMouseEnabled(x=True, y=False)
        self.graph_widget.setClipToView(True)
        self.graph_widget.addLegend(True)
        self.left_layout.addWidget(self.graph_widget)
        
        self.display_graph(measurements_list)

    def display_graph(self, measurements_list):
        for i, measurement in enumerate(measurements_list):
            x = [float(point[1]) for point in measurement]
            y = [float(point[2]) for point in measurement] # something here might not be working
            name = measurement[0][0]
            pen = pg.mkPen(color=(i, len(measurements_list)), width=2)
            self.graph_widget.plot(x, y, pen=pen, name=name)



# if __name__ == "__main__":
#     list = []
#     application = QApplication(sys.argv)                                                            # creates instance of QApplication
#     viewer_window = LineGraphWindow(list)
#     viewer_window.show()
#     sys.exit(application.exec_())