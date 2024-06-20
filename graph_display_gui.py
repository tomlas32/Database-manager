import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QItemSelection
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QMainWindow, QWidget, QPushButton, QComboBox, QMessageBox, QLabel, QLineEdit
from PyQt5.QtWidgets import QSizePolicy, QSpacerItem, QTextEdit, QTableView, QAbstractItemView, QMenu, QAction, QApplication, QHeaderView
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
import credentials as cr
import database as db
import sys
import pyqtgraph as pg
from data_models import MeasurementTableModel


class LineGraphWindow(QMainWindow):
    def __init__(self, measurements_list, documents):
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

        ######################## table model
        self.table_model1 = MeasurementTableModel(self, documents)
        self.table_view1 = QTableView()
        self.table_view1.setModel(self.table_model1)
        self.table_view1.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view1.horizontalHeader().setVisible(True)
        self.table_view1.verticalHeader().setVisible(True)
        self.table_view1.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_view1.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_view1.doubleClicked.connect(self.highlight_plot)
        self.right_layout.addWidget(self.table_view1)

        ######################## specify widgets
        self.window = QWidget()
        self.window.setLayout(self.main_layout)
        self.setCentralWidget(self.window)

        ######################## configure plotting area
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("#000000")
        self.graph_widget.setLabel("left", "Value")
        self.graph_widget.setLabel("bottom", "Time (s)")
        self.graph_widget.showGrid(True, True)
        self.graph_widget.setMouseEnabled(x=True, y=False)
        self.graph_widget.setClipToView(True)
        self.graph_widget.addLegend(True)
        self.left_layout.addWidget(self.graph_widget)
        
        self.display_graph(measurements_list, documents)

    def display_graph(self, measurements_list, documents):

        self.graph_widget.clear()
        self.table_model1.update_data(documents)

        for i, document in enumerate(documents.values()):
            entry_id = document["_id"]
            measurements = document["pressure_measurements"]
            x = [float(point[1]) for point in measurements]
            y = [float(point[2]) for point in measurements]
            pen = pg.mkPen(color=i, width=2)  # Default pen for all plots
            self.graph_widget.plot(x, y, pen=pen, name=str(entry_id))

    def highlight_plot(self, selected):
        # Reset all plot items to their original color
        for i, item in enumerate(self.graph_widget.getPlotItem().listDataItems()):
            item.setPen(pg.mkPen(color=i , width=2))

        # Highlight the selected plot items
        indexes = selected.indexes() if isinstance(selected, QItemSelection) else [selected]
        for index in indexes:
            row = index.row()
            entry_id, _ = self.table_model1._data[row]
            for item in self.graph_widget.getPlotItem().listDataItems():
                if item.name() == entry_id:
                    item.setPen(pg.mkPen(color='m', width=4))  # Highlight matching plot
                    break  

# if __name__ == "__main__":
#     list = []
#     application = QApplication(sys.argv)                                                            # creates instance of QApplication
#     viewer_window = LineGraphWindow(list)
#     viewer_window.show()
#     sys.exit(application.exec_())