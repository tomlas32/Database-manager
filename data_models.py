from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel

class MeasurementTableModel(QAbstractTableModel):
    def __init__(self, parent=None, documents=None):
        super().__init__(parent)
        self._data = list(documents.items()) if documents else []

    def update_data(self, documents):
        self.beginResetModel()  # Signal start of major data change
        self._data = list(documents.items())  # Update data
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 4  # Consistent with your header count

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            entry_id, document = self._data[row]  # Unpack directly

            if col == 0:
                return entry_id
            elif col == 1:
                return document.get("user_id", "")  # Handle missing values
            elif col == 2:
                return document.get("test_date", "") 
            elif col == 3:
                return document.get("instrument_id", "")
    
    def headerData(self, section, orientation, role=Qt.DisplayRole): 
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return ["_id", "User ID", "Test Date", "Instrument"][section]