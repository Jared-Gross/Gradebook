from PyQt6.QtCore import Qt
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QFrame, QLabel, QWidget

from utils import globals


class GradeLetters(QWidget):
    def __init__(self, parent=None):
        super(GradeLetters, self).__init__(parent)
        self.labels: list[QLabel] = []
        self.vertical_lines: list[QFrame] = []
        for letter in globals.grade_ranges:
            label = QLabel(letter[1], self)
            label.setFixedSize(30, 30)
            label.setAlignment(
                Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter
            )
            self.labels.append(label)
            vertical_line = QFrame(self)
            vertical_line.setFrameShape(QFrame.Shape.VLine)
            vertical_line.setFrameShadow(QFrame.Shadow.Sunken)
            self.vertical_lines.append(vertical_line)

    def resizeEvent(self, event: QResizeEvent) -> None:
        positions = [
            int(position[0] / 100 * self.width()) for position in globals.grade_ranges
        ]
        for label, vertical_line, pos in zip(
            self.labels, self.vertical_lines, positions
        ):
            if self.width() < 200:
                if label.text() in ["C-", "C", "C+", "B-", "B", "B+", "A-", "A+"]:
                    label.setHidden(True)
                    vertical_line.setHidden(True)
            elif 200 <= self.width() < 500:
                if label.text() in ["C-", "C+", "B-", "B+", "A-", "A+"]:
                    label.setHidden(True)
                    vertical_line.setHidden(True)
                else:
                    label.setHidden(False)
                    vertical_line.setHidden(False)
            else:
                label.setHidden(False)
                vertical_line.setHidden(False)
            if label.text() == "F":
                label.move(pos - 5, 0)
                vertical_line.setGeometry(pos + int(label.width() / 2) - 5, 30, 1, 20)
            else:
                label.move(pos - 15, 0)
                vertical_line.setGeometry(pos + int(label.width() / 2) - 15, 30, 1, 20)
