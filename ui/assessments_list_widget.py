from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QListWidget


class AssessmentsListWidget(QListWidget):
    dropEventOccurred = pyqtSignal()

    def __init__(self, parent=None):
        super(AssessmentsListWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropEventOccurred.emit()
