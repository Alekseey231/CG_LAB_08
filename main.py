import asyncio
import os
import sys
import time
from typing import List

import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPen, QTransform, QPainter, QPixmap, QColor, QImage
from PyQt5.QtWidgets import QGraphicsScene, QTableWidgetItem, QMessageBox, QLabel, QApplication, QTableWidget, \
    QColorDialog, QAction
from fontTools.pens.qtPen import QtPen

from alg import otsek_all, brezenhem_int, NOT_VISIBLE
from design_all import Ui_MainWindow


def create_error_window(title, message):
    error = QMessageBox()
    error.setWindowTitle(title)
    error.setText(message)
    error.exec()


class Main_window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.scene = QGraphicsScene()
        self.graphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.pointSignal.connect(self.add_point)
        self.graphicsView.endSignal.connect(self.complete_polygon)
        self.graphicsView.keySignal.connect(self.key_press)
        self.graphicsView.middleSignal.connect(self.add_seed_point)

        self.pen = QPen()
        self.color = QColor(Qt.green)

        self.l_choosen_color.setStyleSheet("background-color: green")
        self.l_choosen_color.clicked.connect(self.set_color)

        self.setup_toolbar()

        self.image = self.graphicsView.image
        self.image.fill(Qt.white)
        transform = QTransform()
        transform.translate(self.image.width() / 2,
                            self.image.height() / 2)  # смещение начала координат в центр изображения
        transform.scale(1, -1)  # инвертируем ось Y
        self.transform = transform
        self.p = QPainter()
        self.p.begin(self.image)
        self.p.setTransform(self.transform)
        self.p.setBrush(Qt.black)
        self.scene.addPixmap(QPixmap.fromImage(self.image))
        self.p.end()

        self.current_polygon = []
        self.all_polygon = []
        self.count_poly = 0
        self.cur_label = []
        self.current_line = []
        self.all_line = []

        self.seed_pixel = None

        self.init_table()

        self.black = QColor(0, 0, 0)
        self.green = QColor(0, 255, 0)
        self.blue = QColor(0, 0, 255)

        self.p_fill.clicked.connect(self.fill)

        self.b_clear.clicked.connect(self.clear_scene)
        self.b_del_sides.clicked.connect(self.clear_sides)
        self.b_del_cutter.clicked.connect(self.clear_cutter)
        self.b_choose_color.clicked.connect(self.set_color)
        self.b_add_point.clicked.connect(self.get_point)
        self.b_add_point_2.clicked.connect(self.set_seed_pixel)

    def clear_sides(self):
        try:
            self.image.fill(Qt.white)
            if len(self.all_polygon) == 0 or len(self.all_polygon[0]) == 0:
                pass
            else:
                for i in range(1, len(self.all_polygon[0])):
                    self.draw_line(self.all_polygon[0][i - 1], self.all_polygon[0][i], self.blue)

            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(self.image))
            self.all_line = []
            self.current_line = []
        except Exception as e:
            print(e)

    def clear_cutter(self):
        if len(self.all_polygon) == 0 or len(self.all_polygon[0]) == 0:
            create_error_window("Error!\n", "Отсекатель не добавлен на сцену")
            return
        try:
            self.image.fill(Qt.white)
            for i in range(len(self.all_line)):
                self.draw_line(self.all_line[i][0], self.all_line[i][1], self.black)
            self.tableWidget.setRowCount(0)
            self.scene.clear()
            self.scene.addPixmap(QPixmap.fromImage(self.image))
            self.all_polygon = []
            self.current_polygon = []
        except Exception as e:
            print(e)

    def set_seed_pixel(self):
        try:
            x = int(self.l_seed_x.text())
            y = int(self.l_seed_y.text())
            self.add_seed_point(QPoint(x, y))
        except Exception as e:
            create_error_window("Error!", "Некорретный ввод")
        else:
            self.l_seed_x.setText("")
            self.l_seed_y.setText("")

    def add_seed_point(self, point: QPoint):
        if len(self.all_polygon) == 1:
            create_error_window("Error!", "Возможен только 1 отсекатель")
            return

        if len(self.current_polygon) == 0:
            self.count_poly += 1
            self.cur_label.append("")
            self.add_row("Отсекатель", "")
            self.tableWidget.setSpan(self.tableWidget.rowCount() - 1, 0, 1, 2)
            self.tableWidget.setVerticalHeaderLabels(self.cur_label)

        if len(self.current_polygon) > 0 and self.current_polygon[-1] == point:
            return

        self.current_polygon.append(point)
        self.cur_label.append(str(len(self.current_polygon)))
        self.add_row(point.x(), point.y())
        self.tableWidget.setVerticalHeaderLabels(self.cur_label)
        if len(self.current_polygon) == 1:
            try:
                self.draw_point(point, self.blue)
            except Exception as e:
                print(e)
        else:
            try:
                self.draw_line(self.current_polygon[-1], self.current_polygon[-2], self.blue)
            except Exception as e:
                print("11", e)
        if len(self.current_polygon) > 3 and self.current_polygon[-1] == self.current_polygon[0]:
            self.all_polygon.append(self.current_polygon)
            self.current_polygon = []

    def get_point(self):
        try:
            x = int(self.l_x.text())
            y = int(self.l_y.text())
        except Exception as e:
            create_error_window("Error!", "Некорретный ввод")
        else:
            self.l_x.setText("")
            self.l_y.setText("")
            self.add_point(QPoint(x, y))

    def set_color(self):
        color = QColorDialog.getColor()

        if color.isValid():
            self.l_choosen_color.setStyleSheet("background-color: {}".format(color.name()))
            self.color = color

    def init_table(self):
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["x", "y"])

        self.tableWidget.horizontalHeaderItem(0).setToolTip("Column 1 ")
        self.tableWidget.horizontalHeaderItem(1).setToolTip("Column 2 ")
        self.tableWidget.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        self.tableWidget.horizontalHeaderItem(1).setTextAlignment(Qt.AlignRight)

    def clear_scene(self):
        self.image.fill(Qt.white)
        self.tableWidget.setRowCount(0)
        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(self.image))
        self.current_polygon = []
        self.all_polygon = []
        self.cur_label = []
        self.current_line = []
        self.all_line = []
        self.count_poly = 0
        self.seed_pixel = None

    def fill(self):
        if len(self.all_polygon) == 0:
            create_error_window("Error!", "Необходимо задать хотя бы 1 отсекатель")
            return
        res = otsek_all(self.all_line, self.all_polygon[0])
        if res == -1:
            create_error_window("Error!", "Отсекатель должен быть выпуклым многоугольником!")
            return
        self.image.fill(Qt.white)
        for i in range(len(res)):
            if res[i] != NOT_VISIBLE:
                #print(self.all_line[i], res[i])
                if self.all_line[i][0] == res[i][0] and self.all_line[i][1] == res[i][1]:
                    self.draw_line(res[i][0], res[i][1], self.green)
                else:
                    self.draw_line(self.all_line[i][0], res[i][0], self.black)
                    self.draw_line(res[i][0], res[i][1], self.green)
                    if self.all_line[i][1] != res[i][1]:
                        self.draw_line(res[i][1], self.all_line[i][1], self.black)
            else:
                self.draw_line(self.all_line[i][0], self.all_line[i][1], self.black)
        for i in range(1, len(self.all_polygon[0])):
            self.draw_line(self.all_polygon[0][i-1], self.all_polygon[0][i], self.blue)
        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(self.image))

    def add_row(self, num1, num2):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(str(num1)))
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QTableWidgetItem(str(num2)))

    # shift - вертикальное ребро
    def key_press(self, point: QPoint, sign_type: int):
        try:
            if len(self.current_polygon) > 0:
                if sign_type == 0:
                    point = QPoint(self.current_polygon[-1].x(), point.y())
                else:
                    point = QPoint(point.x(), self.current_polygon[-1].y())
            self.add_point(point)
        except Exception as e:
            #print(point)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

    def add_point(self, point: QPoint):
        self.current_line.append(point)
        try:
            if len(self.current_line) == 1:
                try:
                    self.draw_point(point, self.black)
                except Exception as e:
                    print(e)
            else:
                self.draw_line(self.current_line[-1], self.current_line[-2], self.black)
                self.all_line.append(self.current_line)
                self.current_line = []
                #print(self.all_line)
        except Exception as e:
            print(e)

    def complete_polygon(self, int):
        if len(self.current_polygon) < 3:
            create_error_window("Error!", "Полигон должен состоять минимум из 3-х точек!")
        else:
            self.current_polygon.append(self.current_polygon[0])
            self.draw_line(self.current_polygon[-1], self.current_polygon[-2], self.blue)
            self.all_polygon.append(self.current_polygon)
            self.current_polygon = []

    def draw_point(self, point: QPoint, color):
        self.image.setPixel(round(point.x()) + self.image.width() // 2, round(point.y()) * -1 + self.image.width() // 2,
                            color.rgb())

        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(self.image))

    def draw_line(self, start_point: QPoint, end_point: QPoint, color):

        #self.my_draw_line(start_point, end_point, color)
        self.p.begin(self.image)
        self.p.setTransform(self.transform)
        self.pen.setColor(color)
        self.p.setPen(self.pen)

        self.p.drawLine(start_point, end_point)
        self.scene.clear()

        self.scene.addPixmap(QPixmap.fromImage(self.image))

        self.p.end()

        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(self.image))
        self.p.end()

    def my_draw_line(self, start_point, end_point, color):
        all_points = brezenhem_int(start_point, end_point)
        for point in all_points:
            self.image.setPixel(round(point[0]) + self.image.width() // 2,
                                (round(point[1]) * -1 + self.image.width() // 2),
                                color.rgb())

    def get_time(self):
        self.comboBox.setCurrentIndex(0)
        start_time = time.time()
        self.fill()
        end_time = time.time()
        try:
            create_error_window("Замеры времени: ", "{:.3f}".format(end_time - start_time))
        except Exception as e:
            print(e)

    def setup_toolbar(self):
        close = QAction('О программе', self)
        close.triggered.connect(self.about_program)
        self.toolbar = self.addToolBar("О программе")
        self.toolbar.addAction(close)

        close = QAction('Об авторе', self)
        close.triggered.connect(self.about_author)
        self.toolbar = self.addToolBar("Об авторе")
        self.toolbar.addAction(close)

        close = QAction('Справка', self)
        close.triggered.connect(self.info)
        self.toolbar = self.addToolBar("Справка")
        self.toolbar.addAction(close)

        close = QAction('Закрыть', self)
        close.triggered.connect(self.close)
        self.toolbar = self.addToolBar("Закрыть")
        self.toolbar.addAction(close)

    def about_author(self):
        create_error_window("Об авторе", "Толмачев Алексей; ИУ7-45B")

    def about_program(self):
        create_error_window("О программе",
                            "Реализован алгоритм заполнения области по ребрам")

    def info(self):
        create_error_window("Справка",
                            "1) Ввод точек на графическую сцену осуществляется с помощью левой кнопки мыши или с помощью "
                            "ввода в соответствующие поля координат в интерфейсе\n "
                            "2) С помощью правой кнопки мыши можно замкнуть область\n"
                            "3) Для того, чтобы построить вертикальное ребро - после ввода точки нужно удерживать "
                            "shift при вводе следующей точки\n"
                            "4) Для построения горизонтального ребра нужно удерживать Ctrl при вводе следующей точки\n")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = Main_window()
    form.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
