import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QMenu,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction


class MultiRowTabWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tab_buttons = []
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBarDoubleClicked.connect(self.on_tab_double_clicked)

        self.tabs_layout = QVBoxLayout()
        self.tabs_layout.addWidget(self.tab_widget)

        self.tab_buttons_layout = QHBoxLayout()
        self.tabs_layout.addLayout(self.tab_buttons_layout)

        self.setLayout(self.tabs_layout)

    def add_tab(self, widget, title):
        index = self.tab_widget.addTab(widget, title)
        button = QPushButton(title)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.clicked.connect(lambda: self.tab_widget.setCurrentIndex(index))
        button.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )  # CustomContextMenu policy
        button.customContextMenuRequested.connect(
            lambda point: self.show_menu(point, button)
        )
        self.tab_buttons.append(button)
        self.update_buttons_layout()

    def remove_tab(self, index):
        self.tab_widget.removeTab(index)
        button = self.tab_buttons.pop(index)
        button.deleteLater()
        self.update_buttons_layout()

    def on_tab_double_clicked(self, index):
        self.tab_widget.removeTab(index)

    def show_menu(self, point, button):
        menu = QMenu(self)
        close_action = menu.addAction("Close")
        action = menu.exec(button.mapToGlobal(point))
        if action == close_action:
            index = self.tab_buttons.index(button)
            self.remove_tab(index)

    def update_buttons_layout(self):
        # Clear the layout
        # Add buttons back in the appropriate rows
        row_layout = QHBoxLayout()
        for button in self.tab_buttons:
            row_layout.addWidget(button)
            if row_layout.sizeHint().width() > self.width():
                # Move to a new row
                self.tab_buttons_layout.addLayout(row_layout)
                row_layout = QHBoxLayout()
        # Add the last row if it's not empty
        if row_layout.count() > 0:
            self.tab_buttons_layout.addLayout(row_layout)


class Example(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.multi_row_tab_widget = MultiRowTabWidget()
        layout.addWidget(self.multi_row_tab_widget)

        self.add_button = QPushButton("Add Tab")
        self.add_button.clicked.connect(self.add_tab)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_tab(self):
        new_tab = QWidget()
        title = f"Tab {self.multi_row_tab_widget.tab_widget.count() + 1}"
        self.multi_row_tab_widget.add_tab(new_tab, title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    example = Example()
    example.show()
    sys.exit(app.exec())
