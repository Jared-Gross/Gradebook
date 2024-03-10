import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QMainWindow,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "QTreeWidget with Editable Options, Add Option Button, and Answer Column"
        )
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Select", "Question/Option", "Answer"])
        self.layout.addWidget(self.treeWidget)

        self.treeWidget.setEditTriggers(QTreeWidget.EditTrigger.DoubleClicked)
        self.treeWidget.setColumnWidth(
            0, 50
        )  # Adjust as needed for checkbox visibility

        # Initially add a question with an option
        self.initialSetup()

    def initialSetup(self):
        questionItem = self.addQuestion("Sample Question")
        self.addOption(questionItem, "Option 1")
        self.addAddOptionButton(questionItem)

    def addQuestion(self, questionText):
        questionItem = QTreeWidgetItem(self.treeWidget)
        questionItem.setFlags(questionItem.flags() | Qt.ItemFlag.ItemIsEditable)
        questionItem.setText(1, questionText)  # Set question text in the second column
        return questionItem

    def addOption(self, questionItem, optionText):
        optionItem = QTreeWidgetItem(questionItem)
        optionItem.setFlags(
            optionItem.flags()
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsUserCheckable
        )
        optionItem.setText(1, optionText)  # Set option text in the second column
        optionItem.setCheckState(
            0, Qt.CheckState.Unchecked
        )  # Add checkbox in the first column

        # Avoid directly connecting to updateAnswer to prevent argument issues.
        # Instead, handle state changes individually.
        optionItem.checkStateChangeHandled = (
            False  # Custom attribute to prevent recursion.
        )

    def setupConnections(self):
        # Connect itemChanged signal globally, handle logic inside the slot
        self.treeWidget.itemChanged.connect(self.handleItemChanged)

    def handleItemChanged(self, item, column):
        if column == 0:  # Only proceed if the change happened in the checkbox column
            questionItem = item.parent()
            if questionItem:
                selectedOptions = []
                for i in range(
                    questionItem.childCount() - 1
                ):  # Exclude the Add Option button
                    child = questionItem.child(i)
                    if child.checkState(0) == Qt.CheckState.Checked:
                        selectedOptions.append(child.text(1))

                # Update the answer column with all selected options
                questionItem.setText(2, ", ".join(selectedOptions))

    def addAddOptionButton(self, questionItem):
        buttonItem = QTreeWidgetItem(questionItem)
        button = QPushButton("Add Option")
        button.clicked.connect(
            lambda: self.onAddOptionClicked(questionItem, buttonItem)
        )
        self.treeWidget.setItemWidget(buttonItem, 1, button)

    def onAddOptionClicked(self, questionItem, buttonItem):
        self.addOption(questionItem, "New Option")
        questionItem.removeChild(buttonItem)  # Remove the button item temporarily
        self.addAddOptionButton(questionItem)  # Re-add the button item
        self.treeWidget.expandItem(questionItem)  # Ensure the question item is expanded

    def updateAnswer(self, questionItem):
        # Temporarily disconnect the itemChanged signal to avoid recursion
        self.treeWidget.itemChanged.disconnect()

        # Reset the answer column for the question
        questionItem.setText(2, "")
        for i in range(questionItem.childCount() - 1):  # Exclude the Add Option button
            child = questionItem.child(i)
            if child.checkState(0) == Qt.CheckState.Checked:
                questionItem.setText(2, child.text(1))  # Update the answer column
                break  # Assuming only one answer can be selected

        # Reconnect the itemChanged signal after updates
        self.treeWidget.itemChanged.connect(lambda _: self.updateAnswer(questionItem))

        self.uncheckOtherOptions(questionItem)

    def uncheckOtherOptions(self, questionItem, selectedOptionItem):
        for i in range(
            questionItem.childCount() - 1
        ):  # Exclude the last child (Add Option button)
            child = questionItem.child(i)
            if (
                child != selectedOptionItem
                and child.checkState(0) == Qt.CheckState.Checked
            ):
                child.setCheckState(0, Qt.CheckState.Unchecked)
                self.updateAnswer(questionItem)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
