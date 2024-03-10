from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QMenu,
    QWidget,
)


class QuestionsTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(QTreeWidget, self).__init__(parent)
        self.setHeaderLabels(["Question", "Answer"])
        self.setColumnWidth(0, 550)
        self.setColumnWidth(1, 350)
        self.content: dict = {}
        self.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
        self.setVerticalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTreeWidget.ScrollMode.ScrollPerPixel)
        top = QTreeWidgetItem(self)
        self.addTopLevelItem(top)
        add_question_button = QPushButton("Add Question", self)
        add_question_button.clicked.connect(partial(self.add_question, "New Question", "New Question", True))
        self.setItemWidget(top, 0, add_question_button)
        self.itemChanged.connect(self.update_answer)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def add_question(self, question: str = "", answer: str = "", add_option: bool = False) -> QTreeWidgetItem:
        parent = QTreeWidgetItem(self)
        parent.setFlags(parent.flags() | Qt.ItemFlag.ItemIsEditable)
        parent.setText(0, question)
        parent.setText(1, answer)
        if add_option:
            self.add_option(parent, "New Option", True, None)
            button_child = QTreeWidgetItem(parent)
            add_option_button = QPushButton("Add Option", self)
            add_option_button.clicked.connect(
                partial(self.add_option, parent, "New Option", False, button_child)
            )
            self.setItemWidget(button_child, 0, add_option_button)
        parent.setExpanded(True)
        self.invisibleRootItem().insertChild(1, parent)
        return parent

    def add_option(
        self, parent: QTreeWidgetItem, option: str = "", checked: bool = False, button_child: QTreeWidgetItem = None
    ):
        self.blockSignals(True)
        child = QTreeWidgetItem(parent)
        child.setText(0, option)
        child.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable)
        parent.insertChild(0, child)
        if button_child is not None:
            parent.removeChild(button_child)
            button_child = QTreeWidgetItem(parent)
            add_option_button = QPushButton("Add Option", self)
            add_option_button.clicked.connect(
                partial(self.add_option, parent, "New Option", False, button_child)
            )
            self.setItemWidget(button_child, 0, add_option_button)
        self.blockSignals(False)

    def update_answer(self, item: QTreeWidgetItem, column: int):
        if item.parent() is None:
            return
        self.blockSignals(True)
        if item.checkState(0) == Qt.CheckState.Checked:
            self.uncheck_other_options(item.parent(), item)
        item = item.parent()

        for row in range(item.childCount()):
            child = item.child(row)
            if child.checkState(0) == Qt.CheckState.Checked:
                item.setText(1, child.text(0))
                break
        self.blockSignals(False)

    def uncheck_other_options(self, question: QTreeWidgetItem, selected_item: QTreeWidget):
        for i in range(question.childCount() - 1):  # Exclude the last child (Add Option button)
            child = question.child(i)
            if child != selected_item and child.checkState(0) == Qt.CheckState.Checked:
                child.setCheckState(0, Qt.CheckState.Unchecked)

    def openMenu(self, position):
        selected = self.itemAt(position)
        menu = QMenu()
        if selected:
            remove_action = QAction("Remove", self)
            remove_action.triggered.connect(lambda: self.removeSelectedItem(selected))
            menu.addAction(remove_action)
        menu.exec(self.viewport().mapToGlobal(position))

    def removeSelectedItem(self, item: QTreeWidgetItem):
        root = self.invisibleRootItem()
        (item.parent() or root).removeChild(item)

    def load_data(self, data: dict[str, dict[str, bool]]):
        self.clear()
        top = QTreeWidgetItem(self)
        self.addTopLevelItem(top)
        add_question_button = QPushButton("Add Question", self)
        add_question_button.clicked.connect(partial(self.add_question, "New Question", "New Question", True))
        self.setItemWidget(top, 0, add_question_button)

        for question, question_data in data.items():
            answer = next((option for option, value in question_data.items() if value), None)
            parent = self.add_question(question, answer)
            for option in question_data.keys():
                self.add_option(parent, option, question_data[option], None)
            button_child = QTreeWidgetItem(parent)
            add_option_button = QPushButton("Add Option", self)
            add_option_button.clicked.connect(
                partial(self.add_option, parent, "New Option", False, button_child)
            )
            self.setItemWidget(button_child, 0, add_option_button)

    def get_tree_data(self) -> dict[str, dict[str, bool]]:
        data = {}
        root = self.invisibleRootItem()
        for question_index in range(root.childCount()):
            question_item = root.child(question_index)
            question_text = question_item.text(0)
            if isinstance(question_item, QPushButton) or question_text == "":
                continue
            options: dict[str, bool] = {}
            for option_index in range(question_item.childCount()):
                option_item = question_item.child(option_index)
                option_text = option_item.text(0)
                if isinstance(option_item, QPushButton) or option_text == "":
                    continue
                options[option_text] = True if option_item.checkState(0) == Qt.CheckState.Checked else False
            data[question_text] = options
        return data
