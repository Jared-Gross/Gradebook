import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QInputDialog, QTabWidget, QWidget, QTabBar, QStyle, QStyleOptionTab

from ui.course_widget import CourseWidget
from utils import globals
from utils.assignment import Assignment
from utils.course import Course
from utils.school import School
from utils.student import Student

                
class MultiRowTabBar(QTabBar):
    def tabSizeHint(self, index):
        size_hint = super().tabSizeHint(index)
        size_hint.transpose()  # Transpose the size hint to make it vertical
        return size_hint

    def paintEvent(self, event):
        painter = QPainter(self)
        opt = QStyleOptionTab()

        tab_height = self.tabSizeHint(0).height()
        num_rows = (self.count() * tab_height) / self.height()
        row = 0
        y_offset = 0

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            tab_rect = opt.rect
            tab_width = tab_rect.width()
            tab_rect.setWidth(int(self.width() / self.count()))
            tab_rect.moveTop(y_offset + row * tab_height)

            # painter.drawControl(QTabBar.ControlElement.CE_TabBarTab, opt)
            self.style().drawPrimitive(QStyle.PrimitiveElement.PE_FrameTabWidget, opt, painter, self)
            painter.drawText(tab_rect, Qt.AlignmentFlag.AlignCenter, self.tabText(i))

            if tab_rect.bottom() > self.height():
                row += 1
                y_offset = -row * tab_height
class CoursesTabWidget(QTabWidget):
    def __init__(self, school: School, parent=None):
        super(CoursesTabWidget, self).__init__(parent)
        self.parent = parent
        self.courses: dict[str, Course] = {}
        self.school = school
        self.setMovable(True)
        self.setTabShape(QTabWidget.TabShape.Triangular)
        self.tabBarDoubleClicked.connect(self.rename_tab)
        self.setTabBar(MultiRowTabBar(self))
        
    def load_tab(self):
        course_name = self.current_tab()
        course_widget = CourseWidget(self.courses[course_name], self.school, self)
        self.blockSignals(True)
        self.insertTab(self.currentIndex(), course_widget, course_name)
        # With out this if statement you cannot select the last tab
        if self.currentIndex() == self.count()-1:
            self.removeTab(self.currentIndex())
            self.setCurrentIndex(self.currentIndex()+1)
        else:
            self.removeTab(self.currentIndex())
            self.setCurrentIndex(self.currentIndex()-1)
        self.blockSignals(False)

    def rename_tab(self):
        old_name = self.current_tab()
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter course name:", text=old_name
        )
        if ok_pressed and text:
            for course in self.school.courses:
                if course.name == old_name:
                    course.name = text
                    self.school.save()
                    break
            self.parent.last_selected_course = text
            self.parent.load_courses()

    def enable_save_tab_order(self):
        self.currentChanged.connect(self.save_tab_order)
        self.currentChanged.connect(self.load_tab)

    def current_tab(self) -> str:
        return self.tabText(self.currentIndex())

    def add_course(self, course: Course):
        self.addTab(QWidget(self), course.name)
        self.courses[course.name] = course

    def get_tab_order(self) -> list[str]:
        return [self.tabText(i) for i in range(self.count())]

    def save_tab_order(self):
        tab_order = self.get_tab_order()
        courses_order: list[Course] = []
        for tab in tab_order:
            for course in self.school.courses:
                if tab == course.name:
                    courses_order.append(course)
        self.school.courses = courses_order
        self.school.save()
