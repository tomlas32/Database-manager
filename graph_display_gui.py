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
            line_styles = [Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotDotLine]

            if "pressure_measurements" in document and document["pressure_measurements"]:
                measurements = document["pressure_measurements"]
                x = [float(point[1]) for point in measurements]
                y = [float(point[2]) for point in measurements]
                pen = pg.mkPen(color=i, width=2)  # Default pen for all plots
                self.graph_widget.plot(x, y, pen=pen, name=str(entry_id))
            elif "temp_measurements" in document and document["temp_measurements"]:
                measurements = document["temp_measurements"]
                for channel, data in measurements.items():
                    if data:
                        x = [float(point[0]) for point in data]
                        y = [float(point[1]) for point in data]
                        line_style = line_styles.pop()
                        pen = pg.mkPen(color=i, style=line_style, width=2)  # Default pen for all plots
                        self.graph_widget.plot(x, y, pen=pen, name=str(entry_id))
    
    # highlights plots based on user choice from tabel view
    def highlight_plot(self, selected):
        # Reset all plot items to their original style (while maintaining original color)
        for item in self.graph_widget.getPlotItem().listDataItems():
            original_pen = item.opts['pen']
            if original_pen.width() == 4: # Check if it's highlighted (only width changed)
                new_pen = pg.mkPen(
                    color=original_pen.color(),  # Keep the original color
                    width=2,  # Reset width back to 2
                    style=original_pen.style()  # Keep original style
                )  
                item.setPen(new_pen)  

        # Extract selected entry IDs
        indexes = selected.indexes() if isinstance(selected, QItemSelection) else [selected]
        selected_entry_ids = [self.table_model1._data[index.row()][0] for index in indexes]

        # Highlight all plots associated with selected entries
        for item in self.graph_widget.getPlotItem().listDataItems():
            if item.name() in selected_entry_ids:
                highlight_pen = pg.mkPen(
                    color=item.opts['pen'].color(), # Keep the original color
                    width=4,  # Change width to 4
                    style=item.opts['pen'].style()  # Keep original style
                )
                item.setPen(highlight_pen)

    # function for getting sensor data list per entry_id selected
    def get_sensor_data(self, documents):
        sensor_data = {}
        for entry_id, doc in documents.items():
            if "pressure_measurements" in doc:
                sensor_data[entry_id] = doc["pressure_measurements"]
            elif "temp_measurements" in doc:
                sensor_data[entry_id] = doc["temp_measurements"]

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
                if isinstance(data, list):  
                    # Write header row
                    worksheet.write_row(0, 0, ["Sensor", "Time", "Value"])  # Assuming your data has these columns
                    # Write data rows (starting from row 1)
                    for row_num, point in enumerate(data, start=1):  # Start from row 1
                        worksheet.write_row(row_num, 0, point)
                elif isinstance(data, dict):
                    channels = list(data.keys())             # Get all channel names
                    header = ["Time"] + channels
                    worksheet.write_row(0, 0, header)
                    num_rows = len(data[channels[0]]) 
                    for row_num in range(num_rows):
                        row_data = [data[ch][row_num][0] for ch in channels]  # Get time for each channel
                        values = [data[ch][row_num][1] for ch in channels]    # Get temp value for each channel
                        row_data = [row_data[0]] + values                     # Combine time and values
                        worksheet.write_row(row_num + 1, 0, row_data)

            workbook.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the file:\n{e}", QMessageBox.Ok)
            return  # Exit the function on error
    
    # helper function for exporting data into xslx format
    def export_data(self):
        try:
            sensor_data = self.get_sensor_data(self.documents)
            self.write_to_xlsx(sensor_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while exporting the data:\n{e}", QMessageBox.Ok)
            return  # Exit the function on error

    #exit function
    def close_window(self):
        self.close()