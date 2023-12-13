from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget,
                             QLineEdit, QPushButton, QInputDialog,
                             QTextEdit, QLabel, QGridLayout, QScrollArea, QGroupBox,
                             QVBoxLayout, QMessageBox, QComboBox, QFileDialog, QHBoxLayout)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from screeninfo import get_monitors
import sys
import sqlite3
from json import dumps, loads
from re import *


# Кликабельный лейбел
class Clicked_Label(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent, use_date):
        QLabel.__init__(self, parent)
        self.use_data = use_date

    def mousePressEvent(self, ev):
        self.clicked.emit()


# Кликабельный лейбел

class My_Push_Button(QPushButton):
    def __init__(self, parent, text, id_db,
                 number_row,
                 name):  # id заметки в базе данных, #number_row номер ряда в QGridLayout, name - название удаляемой заметки
        QPushButton.__init__(self, parent=parent, text=text)
        self.id_db = id_db
        self.number_row = number_row
        self.name = name


class Application(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.initUI()

    def initUI(self):

        ##Статус - бар
        self.statusbar = self.statusBar()
        self.count_word = QLabel(self, text='Слов: 0')
        self.count_letters = QLabel(self, text='Символом: 0')
        self.statusbar_category = QLabel(self, text='Текущая категория:...')
        self.statusbar.addPermanentWidget(self.count_word)
        self.statusbar.addPermanentWidget(self.count_letters)
        self.statusbar.addPermanentWidget(self.statusbar_category)
        ##Статус - бар

        ##База данных
        self.db = sqlite3.connect("project_sqlite.db")
        self.cursor = self.db.cursor()
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS Заметки(id INTEGER NOT NULL PRIMARY KEY, имя TEXT, содержание TEXT, id_категории INTEGER, фото TEXT)')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS Категории(id INTEGER NOT NULL PRIMARY KEY, имя TEXT)'
        )
        self.db.commit()
        ##База данных

        ##Контейнер-Виджет
        self.container = QWidget(self)
        self.container.setStyleSheet('background-color:#bbbbbb')
        monitor = get_monitors()[0]
        self.width = monitor.width
        self.height = monitor.height
        self.container.resize(int(0.25 * self.width), int(0.95 * self.height))
        ##Контейнер-Виджет

        ##Выберите категорию
        self.choice_category_label = QLabel(text='Выберите категорию:', parent=self.container)
        self.choice_category_label.move(int(0.2 ** 2 * self.width), int(0.05 * self.height))
        self.choice_category_label.resize(self.choice_category_label.sizeHint())
        ##Выберите категорию

        ##Кнопка добавить категорию
        self.add_category_bttn = QPushButton(self.container, text='Добавить категорию+')
        self.add_category_bttn.setStyleSheet('background-color:white')
        self.add_category_bttn.move(int(0.41 ** 2 * self.width), int(0.04 * self.height))
        self.add_category_bttn.resize(150, 35)
        self.add_category_bttn.clicked.connect(self.add_category)
        ##Кнопка добавить категорию
        self.del_category_bttn = QPushButton(self.container, text='Удалить категорию+')
        self.del_category_bttn.setStyleSheet('background-color:white')
        self.del_category_bttn.move(int(0.41 ** 2 * self.width), int(0.095 * self.height))
        self.del_category_bttn.resize(150, 35)
        self.del_category_bttn.clicked.connect(self.del_category)
        ##Кнопка удалить категорию
        ##

        ##LineEdit
        self.search = QLineEdit(self.container)
        self.search.setStyleSheet('background-color:white')
        self.search.move(int(0.1 ** 2 * self.width), int(0.15 * self.height))
        self.search.resize(260, 35)
        self.search.textChanged.connect(self.change_line_edit)
        ##LineEdit

        ##Добавить заметку
        self.add_button = QPushButton(self.container, text='Добавить заметку+')
        self.add_button.setStyleSheet('background-color:white')
        self.add_button.move(int(0.41 ** 2 * self.width), int(0.15 * self.height))
        self.add_button.resize(150, 35)
        self.add_button.clicked.connect(self.add_information)
        ##Добавить заметку

        ##Кнопка Выхода
        self.close_button = QPushButton(self, text='Закрыть ❌')
        self.close_button.setStyleSheet('background-color:white')
        self.close_button.clicked.connect(self.close_program)

        ##Кнопка Выхода

        ##важные флаги и констаты
        self.current = []  # текущая откртая ссесия
        self.was_saved = None  # True если файл из текущей ссесии был сохранен и его надо обновлять
        self.count = self.cursor.execute('select Count(*) from Заметки').fetchall()[0][0]
        self.id = self.count
        self.old = None  # если открыт старый файл
        self.skip = None
        self.maximum_layout = self.count
        ##важные флаги и констаты

        # self.make_scrollbar() здесь именно заметки текущей категории
        self.make_scrollbar()
        self.make_category_combo_box()

        self.make_mini_message()

    def keyPressEvent(self, event):
        if int(event.modifiers()) == Qt.CTRL and event.key() == Qt.Key_S:
            if self.current:  # проверяет, открыта ли какая то ссесия(заметка)
                self.save_file()

    def del_category(self):
        if self.BoxCategory.currentData() != '%':
            message_warning = QMessageBox(self)
            message_warning.setWindowTitle('Внимание')
            message_warning.setText('Действительно удалить текущую категорию?')
            message_warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_warning.setIcon(QMessageBox.Warning)
            message_warning.buttonClicked.connect(self.yes_delete_category)
            message_warning.show()
        else:
            message_warning = QMessageBox(self)
            message_warning.setWindowTitle('Внимание')
            message_warning.setText('Выберите Категорию')
            message_warning.setStandardButtons(QMessageBox.Ok)
            message_warning.setIcon(QMessageBox.Warning)
            message_warning.show()

    def yes_delete_category(self, btn):
        if btn.text()[1:] == 'Yes':
            self.cursor.execute(f'delete from Заметки where id_категории = ?', (self.BoxCategory.currentData(),))
            self.cursor.execute(f'delete from Категории where id = ?', (self.BoxCategory.currentData(),))
            self.BoxCategory.removeItem(self.BoxCategory.currentIndex())
            self.was_saved = None  # True если файл из текущей ссесии был сохранен и его надо обновлять
            self.count = self.cursor.execute('select Count(*) from Заметки').fetchall()[0][0]
            self.id = self.count
            self.old = None  # если открыт старый файл
            self.skip = None
            for i in self.current:
                i.deleteLater()
            self.current = []
            self.db.commit()

    def change_find_on_line(self):  # изменение строки поиска по заметке
        flag = 0
        patter = self.find_on_line.text()  # результат ввода в поисковую строку
        text = self.text_edit.toPlainText()
        if patter:
            text = text.replace(patter, f'<font color="red" size=4>{patter}</font>')
        if self.was_saved:
            flag = 1
        self.text_edit.setText(text)
        if flag == 0:
            self.was_saved = False
        else:
            self.was_saved = True
            self.statusbar.showMessage(self.hendler.text())

    def add_category(self):
        if self.was_saved or (self.was_saved is None and self.old is None) or self.skip:
            dialog = QInputDialog()
            name, ok_pressed = dialog.getText(self, 'Новая категория', 'Введите название')
            if ok_pressed:
                if name == '':
                    name = 'Новая категория'
                new_id = self.cursor.execute('select max(id) from Категории').fetchall()[0][0]
                new_id = 1 if new_id is None else int(new_id) + 1
                self.BoxCategory.addItem(name, userData=new_id)
                self.BoxCategory.setCurrentText(name)
                contain = dumps([])
                self.cursor.execute('insert into Категории values(?, ?)', (new_id, name))
                self.db.commit()
        else:
            self.make_answer_saved(self.save_changes_question)

    def make_category_combo_box(self):
        query = self.cursor.execute('select id, имя from Категории').fetchall()
        self.BoxCategory = QComboBox(self.container)
        self.BoxCategory.addItem('*', userData='%')
        for i in query:
            id_, name = i
            self.BoxCategory.addItem(name, userData=id_)
        self.BoxCategory.move(int(0.2 ** 2 * self.width), int(0.07 * self.height))
        self.BoxCategory.resize(150, 35)
        self.BoxCategory.setStyleSheet('background-color:white')
        self.BoxCategory.currentTextChanged.connect(self.change_category)
        self.change_category()

    def change_category(self):
        self.groupBox.setTitle(self.BoxCategory.currentText())
        self.delete_scrollbar()
        self.statusbar_category.setText(f'Текущая категория:{self.BoxCategory.currentText()}')
        if self.BoxCategory.currentText() == "*":
            query = self.cursor.execute('select id, имя from Заметки').fetchall()
        else:
            query = self.cursor.execute(
                f'select id, имя from Заметки where id_категории = {self.BoxCategory.currentData()}').fetchall()
        for i in range(len(query)):
            id_, name = query[i]  # id в базе данных
            self.add_scrollbar(name, id_db=id_, row=i)

    def add_scrollbar(self, text, id_db, row):
        bttn = My_Push_Button(parent=self.container, text=text, id_db=id_db, number_row=row, name=text, )
        bttn.clicked.connect(self.open_file)
        bttn.setStyleSheet('background-color:white;')
        self.layout.addWidget(bttn, row, 0)
        self.layout.setColumnStretch(0, 4)
        del_bttn = My_Push_Button(parent=self.container, text='Удалить', id_db=id_db, number_row=row, name=text)
        del_bttn.setStyleSheet('background-color:white;')
        del_bttn.clicked.connect(self.delete_information)
        self.layout.addWidget(del_bttn, row, 1)
        self.groupBox.setLayout(self.layout)
        self.maximum_layout += 1

    def delete_information(self):
        question = QMessageBox(self)
        sender = self.sender()
        question.setText(f'Действительно удалить заметку "{sender.name}"?')
        question.setWindowTitle('Удаление заметки')
        question.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        question.setDefaultButton(QMessageBox.Ok)
        question.buttonClicked.connect(lambda btn: self.yes_delete(btn=btn, sender=sender))
        question.show()

    def yes_delete(self, btn, sender):
        if btn.text() == 'OK':
            row = sender.number_row
            id_db = sender.id_db
            note = self.layout.itemAtPosition(row, 0)
            self.layout.removeWidget(note.widget())
            self.layout.removeWidget(sender)
            sender.deleteLater()
            self.cursor.execute(f'delete from Заметки where id = "{id_db}"')
            self.db.commit()
            self.count -= 1
            self.groupBox.setLayout(self.layout)
            if self.id == id_db:
                for i in self.current:
                    i.deleteLater()
                self.current = []
                self.old = None
                self.skip = False
                self.was_saved = None

    def make_mini_message(self):
        label = QLabel(self, text='Выберите заметку\nИли создайте новую')
        label.move(int(self.width * 0.6), int(self.height * 0.45))
        font = label.font()
        font.setPixelSize(16)
        font.bold()
        label.setFont(font)
        label.resize(label.sizeHint())

    def make_scrollbar(self):
        self.groupBox = QGroupBox(self.container)
        self.layout = QGridLayout()
        scroll = QScrollArea()
        scroll.setWidget(self.groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(int(self.height * 0.75))
        Vlayout = QVBoxLayout(self.container)
        Vlayout.addStretch()
        Vlayout.addWidget(scroll)

    ###############################################
    def change_line_edit(self):  ## поиск заметки
        text = self.search.text()
        self.delete_scrollbar()
        query = self.cursor.execute(
            f'select id, имя from Заметки where имя like "%{text}%" and id_категории = "{self.BoxCategory.currentData()}"').fetchall()
        if self.BoxCategory.currentData() == '%':
            query = self.cursor.execute(f'select id, имя from Заметки where имя like "%{text}%"').fetchall()
        for i in range(len(query)):
            id_, name = query[i]  # id в базе данных
            self.add_scrollbar(name, id_db=id_, row=i)
            self.maximum_layout += 1

    def delete_scrollbar(self):
        for i in range(self.maximum_layout):
            for j in range(2):
                item = self.layout.itemAtPosition(i, j)
                if item is not None: self.layout.removeWidget(item.widget())
        self.count = 0
        self.maximum_layout = 0

    ###############################################
    def add_information(self):
        if self.BoxCategory.currentData() != '%':
            if self.was_saved or (self.was_saved is None and self.old is None) or self.skip:
                dialog = QInputDialog()
                name, ok_pressed = dialog.getText(self, 'Новая заметка', 'Введите название')
                if ok_pressed:
                    if self.current:
                        for i in self.current:
                            i.deleteLater()
                        self.current = []  # удаление элементов текущей ссесии
                    if name == '':
                        name = 'Новая заметка'
                    self.old = False
                    self.was_saved = False
                    self.skip = False
                    self.make_session(name, [])
            else:
                self.make_answer_saved(self.save_changes_question)
        else:
            message_warning = QMessageBox(self)
            message_warning.setWindowTitle('Внимание')
            message_warning.setText('Сначала выберите категорию или создайте новую')
            message_warning.setStandardButtons(QMessageBox.Ok)
            message_warning.setIcon(QMessageBox.Warning)
            message_warning.show()

    def make_session(self, name, photos):
        self.hendler = QLabel(self, text=name)
        self.hendler.move(int(0.3 * self.width), int(self.width * 0.02))
        font = self.hendler.font()
        font.setPixelSize(32)
        self.hendler.setFont(font)
        self.hendler.resize(self.hendler.sizeHint())
        self.hendler.show()
        # поиск по заметке
        self.find_on_line = QLineEdit(self)
        self.find_on_line.resize(220, 35)
        self.find_on_line.move(int(0.55 * self.width), int(self.width * 0.07))
        self.find_on_line.show()
        self.find_on_line.setPlaceholderText('Поиск по заметке')
        self.find_on_line.textChanged.connect(self.change_find_on_line)
        # поиск по заметке

        ##Поле для ввода
        self.text_edit = QTextEdit(self)
        self.text_edit.resize(int(self.width * 0.65), int(self.height * 0.55))
        self.text_edit.move(int(0.3 * self.width), int(self.width * 0.1))
        self.text_edit.textChanged.connect(self.change_text_edit)
        font = self.text_edit.font()
        font.setPixelSize(18)
        self.text_edit.setFont(font)
        self.text_edit.show()
        ##Поле для ввода
        ## Кнопка для сохранения
        save_button = QPushButton('💾', self)
        save_button.resize(40, 40)
        save_button.move(int(self.width * 0.93), int(self.height * 0.75))
        save_button.clicked.connect(self.save_file)
        save_button.show()
        ## Кнопка для сохранения

        ##Прикрепить фото
        add_file = QPushButton('Прикрепить фото+', self)
        add_file.resize(150, 40)
        add_file.move(int(self.width * 0.85), int(self.height * 0.75))
        add_file.clicked.connect(self.add_photo)
        add_file.show()
        ##Прикрепить фото

        ##контейнер для фото
        self.photo_contaiter = QWidget(self)
        self.photo_contaiter.setStyleSheet('background-color:#bbbbbb;')
        self.photo_contaiter.resize(int(self.width * 0.53), int(self.height * 0.2))
        self.photo_contaiter.move(int(0.3 * self.width), int(self.height * 0.75))

        self.groupBox_photo = QGroupBox(self.photo_contaiter)
        self.groupBox_photo.setTitle('Прикрепленные фото')
        self.layout_photo = QHBoxLayout()
        scroll = QScrollArea()
        scroll.setWidget(self.groupBox_photo)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)
        Vlayout = QVBoxLayout(self.photo_contaiter)
        Vlayout.addStretch()
        Vlayout.addWidget(scroll)
        for i in range(len(photos)):
            self.add_photo_in_QHLayout(photos[i])
        self.photo_contaiter.show()
        ##контейнер для фото

        self.current.append(self.hendler)
        self.current.append(self.text_edit)
        self.current.append(save_button)
        self.current.append(self.find_on_line)
        self.current.append(add_file)
        self.current.append(self.photo_contaiter)

    ##открыть фото
    def open_photo_on_full_screen(self):
        userdata = self.sender().use_data
        new_container = ChildrenWindow(self, w=self.width, h=self.height, load=userdata)
        new_container.showFullScreen()

    ##открыть фото

    ##Добавить фото именно в базу данных(тут же будем вызывать метод отображения add_photo_in_QHLayout)
    def add_photo(self):
        if self.old:
            file = \
                QFileDialog.getOpenFileName(self, 'Выберите фото', '',
                                            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[
                    0]
            if file:
                old_list = loads(self.cursor.execute(f'select фото from Заметки where id = {self.id}').fetchall()[0][0])
                old_list.append(file)
                new_list = dumps(old_list)
                self.cursor.execute(f'update Заметки set фото = ? where id = ?', (new_list, self.id))
                self.db.commit()
                self.add_photo_in_QHLayout(file)
        else:
            message_box = QMessageBox(self)
            message_box.setWindowTitle('Внимание')
            message_box.setIcon(QMessageBox.Warning)
            message_box.setText(
                'Для работы с фото заметка будет сохранена со всеми текущими изменениями (В дальнейшем это не потребуется)')
            message_box.buttonClicked.connect(self.save_file)
            message_box.show()

    def add_photo_in_QHLayout(self, photo):
        label = Clicked_Label(self.photo_contaiter, use_date=photo)
        self.layout_photo.addWidget(label)
        label.clicked.connect(self.open_photo_on_full_screen)
        pixmap = QPixmap(photo)
        label.setPixmap(pixmap.scaledToHeight(120))
        self.groupBox_photo.setLayout(self.layout_photo)

    ##Добавить фото

    def change_text_edit(self):
        text = self.text_edit.toPlainText()
        self.statusbar.showMessage('Изменён')
        self.count_letters.setText(f'Символов: {len(text)}')
        self.count_word.setText(f'Слов: {len(text.split())}')
        self.was_saved = False

    def save_file(self):
        self.statusbar.showMessage('Сохранён')
        if not self.was_saved and not self.old:
            name = str(self.hendler.text())
            text = str(self.text_edit.toPlainText())
            new_id = self.cursor.execute('select max(id) from Заметки').fetchall()[0][0]
            new_id = 1 if new_id is None else int(new_id) + 1
            photos = dumps([])
            self.cursor.execute('insert into Заметки values (?, ?, ?, ?, ?)',
                                (new_id, name, text, self.BoxCategory.currentData(), photos))
            self.db.commit()
            self.id = new_id
            self.maximum_layout = new_id
            self.add_scrollbar(self.hendler.text(), id_db=self.id, row=self.maximum_layout)
        else:
            text = self.text_edit.toPlainText()
            self.cursor.execute(f'update Заметки set содержание = ? where id = {self.id}', (str(text),))
            self.db.commit()
        self.was_saved = True
        self.old = True

    def open_file(self):
        if self.was_saved or (self.old is None and self.was_saved is None) or self.skip:
            id_ = self.sender().id_db
            self.id = id_
            text, name = self.cursor.execute(f'select содержание, имя from Заметки where id = {id_}').fetchall()[0]
            all_photos = loads(self.cursor.execute(f'select фото from Заметки where id = {self.id}').fetchall()[0][0])
            for i in self.current:
                i.deleteLater()
            self.current = []
            self.make_session(name, all_photos)
            self.text_edit.setText(text)
            self.statusbar.showMessage(name)
            self.old = True
            self.was_saved = True
            self.skip = False
        else:
            self.make_answer_saved(self.save_changes_question)

    def make_answer_saved(self, func):
        object = QMessageBox(self)
        object.setText('Сохранить данную заметку?')
        object.setWindowTitle('Сохранение')
        object.setIcon(QMessageBox.Warning)
        object.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        object.setDefaultButton(QMessageBox.Ok)
        object.buttonClicked.connect(func)
        object.show()

    def save_changes_question(self, btn):
        if btn.text() == 'OK':
            self.save_file()
        else:
            self.skip = True
        for i in self.current:
            i.deleteLater()
        self.current = []

    def exit_changes_question(self, btn):
        if btn.text() == 'OK':
            self.save_file()
        sys.exit()

    def close_program(self):
        if self.was_saved or (self.was_saved is None and self.old is None) or self.skip:
            sys.exit()
        else:
            self.make_answer_saved(self.exit_changes_question)


class ChildrenWindow(QMainWindow):
    def __init__(self, parent, load, w, h):
        super().__init__(parent)
        self.load = load
        self.w = w
        self.h = h
        self.initUI()

    def initUI(self):
        label = QLabel(self)
        label.resize(450, 450)

        pixmap = QPixmap(self.load)
        if pixmap.height() >= int(self.h * 0.8):
            pixmap = pixmap.scaledToHeight(int(self.h * 0.8))
        label.resize(pixmap.width(), pixmap.height())
        label.setPixmap(pixmap)
        rect = label.frameGeometry()
        center = app.desktop().availableGeometry().center()
        rect.moveCenter(center)
        label.move(rect.topLeft())
        self.close_button = QPushButton(self, text='Закрыть ❌')
        self.close_button.setStyleSheet('background-color:white')
        self.close_button.clicked.connect(self.close_program)

    def close_program(self):
        self.deleteLater()


def hook(): pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    res = Application()
    sys.excepthook = hook
    res.showFullScreen()
    sys.exit(app.exec())
