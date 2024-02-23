from PyQt6 import uic
from PyQt6.QtCore import QFile, Qt, QTextStream
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtWidgets import QDialog

from utils.icons import Icons

from utils import globals


class AboutDialog(QDialog):
    def __init__(self, parent):
        super(AboutDialog, self).__init__(parent)
        uic.loadUi("ui/about_dialog.ui", self)
        self.setWindowIcon(QIcon(Icons.app_icon))
        pixmap = QPixmap(Icons.app_icon)
        self.lblIcon.setFixedSize(200, 200)
        scaled_pixmap = pixmap.scaled(
            self.lblIcon.size(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self.lblIcon.setPixmap(scaled_pixmap)
        license_file = QFile("LICENSE")
        if license_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(license_file)
            license = stream.readAll()
            license_file.close()
            self.textEdit_2.setText(license)
        about_file = QFile("README.md")
        if about_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(about_file)
            about = stream.readAll()
            about_file.close()
            self.textEdit.setHtml(about)
        self.lblTitle.setText(f"{globals.__version__}")
        self.lblHome.setText(
            "Home: <a style='text-decoration:none; color:blue;'href='https://github.com/TheCodingJsoftware/Gradiance'>https://github.com/TheCodingJsoftware/Gradiance</a>"
        )
        self.btnClose.clicked.connect(self.close)
