from gui_DB import DatabaseManager
from PyQt5.QtWidgets import QApplication
import sys



if __name__ == "__main__":
    application = QApplication(sys.argv)                                                            # creates instance of QApplication
    main_window = DatabaseManager()
    main_window.show()
    sys.exit(application.exec_())