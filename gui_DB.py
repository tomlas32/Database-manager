from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMainWindow,
    QWidget,
    QPushButton,
    QComboBox,
    QMessageBox,
    QLabel,
)
from PyQt5.QtWidgets import (
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QTableView,
    QAbstractItemView,
    QMenu,
    QAction,
    QApplication,
)
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
import credentials as cr
import database as db
from graph_display_gui import LineGraphWindow
from database_worker import DatabaseWorker
from waiting_spinner import WaitingSpinner
from bson.objectid import ObjectId
import xlsxwriter, os, sys


class DatabaseManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.search_completed = pyqtSignal(list)
        self.worker_thread = None

        ######################## specify basic resources
        main_icon = QIcon(self.resource_path("assets/main-icon.ico"))

        ######################## specify basic main window configurations
        self.setWindowTitle("Database Manager")
        self.setWindowIcon(main_icon)
        self.setFixedSize(940, 600)

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
        self.spacer_5 = QSpacerItem(20, 30, QSizePolicy.Fixed, QSizePolicy.Fixed)
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
        self.url_input.setFixedWidth(350)
        self.url_input.addItems(cr.MONGO_URL)
        self.db_label = QLabel("Database:")
        self.db_input = QComboBox()
        self.db_input.setFixedWidth(140)
        self.collection_label = QLabel("Collection:")
        self.collection_input = QComboBox()
        self.collection_input.setFixedWidth(170)
        self.db_layout.addWidget(self.url_label)
        self.db_layout.addWidget(self.url_input)
        self.db_layout.addWidget(self.db_label)
        self.db_layout.addWidget(self.db_input)
        self.db_layout.addWidget(self.collection_label)
        self.db_layout.addWidget(self.collection_input)

        # create query widgets and add to layouts
        self.query_label = QLabel("Query:")
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your query here...")
        self.query_input.setGeometry(0, 0, 300, 60)
        self.query_input.setFixedHeight(60)
        self.query_button = QPushButton("Search")
        self.query_button.setFixedWidth(80)
        self.query_button.clicked.connect(self.on_search_button_clicked)
        self.query_layout.addWidget(self.query_label)
        self.query_layout.addWidget(self.query_input)
        self.query_layout.addWidget(self.query_button)
        self.query_layout.addSpacerItem(self.spacer_5)
        self.spinner = WaitingSpinner(
            self.query_button, True
        )  # Set roundness to True for circle
        self.query_layout.addWidget(self.spinner)
        self.spinner.hide()
        self.query_layout.addStretch(1)

        # create table view widget and add to the corresponding layout
        self.table_view = QTableView()
        self.table_view.setGeometry(0, 0, 800, 300)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        self.table_model = QStandardItemModel()
        self.table_view.doubleClicked.connect(self.open_graph_window)
        self.result_layout.addWidget(self.table_view)

        # create buttons and add to the corresponding layout
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.open_graph_window)
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_to_xlsx)
        self.clear_button = QPushButton("Clear")
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.export_button)
        self.buttons_layout.addSpacerItem(self.spacer_4)
        self.buttons_layout.addWidget(self.clear_button)
        self.buttons_layout.addStretch(1)

        # database specific connection initialization
        self.db_input.currentTextChanged.connect(self.populate_collection_combobox)
        self.populate_db_combobox()

    # function for populating database combobox with the user created databases
    def populate_db_combobox(self):
        self.db_input.clear()
        self.db_input.addItems(db.get_database())

    # function for populating collection combobox with the user created collections
    def populate_collection_combobox(self):
        db_name = self.db_input.currentText()
        if db_name:
            self.collection_input.clear()
            self.collection_input.addItems(db.list_collections(db_name))

    # function parsing user query input
    def create_query(self):
        query_text = self.query_input.toPlainText().strip()
        # parse the query string to obtain individual key-value pairs
        query_parts = query_text.split(";")
        query = {}
        try:
            for part in query_parts:
                if ":" in part:
                    key, value = part.split(":")
                    key = key.strip()
                    values = [
                        v.strip() for v in value.split(",")
                    ]  # creates a list of values for a given key in case user specified multiple values to search for

                    if key in [
                        "_id",
                        "test_date",
                        "test_time",
                        "user_id",
                        "instrument_id",
                        "experiment_name",
                        "cartridge_number",
                        "protocol",
                        "sensor_type",
                    ]:
                        values = [
                            ObjectId(v) if key == "_id" else str(v) for v in values
                        ]
                        if (
                            len(values) > 1
                        ):  # if user specified multiple values and we dealing with a list
                            query[key] = {"$in": values}
                        else:
                            query[key] = values[0]
            return query
        except ValueError:
            return None

    # helper function for making a database query when search button is clicked
    def on_search_button_clicked(self):
        self.table_model.clear()
        if len(self.query_input.toPlainText()) > 0:
            query = self.create_query()

            # Disable the search button and show the spinner
            self.query_button.setEnabled(False)
            self.spinner.start()
            try:
                if self.worker_thread is not None and self.worker_thread.isRunning():
                    # If a previous thread is running, wait for it to finish
                    self.worker_thread.quit()
                    self.worker_thread.wait()
            except RuntimeError:
                pass
            self.worker_thread = QThread()
            self.worker = DatabaseWorker(
                query, self.db_input.currentText(), self.collection_input.currentText()
            )
            self.worker.moveToThread(self.worker_thread)

            # Connect signals and start the thread
            self.worker_thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.worker_thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.worker.finished.connect(self.handle_search_result)  # Connect directly
            self.worker.finished.connect(self.reset_worker_thread)  # New method
            self.worker_thread.start()

            QApplication.processEvents()

    # function for updating table view based on database query output
    def handle_search_result(self, documents):
        if documents:
            try:
                desired_header_order = [
                    "_id",
                    "user_id",
                    "test_date",
                    "test_time",
                    "instrument_id",
                    "cartridge_number",
                    "test_duration",
                    "protocol",
                ]

                all_headers = set()
                for document in documents:
                    all_headers.update(
                        document.keys()
                    )  #  this itarates through the docs and gets the keys. set will only add unique values

                all_headers = list(all_headers)

                if "pressure_measurements" in all_headers:
                    all_headers.remove("pressure_measurements")
                elif "temp_measurements" in all_headers:
                    all_headers.remove("temp_measurements")
                headers = [
                    header for header in desired_header_order if header in all_headers
                ]
                # Add remaining headers alphabetically
                remaining_headers = sorted(set(all_headers) - set(headers))
                headers.extend(remaining_headers)

                self.table_model.setHorizontalHeaderLabels(headers)
                # Add all documents including the first one
                for document in documents:
                    row = [
                        QStandardItem(str(document.get(key, ""))) for key in headers
                    ]  # Handle missing keys
                    self.table_model.appendRow(row)

                self.query_button.setEnabled(True)
                self.spinner.stop()

            except (
                TypeError,
                StopIteration,
            ):  # Handle cases where 'documents' is not iterable or empty
                QMessageBox.warning(
                    self, "Current query", "No results found or invalid data format."
                )
                self.query_button.setEnabled(True)
                self.spinner.stop()
        else:
            QMessageBox.warning(self, "Current query", "No results found")
            self.query_button.setEnabled(True)
            self.spinner.stop()

        self.table_view.setModel(self.table_model)
        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()

    def reset_worker_thread(self):
        self.worker_thread.deleteLater()  # Delete the thread after it's finished
        self.worker_thread = None  # Reset the reference

    # function defining context menu
    def show_context_menu(self, point):
        menu = QMenu(self)
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        menu.addAction(copy_action)
        menu.exec_(self.table_view.viewport().mapToGlobal(point))

    # function for copying selected rows to clipboard
    def copy_to_clipboard(self):
        selected_indexes = self.table_view.selectedIndexes()
        if selected_indexes:
            data = []
            for index in selected_indexes:
                data.append(index.data())
            text = "".join(data)
            QApplication.clipboard().setText(text)

    # function for visualizing data based on user choice from table view
    def open_graph_window(self):

        entry_ids = self.get_entry_ids()
        measurements_list, documents = self.get_docs_measurements(entry_ids)
        self.graph_window = LineGraphWindow(measurements_list, documents)
        self.graph_window.show()

    def get_entry_ids(self):
        selected_rows = {index.row() for index in self.table_view.selectedIndexes()}

        if not selected_rows:  # Check if any rows are selected
            QMessageBox.warning(self, "Error", "No rows selected.")
            return None  # Indicate no valid selection
        entry_ids = []
        for row in selected_rows:
            id_index = self.table_model.index(row, 0)
            entry_id = self.table_model.itemFromIndex(id_index).text()
            if entry_id:
                entry_ids.append(entry_id)

        return entry_ids

    # function for making query based on user row selection
    def get_docs_measurements(self, entry_ids):
        db_name = self.db_input.currentText()
        collection_name = self.collection_input.currentText()
        measurements_list, documents = db.get_measurements(
            entry_ids, db_name, collection_name
        )

        return measurements_list, documents

    def export_to_xlsx(self):
        entry_ids = self.get_entry_ids()
        if entry_ids is None:
            return
        try:
            _, documents = self.get_docs_measurements(entry_ids)
            sensor_data = self.get_sensor_data(documents)
            self.write_to_xlsx(sensor_data)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while exporting the data:\n{e}",
                QMessageBox.Ok,
            )
            return  # Exit the function on error

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
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save file", "", "Excel files (*.xlsx)"
        )
        if not file_name:
            return  # User canceled the file selection
        try:
            workbook = xlsxwriter.Workbook(file_name)
            for entry_id, data in sensor_data.items():
                worksheet = workbook.add_worksheet(
                    str(entry_id)
                )  # Name the sheet with the entry_id
                if isinstance(data, list):
                    # Write header row
                    worksheet.write_row(
                        0, 0, ["Sensor", "Time", "Value"]
                    )  # Assuming your data has these columns
                    # Write data rows (starting from row 1)
                    for row_num, point in enumerate(data, start=1):  # Start from row 1
                        worksheet.write_row(row_num, 0, point)
                elif isinstance(data, dict):
                    channels = list(data.keys())  # Get all channel names
                    header = ["Time"] + channels
                    worksheet.write_row(0, 0, header)
                    num_rows = len(data[channels[0]])
                    for row_num in range(num_rows):
                        row_data = [
                            data[ch][row_num][0] for ch in channels
                        ]  # Get time for each channel
                        values = [
                            data[ch][row_num][1] for ch in channels
                        ]  # Get temp value for each channel
                        row_data = [row_data[0]] + values  # Combine time and values
                        worksheet.write_row(row_num + 1, 0, row_data)

            workbook.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving the file:\n{e}",
                QMessageBox.Ok,
            )
            return  # Exit the function on error

    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS2
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
