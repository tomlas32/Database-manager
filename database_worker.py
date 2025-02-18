from PyQt5.QtCore import pyqtSignal, QObject
import database as db


# Class to handle database search
class DatabaseWorker(QObject):
    finished = pyqtSignal(list)  # Signal to indicate completion

    def __init__(self, query, db_name, collection_name):
        super().__init__()
        self.query = query
        self.db_name = db_name
        self.collection_name = collection_name

    def run(self):
        documents = self.search_database(self.query)
        self.finished.emit(documents)  # Emit the result (list)

    # function to search database based on given query
    def search_database(self, query):
        # Now you can use self.db_name and self.collection_name
        if self.db_name and self.collection_name:
            documents = list(
                db.find_documents(self.db_name, self.collection_name, query)
            )
        return documents
