import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image = self.map_file = self.scale = self.pixmap = self.coords = None
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
            'l': 'map'
        }
        link = 'http://static-maps.yandex.ru/1.x/'

        response = requests.get(link, search_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            quit()

        self.map_file = f"map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.coords = "35.91184997558594,56.85956192016602"
        self.scale = 1

        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Задание 1')
        self.get_image(self.coords, self.scale)

        self.pixmap = QPixmap('map.png')
        self.image = QLabel(self)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

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
            self.coords = ','.join(coords)
        elif event.key() == Qt.Key_Right:
            coords = self.coords.split(',')
            step = 360 / pow(2, self.scale)
            coords[0] = str(float(coords[0]) + abs(step))
            if abs(float(coords[0])) >= 180:
                return
            self.coords = ','.join(coords)
        elif event.key() == Qt.Key_Up:
            coords = self.coords.split(',')
            step = 180 / pow(2, self.scale)
            coords[1] = str(float(coords[1]) + abs(step))
            if abs(float(coords[1])) >= 90:
                return
            self.coords = ','.join(coords)
        elif event.key() == Qt.Key_Down:
            coords = self.coords.split(',')
            step = 180 / pow(2, self.scale)
            coords[1] = str(float(coords[1]) - abs(step))
            if abs(float(coords[1])) >= 90:
                return
            self.coords = ','.join(coords)

        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap('map.png'))

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove('map.png')


def except_hook(cls, exception, traceback):
    sys.excepthook(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = except_hook
    ex = Example()
    ex.show()
    sys.exit(app.exec())
