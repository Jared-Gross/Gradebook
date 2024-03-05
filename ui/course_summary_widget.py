import contextlib
import math
import random
from statistics import linear_regression

import numpy as np
import pyqtgraph as pg
import qt_material
from natsort import natsorted
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction, QColor
from PyQt6.QtWidgets import (QAbstractScrollArea, QHeaderView, QMenu,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QToolBox, QVBoxLayout, QWidget)
from pyqtgraph import (AxisItem, GraphicsLayout, InfiniteLine, PlotDataItem,
                       ScatterPlotItem, TextItem)

from utils.course import Course
from utils.student import Student


class CourseSummaryWidget(QWidget):
    def __init__(self, course: Course, parent) -> None:
        super(CourseSummaryWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.course = course
        self.parent = parent
        self.settings = QSettings("TheCodingJ's", "Gradiance", self)

        pg.setConfigOptions(antialias=True)

        self.data = {}
        self.load_data()
        self.load_graphs()
        self.setLayout(self.layout)

    def load_data(self):
        self.data.clear()
        for assessment in self.course.assessments:
            self.data[assessment] = {}
            for student in self.course.assessments[assessment]:
                self.data[assessment][student] = {"x": [], "y": []}
                for i, assignment in enumerate(
                    self.course.assessments[assessment][student]
                ):
                    self.data[assessment][student]["x"].append(i)
                    self.data[assessment][student]["y"].append(
                        assignment.get_percentage()
                    )

    def get_all_assignment_names(self, assessment: str) -> list[str]:
        assignemnts = set()
        for student in self.course.assessments[assessment]:
            for assignment in self.course.assessments[assessment][student]:
                assignemnts.add(assignment.template.name)
        return list(assignemnts)

    def load_graphs(self):
        self.clear_layout(self.layout)
        self.theme = qt_material.get_theme(
            self.settings.value(f"{self.parent.school.name} - theme", "dark_teal.xml")
        )
        primary_color = self.theme["primaryColor"]
        secondary_color = self.theme["secondaryColor"]
        self.win: GraphicsLayout = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle("Assessments")
        self.win.ci.setBorder(primary_color)
        self.win.setBackground(secondary_color)
        self.layout.addWidget(self.win)
        max_x_range = 0
        max_y_range = 0
        for assessment in self.data:
            assignment_names = natsorted(self.get_all_assignment_names(assessment))

            x_dict = {name: int(index) for index, name in enumerate(assignment_names)}

            plot = self.win.addPlot(title=assessment)
            plot.addLegend()
            plot.showGrid(x=True, y=True)
            plot.setLabel("left", text="Percentage (%)")
            pass_line = InfiniteLine(
                angle=0,
                pen="w",
                label="Passed",
                labelOpts={
                    "fill": (100, 200, 100, 50),
                },
            )
            pass_line.setPen((100, 200, 100))
            pass_line.setValue((0, 50))
            plot.addItem(pass_line)
            for student in self.data[assessment]:
                x_values = self.data[assessment][student]["x"]
                y_values = self.data[assessment][student]["y"]
                if len(x_values) > 1:
                    if max(y_values) > max_y_range:
                        max_y_range = max(y_values)
                        plot.setYRange(0, max_y_range)
                    if len(x_values) > max_x_range:
                        max_x_range = len(x_values)
                        plot.setXRange(0, max_x_range + 1)
                    slope, intercept = linear_regression(x_values, y_values)
                    angle_radians = np.arctan(slope)
                    angle_degrees = np.degrees(angle_radians)
                    inf3 = InfiniteLine(
                        angle=angle_degrees,
                        pen="w",
                        label="LinReg",
                        labelOpts={
                            "rotateAxis": [1, 0],
                            "fill": (200, 200, 200, 50),
                        },
                    )
                    inf3.setValue((0, intercept))
                    plot.addItem(inf3)

                pen = pg.mkPen(color=student.color)
                for i, (x, y) in enumerate(zip(x_values, y_values)):
                    text = TextItem(text=str(i + 1), color=pen.color())
                    text.setPos(x, y)
                    plot.addItem(text)
                plot.plot(x=x_values, y=y_values, name=student.name, pen=pen)
                scatter = ScatterPlotItem(
                    size=10, pen=pen, brush=pen.color(), hoverable=True, hoverSymbol="s"
                )
                scatter.addPoints(x=x_values, y=y_values, data=student.name)
                plot.addItem(scatter)
            axis_left: AxisItem = plot.getAxis("left")
            axis_bottom = plot.getAxis("bottom")
            axis_bottom.setTicks(
                [[(i, str(name[0])) for i, name in enumerate(x_dict.items())]]
            )  # Adjust the range and step as needed

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
