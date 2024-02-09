import math
import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QPushButton, QTextBrowser, \
    QCheckBox
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 520]


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
        if self.now_point[0]:
            search_params['pt'] = self.now_point
        link = 'http://static-maps.yandex.ru/1.x/'

        response = requests.get(link, search_params)

        if not response:
            return 'Error'

        self.map_file = f"map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.text_to_adress.setText(self.now_point[1])

    def initUI(self):
        self.coords = "35.91184997558594,56.85956192016602"
        self.scale = 1
        self.now_point = ('', '', '')
        self.image_x, self.image_y = 600, 450

        self.cur_map_type = 'map'
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Задание 11')

        self.image = QLabel(self)
        self.image.resize(600, 450)

        self.combobox = Combo(self)
        self.combobox.move(480, 10)
        self.combobox.resize(110, 20)
        self.combobox.addItems(('Карта', 'Спутник', 'Гибрид'))
        self.combobox.textHighlighted.connect(self.change_map_type)

        self.lineedit = QLineEdit(self)
        self.lineedit.setPlaceholderText('Введите место поиска здесь')
        self.lineedit.move(200, 455)
        self.lineedit.resize(190, 25)

        self.text_to_adress = QTextBrowser(self)
        self.text_to_adress.setPlaceholderText('Адрес объекта')
        self.text_to_adress.move(10, 475)
        self.text_to_adress.resize(180, 30)

        self.btn_lineedit = QPushButton('Найти', self)
        self.btn_lineedit.move(200, 480)
        self.btn_lineedit.resize(190, 25)
        self.btn_lineedit.clicked.connect(self.btn_lineedit_click)

        self.btn_reset = QPushButton('Сброс поиска', self)
        self.btn_reset.move(500, 480)
        self.btn_reset.resize(90, 25)
        self.btn_reset.clicked.connect(self.btn_reset_click)

        self.box_adresses = QCheckBox('Почт. индекс', self)
        self.box_adresses.move(10, 445)
        self.box_adresses.clicked.connect(self.postal_code)

        self.is_postal_code = False

        self.get_image(self.coords, self.scale)
        self.pixmap = QPixmap('map.png')
        self.image.setPixmap(self.pixmap)

    def postal_code(self):
        self.is_postal_code = self.box_adresses.isChecked()
        if self.is_postal_code and self.now_point[2]:
            self.text_to_adress.setText(f'{self.now_point[1]}, {self.now_point[2]}')
        else:
            self.text_to_adress.setText(f'{self.now_point[1]}')


    def btn_reset_click(self):
        self.now_point = ('', '', '')
        self.get_image(self.coords, self.scale)
        self.image.setPixmap(QPixmap(self.map_file))
        self.text_to_adress.setText(self.now_point[1])

    def btn_lineedit_click(self):
        if not self.lineedit.text():
            return

        search_params = {
            'geocode': self.lineedit.text(),
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'format': 'json'
        }
        link = 'https://geocode-maps.yandex.ru/1.x/'
        response = requests.get(link, search_params)

        data = response.json()
        postal_code = None
        try:
            coords = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
            adress = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                'GeocoderMetaData']['text']
            try:
                postal_code = \
                    data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                        'GeocoderMetaData']['Address']['postal_code']
            except Exception:
                pass
        except Exception:
            return
        coords = ','.join(coords)

        if self.scale < 8:
            self.scale = 8
        elif self.scale > 12:
            self.scale = 12
        if postal_code is None:
            self.now_point = (f'{coords},pm2lbm', adress, '')
        else:
            self.now_point = (f'{coords},pm2lbm', adress, postal_code)
        self.get_image(coords, self.scale)
        self.coords = coords
        self.image.setPixmap(QPixmap(self.map_file))
        if self.is_postal_code and self.now_point[2]:
            self.text_to_adress.setText(f'{self.now_point[1]}, {self.now_point[2]}')
        else:
            self.text_to_adress.setText(f'{self.now_point[1]}')

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.statusBar().clearMessage()
            x = event.pos().x()
            y = event.pos().y()
            if not (0 <= x <= self.image_x and 0 <= y <= self.image_y):
                return
            if self.scale < 8:
                self.statusBar().showMessage(
                    f'Использование меток при помощи мыши допустимо только при масштабе от 8, '
                    f'текущий масштаб: {self.scale}')
                return
            coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
            coords = self.coords.split(',')
            dy = self.image_y // 2 - y
            dx = x - self.image_x // 2

            lx = float(coords[0]) + dx * coord_to_geo_x * 2 ** (15 - self.scale)
            ly = float(coords[1]) + dy * coord_to_geo_y * math.cos(math.radians(float(coords[1]))) * 2 ** (
                    15 - self.scale)
            if lx > 180:
                lx -= 360
            elif lx < -180:
                lx += 360

            self.get_image(self.coords, self.scale)
            self.image.setPixmap(QPixmap(self.map_file))

            search_params = {
                'geocode': f'{lx},{ly}',
                'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                'format': 'json'
            }
            link = 'https://geocode-maps.yandex.ru/1.x/'
            response = requests.get(link, search_params)

            data = response.json()
            postal_code = None
            try:
                adress = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                    'GeocoderMetaData']['text']
                try:
                    postal_code = \
                        data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                            'GeocoderMetaData']['Address']['postal_code']
                except Exception:
                    pass
            except Exception:
                return
            if postal_code is None:
                self.now_point = (f'{lx},{ly},pm2lbm', adress, '')
            else:
                self.now_point = (f'{lx},{ly},pm2lbm', adress, postal_code)
            self.get_image(self.coords, self.scale)
            self.image.setPixmap(QPixmap(self.map_file))
            if self.is_postal_code and self.now_point[2]:
                self.text_to_adress.setText(f'{self.now_point[1]}, {self.now_point[2]}')
            else:
                self.text_to_adress.setText(f'{self.now_point[1]}')


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
