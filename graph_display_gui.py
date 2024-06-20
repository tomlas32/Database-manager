import pyqtgraph as pg
from PyQt5.QtCore import Qt, QItemSelection
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog, QMainWindow, QWidget, QPushButton, QMessageBox
from PyQt5.QtWidgets import QTableView, QAbstractItemView
from PyQt5.QtGui import QIcon
import pyqtgraph as pg
from data_models import MeasurementTableModel
import xlsxwriter


class LineGraphWindow(QMainWindow):
    def __init__(self, measurements_list, documents):
        super().__init__()

        ######################## specify basic resources
        data_icon = QIcon(".\\assets\\graph.ico")

        self.setWindowTitle("Data Visualization")
        self.setFixedSize(1024, 500)
        self.setWindowIcon(data_icon)
        self.documents = documents

        ######################## specify layouts
        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        self.table_view_layout = QVBoxLayout()
        self.buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)
        self.right_layout.addLayout(self.table_view_layout)
        self.right_layout.addLayout(self.buttons_layout)

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
        self.table_view_layout.addWidget(self.table_view1)

        ######################## specify widgets
        self.window = QWidget()
        self.window.setLayout(self.main_layout)
        self.setCentralWidget(self.window)
        #### create buttons
        self.export_button = QPushButton("Export")
        self.export_button.setEnabled(True)
        self.export_button.clicked.connect(self.export_data)
        self.buttons_layout.addWidget(self.export_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setEnabled(True)
        self.exit_button.clicked.connect(self.close)
        self.buttons_layout.addWidget(self.exit_button)

        ######################## configure plotting area
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("#000000")
        self.graph_widget.setLabel("left", "Value")
        self.graph_widget.setLabel("bottom", "Time (s)")
        self.graph_widget.showGrid(True, True)
        self.graph_widget.setMouseEnabled(x=True, y=False)
        self.graph_widget.setClipToView(True)
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

    # function for getting sensor data list per entry_id selected
    def get_sensor_data(self, documents, selected):
        sensor_data = {}
        # Get selected rows from the selection model
        selected_rows = selected.selectedRows()

        for model_index in selected_rows:
            # Assuming the entry_id is in the first column
            entry_id = self.table_model1.data(model_index, Qt.DisplayRole)

            for doc_id, doc in documents.items():
                if doc_id == entry_id:
                    sensor_data[entry_id] = doc["pressure_measurements"]
        return sensor_data

    # function for writing sensor data to xls file
    def write_to_xlsx(self, sensor_data):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save file", "", "Excel files (*.xlsx)")

        if not file_name:
            return  # User canceled the file selection
        try:
            workbook = xlsxwriter.Workbook(file_name)
            for entry_id, data in sensor_data.items():
                worksheet = workbook.add_worksheet(str(entry_id))  # Name the sheet with the entry_id
                # Write header row
                worksheet.write_row(0, 0, ["Sensor", "Time", "Value"])  # Assuming your data has these columns
                # Write data rows (starting from row 1)
                for row_num, point in enumerate(data, start=1):  # Start from row 1
                    worksheet.write_row(row_num, 0, point)
            workbook.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the file:\n{e}", QMessageBox.Ok)
            return  # Exit the function on error
    
    # helper function for exporting data into xslx format
    def export_data(self):
        """Handles the complete export process."""
        selected = self.table_view1.selectionModel()
        if selected.hasSelection():
            sensor_data = self.get_sensor_data(self.documents, selected)  # Use self.documents directly
            self.write_to_xlsx(sensor_data)
        else:
            QMessageBox.information(self, "Information", "Please select rows to export.", QMessageBox.Ok)

    #exit function
    def close_window(self):
        self.close()