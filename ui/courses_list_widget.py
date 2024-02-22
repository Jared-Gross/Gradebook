from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QListWidget

from ui.course_widget import CourseWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student


class CoursesListWidget(QListWidget):
    dropEventOccurred = pyqtSignal()

    def __init__(self, school: School, parent=None):
        super(CoursesListWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropEventOccurred.emit()
