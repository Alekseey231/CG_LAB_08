from typing import List, Union

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPointF, QEvent
from PyQt5.QtGui import QTransform, QImage, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView, QApplication, QLabel, QTableWidget


class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()

    clicked = QtCore.pyqtSignal()


class CustomGraphicsView(QGraphicsView):
    pointSignal = pyqtSignal(QPoint)
    endSignal = pyqtSignal(int)
    keySignal = pyqtSignal(QPoint, int)
    middleSignal = pyqtSignal(QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_x = None
        self.last_y = None
        self.last_mouse_pos = None
        self.image = QImage(3000, 3000, QImage.Format_ARGB32)
        self.image.fill(Qt.white)
        self.zoom = 0
        self.setTransform(QTransform().scale(1, -1))
        self.shift_pressed = False
        # self.installEventFilter(self)
        self.setMouseTracking(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.last_point = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.centerOn(self.image.width() / 2, self.image.height() / 2)

    def wheelEvent(self, event):
        super().wheelEvent(event)
        self.centerOn(self.image.width() / 2, self.image.height() / 2)
        event.ignore()

    def mapToScene(self, pos):
        old_center = self.viewport().rect().center()
        pos_scene = super().mapToScene(pos)
        new_center = self.viewport().rect().center()
        offset = new_center - old_center
        pos_scene += offset
        return pos_scene

    def mousePressEvent(self, event):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
            pos_scene = self.mapToScene(event.pos())
            pos_view = self.mapFromScene(pos_scene)
            center = self.viewport().rect().center()
            diff = pos_view - center
            if event.button() == Qt.MiddleButton:
                self.middleSignal.emit(diff)
            else:
                try:
                    if modifiers == QtCore.Qt.ShiftModifier:
                        self.keySignal.emit(diff, 0)
                    elif modifiers == QtCore.Qt.ControlModifier:
                        self.keySignal.emit(diff, 1)
                    else:
                        self.pointSignal.emit(diff)
                except Exception as e:
                    print(e)
            event.accept()
        elif event.button() == Qt.RightButton:
            self.endSignal.emit(0)
        else:
            super().mousePressEvent(event)


class MyTable(QTableWidget):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)

    def printSelection(self):
        ranges = self.selectedRanges()
        return ranges


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(754, 629)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setMinimumSize(QtCore.QSize(230, 0))
        self.widget.setMaximumSize(QtCore.QSize(250, 16777215))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = MyTable(0, 0)
        self.tableWidget.setMinimumSize(QtCore.QSize(230, 0))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.l_x = QtWidgets.QLineEdit(self.groupBox)
        self.l_x.setObjectName("l_x")
        self.horizontalLayout_2.addWidget(self.l_x)
        self.l_y = QtWidgets.QLineEdit(self.groupBox)
        self.l_y.setObjectName("l_y")
        self.horizontalLayout_2.addWidget(self.l_y)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.b_add_point = QtWidgets.QPushButton(self.groupBox)
        self.b_add_point.setObjectName("b_add_point")
        self.verticalLayout_2.addWidget(self.b_add_point)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_3 = QtWidgets.QGroupBox(self.widget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.l_seed_x = QtWidgets.QLineEdit(self.groupBox_3)
        self.l_seed_x.setObjectName("l_seed_x")
        self.horizontalLayout_3.addWidget(self.l_seed_x)
        self.l_seed_y = QtWidgets.QLineEdit(self.groupBox_3)
        self.l_seed_y.setObjectName("l_seed_y")
        self.horizontalLayout_3.addWidget(self.l_seed_y)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.b_add_point_2 = QtWidgets.QPushButton(self.groupBox_3)
        self.b_add_point_2.setObjectName("b_add_point_2")
        self.verticalLayout_4.addWidget(self.b_add_point_2)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.p_fill = QtWidgets.QPushButton(self.widget)
        self.p_fill.setObjectName("p_fill")
        self.verticalLayout.addWidget(self.p_fill)
        self.b_clear = QtWidgets.QPushButton(self.widget)
        self.b_clear.setObjectName("b_clear")
        self.verticalLayout.addWidget(self.b_clear)
        self.b_del_cutter = QtWidgets.QPushButton(self.widget)
        self.b_del_cutter.setObjectName("b_del_cutter")
        self.verticalLayout.addWidget(self.b_del_cutter)
        self.b_del_sides = QtWidgets.QPushButton(self.widget)
        self.b_del_sides.setObjectName("b_del_sides")
        self.verticalLayout.addWidget(self.b_del_sides)
        self.horizontalLayout.addWidget(self.widget)
        self.graphicsView = CustomGraphicsView(self.centralwidget)
        self.graphicsView.setMinimumSize(QtCore.QSize(500, 0))
        self.graphicsView.setObjectName("graphicsView")
        self.horizontalLayout.addWidget(self.graphicsView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 754, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Добавление точки отрезка"))
        self.b_add_point.setText(_translate("MainWindow", "Добавить точку"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Добавление точки отсекателя"))
        self.b_add_point_2.setText(_translate("MainWindow", "Добавить точку"))
        self.p_fill.setText(_translate("MainWindow", "Отсечь"))
        self.b_clear.setText(_translate("MainWindow", "Очистить сцену"))
        self.b_del_cutter.setText(_translate("MainWindow", "Удалить отсекатель"))
        self.b_del_sides.setText(_translate("MainWindow", "Удалить отрезки"))
