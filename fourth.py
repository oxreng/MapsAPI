import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def get_coords(self, coords, scale):
        if scale > 21:
            scale = 21
        elif scale <= 0:
            scale = 1
        scale = int(scale)

        if scale == 1 or scale == 0:
            coords = f'{self.coords.split(",")[0]},0'
        return coords, scale

    def get_image(self, coords, scale):
        coords, scale = self.get_coords(coords, scale)

        search_params = {
            'll': coords,
            'z': scale,
            'l': self.cur_map_type
        }
        link = 'http://static-maps.yandex.ru/1.x/'

        response = requests.get(link, search_params)

        if not response:
            return 'Error'

        self.map_file = f"map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.coords = "35.91184997558594,56.85956192016602"
        self.scale = 1

        self.cur_map_type = 'map'
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Задание 4')
        self.get_image(self.coords, self.scale)

        # Изображение
        self.pixmap = QPixmap('map.png')
        self.image = QLabel(self)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

        self.combobox = Combo(self)
        self.combobox.move(480, 10)
        self.combobox.resize(110, 20)
        self.combobox.addItems(('Карта', 'Спутник', 'Гибрид'))
        self.combobox.textHighlighted.connect(self.change_map_type)

    def change_map_type(self, text):
        translate = {'Карта': 'map', 'Спутник': 'sat', 'Гибрид': 'sat,skl'}
        self.cur_map_type = translate[text]
        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap(self.map_file))
        self.combobox.setCurrentIndex(self.combobox.findText(text))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.scale < 21:
            self.scale += 1
        elif event.key() == Qt.Key_PageDown and self.scale > 0:
            self.scale -= 1
        elif event.key() == Qt.Key_Left:
            coords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            coords[0] = str(float(coords[0]) - abs(step))
            if abs(float(coords[0])) >= 180:
                return
        elif event.key() == Qt.Key_Right:
            coords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            coords[0] = str(float(coords[0]) + abs(step))
            if abs(float(coords[0])) >= 180:
                return
        elif event.key() == Qt.Key_Up:
            coords = self.coords.split(',')
            step = 180 / pow(2, self.scale)
            coords[1] = str(float(coords[1]) + abs(step))
            if abs(float(coords[1])) >= 90:
                return
        elif event.key() == Qt.Key_Down:
            coords = self.coords.split(',')
            step = 180 / pow(2, self.scale)
            coords[1] = str(float(coords[1]) - abs(step))
            if abs(float(coords[1])) >= 90:
                return
        if event.key() in (Qt.Key_Down, Qt.Key_Up, Qt.Key_Right, Qt.Key_Left):
            if self.get_image(','.join(coords), self.scale) != 'Error':
                self.coords = ','.join(coords)
        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap('map.png'))

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove('map.png')


class Combo(QComboBox):
    def keyPressEvent(self, event):
        ex.keyPressEvent(event)


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = Example()
    ex.show()
    sys.exit(app.exec())
