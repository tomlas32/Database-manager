from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5 import QtGui
import sys, os


class WaitingSpinner(QWidget):
    def __init__(
        self,
        parent,
        centerOnParent=True,
        disableParentWhenSpinning=False,
        modality=Qt.NonModal,
    ):
        super().__init__(parent)

        self._centerOnParent = centerOnParent
        self._disableParentWhenSpinning = disableParentWhenSpinning

        # Create the movie and label
        self.movie = QtGui.QMovie(
            self.resource_path("assets/loading.gif")
        )  # Replace with your spinner GIF path
        self.movie_label = QLabel(self)
        self.movie_label.setMovie(self.movie)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie.setScaledSize(QSize(30, 30))
        self.movie_label.setFixedSize(30, 30)

        # Create the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.movie_label)
        self.setLayout(layout)

        # Initialize variables
        self.parent = parent
        self._isSpinning = False

    def start(self):
        self.movie.start()
        self._isSpinning = True
        if self.parent and self._disableParentWhenSpinning:
            self.parent.setEnabled(False)
        if self._centerOnParent:
            self.move(self.parent.width() // 2, self.parent.height() // 2)
        self.show()

    def stop(self):
        self.movie.stop()
        self._isSpinning = False
        if self.parent and self._disableParentWhenSpinning:
            self.parent.setEnabled(True)
        self.hide()

    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS2
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
