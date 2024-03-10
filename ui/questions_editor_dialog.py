import contextlib
import copy
import random
from typing import Optional

import ujson as json
from PyQt6 import uic
from PyQt6.QtCore import QDate, Qt, QSettings
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import QColorDialog, QDialog, QInputDialog, QToolBox, QListWidget

from ui.questions_tree_widget import QuestionsTreeWidget
from ui.assessments_list_widget import AssessmentsListWidget
from utils import globals
from utils.school import School


class QuestionsEditor(QDialog):
    def __init__(self, school: School, parent=None):
        super(QDialog, self).__init__(parent)
        uic.loadUi("ui/questions_editor_dialog.ui", self)
        self.settings = QSettings("TheCodingJ's", "Gradiance", self)
        self.school = school
        self.data = {}
        self.load_data()
        self.questions_widget = QuestionsTreeWidget(self)
        self.selected_assessment: Optional[str] = None
        self.selected_grade_level: Optional[str] = None
        self.listWidget_assessments = AssessmentsListWidget(self)
        self.listWidget_assessments.dropEventOccurred.connect(self.assessments_moved)
        self.listWidget_assessments.itemSelectionChanged.connect(self.assessment_changed)
        self.listWidget_assessments.itemDoubleClicked.connect(self.rename_assessment)
        self.listWidget_assessments.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.assessments_layout.addWidget(self.listWidget_assessments)
        self.listWidget_grade_levels: QListWidget
        self.listWidget_grade_levels.itemSelectionChanged.connect(self.grade_level_changed)
        self.listWidget_grade_levels.setCurrentRow(self.settings.value("last_selected_grade", 0, int))
        self.pushButton_add_assessment.clicked.connect(self.add_assessment)
        self.pushButton_remove_assessment.clicked.connect(self.remove_assessment)
        self.questions_layout.addWidget(self.questions_widget)
        self.showMaximized()
        self.show()

    def assessments_moved(self):
        grade_data = {}
        self.settings.setValue(f"{self.selected_grade_level} - last_selected_assessment", self.listWidget_assessments.currentRow())
        for row in range(self.listWidget_assessments.count()):
            assessment = self.listWidget_assessments.item(row).text()
            grade_data[assessment] = self.data[self.selected_grade_level][assessment]
        self.data[self.selected_grade_level] = grade_data
        self.save()

    def assessment_changed(self):
        self.settings.setValue(f"{self.selected_grade_level} - last_selected_assessment", self.listWidget_assessments.currentRow())
        if self.selected_assessment is not None:
            self.data[self.selected_grade_level][self.selected_assessment] = self.questions_widget.get_tree_data()
            self.save()
        self.selected_assessment = self.listWidget_assessments.currentItem().text()
        try:
            self.questions_widget.setEnabled(True)
            self.questions_widget.load_data(self.data[self.selected_grade_level][self.selected_assessment])
        except KeyError:
            self.questions_widget.setEnabled(False)
            self.questions_widget.load_data({})

    def grade_level_changed(self):
        self.settings.setValue("last_selected_grade", self.listWidget_grade_levels.currentRow())
        if self.selected_assessment is not None:
            self.data[self.selected_grade_level][self.selected_assessment] = self.questions_widget.get_tree_data()
            self.save()
        self.selected_grade_level = self.listWidget_grade_levels.currentItem().text()
        self.listWidget_assessments.blockSignals(True)
        self.listWidget_assessments.clear()
        self.listWidget_assessments.addItems(self.data[self.selected_grade_level].keys())
        last_selected_assessment_index = self.settings.value(f"{self.selected_grade_level} - last_selected_assessment", 0, int)
        self.listWidget_assessments.setCurrentRow(last_selected_assessment_index)
        try:
            self.selected_assessment = list(self.data[self.selected_grade_level].keys())[last_selected_assessment_index]
        except IndexError:
            self.selected_assessment = None
        self.listWidget_assessments.blockSignals(False)
        try:
            self.questions_widget.setEnabled(True)
            self.questions_widget.load_data(self.data[self.selected_grade_level][self.selected_assessment])
        except KeyError:
            self.questions_widget.setEnabled(False)
            self.questions_widget.load_data({})

    def add_assessment(self):
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter assessment name:"
        )
        if ok_pressed and text:
            self.listWidget_assessments.addItem(text)
            self.data[self.selected_grade_level][text] = {}
            self.save()
            if len(self.data[self.selected_grade_level]) == 1:
                self.listWidget_assessments.setCurrentRow(0)

    def rename_assessment(self):
        old_assessment_name = self.selected_assessment
        text, ok_pressed = QInputDialog.getText(
            self, "Input Dialog", "Enter assessment name:", text=old_assessment_name
        )
        if ok_pressed and text:
            copied_data = copy.deepcopy(self.data[self.selected_grade_level][old_assessment_name])
            del self.data[self.selected_grade_level][old_assessment_name]
            self.data[self.selected_grade_level][text] = copied_data
            self.save()
            self.listWidget_assessments.blockSignals(True)
            self.listWidget_assessments.clear()
            self.listWidget_assessments.addItems(self.data[self.selected_grade_level].keys())
            self.listWidget_assessments.blockSignals(False)
            assessments = []
            for row in range(self.listWidget_assessments.count()):
                assessments.append(self.listWidget_assessments.item(row).text())
            self.selected_assessment = text
            self.listWidget_assessments.setCurrentRow(assessments.index(self.selected_assessment))

    def remove_assessment(self):
        assessments = []
        for row in range(self.listWidget_assessments.count()):
            assessments.append(self.listWidget_assessments.item(row).text())
        current_item = (
            0
            if self.selected_assessment is None
            else assessments.index(self.selected_assessment)
        )
        item, ok_pressed = QInputDialog.getItem(
            None,
            "Select assessment",
            "Choose an assessment to remove:",
            assessments,
            current_item,
            editable=False,
        )
        if ok_pressed and item:
            del self.data[self.selected_grade_level][item]
            assessments.remove(item)
            self.save()
            self.listWidget_assessments.blockSignals(True)
            self.listWidget_assessments.clear()
            self.listWidget_assessments.addItems(self.data[self.selected_grade_level].keys())
            self.listWidget_assessments.blockSignals(False)
            if len(self.data[self.selected_grade_level]) == 0 or self.selected_assessment == item:
                self.selected_assessment = None
                self.questions_widget.load_data({})
                self.questions_widget.setEnabled(False)
            else:
                self.listWidget_assessments.setCurrentRow(assessments.index(self.selected_assessment))

    def save(self):
        with open(
            f"{globals.database_location}/{self.school.name}/Questions.json", "w"
        ) as file:
            json.dump(self.data, file, indent=4)

    def load_data(self):
        try:
            with open(
                f"{globals.database_location}/{self.school.name}/Questions.json", "r"
            ) as file:
                self.data = json.load(file)
        except FileNotFoundError:
            for row in range(self.listWidget_grade_levels.count()):
                self.data[self.listWidget_grade_levels.item(row).text()] = {}
            self.save()

    def clear_layout(self, layout):
        with contextlib.suppress(AttributeError):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        self.clear_layout(item.layout())

    def closeEvent(self, event):
        if self.selected_assessment is not None:
            self.data[self.selected_grade_level][self.selected_assessment] = self.questions_widget.get_tree_data()
            self.save()
        self.accept()
