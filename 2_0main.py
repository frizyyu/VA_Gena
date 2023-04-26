import asyncio
import ctypes
import ctypes
import ctypes.wintypes
import datetime
import getpass
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
import tkinter.filedialog
import wave
import webbrowser
from ctypes import *
from ctypes import c_int
from ctypes.wintypes import HWND, DWORD
from datetime import datetime
from tkinter import filedialog
from tkinter import filedialog
# import tts
import player_tracks
import pyaudio
import pyautogui
import pygame
import pymorphy2
import pyttsx3
# import sett
import speech_recognition
import speech_recognition as sr
import win32com.client
import win32con
import win32gui
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

'''from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QSystemTrayIcon, QMenu, QMessageBox, \
    QPushButton, \
    QStyle, QWidget, QAction'''
# from voice_assistand_gena.dist import daily_planner
from ai_gpt import quest_or_task, check_token

pygame.init()

hwnd = 0
waiting = False
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
with open("config.json", encoding="UTF8") as myfile:
    d = json.load(myfile)
# подключить чат гпт, улучшить работу команд с 68 строки
opts = {
    "alias": ('гена', 'геннадий', 'ген'),
    "cmds": {
        "ctime": ('время', 'час', 'времени'),  # +
        "YT": ('youtube', 'ютуб'),  # +
        # "find": ('такое', 'такая', 'такой', 'такое'),  # +
        "schedule": ('расписание', 'расписания', 'расписании', 'расписанию'),  # + убрал
        "daily_planner": ('ежедневник', 'ежедневника', 'ежедневнику', "ежедневнике", "ежедневники"),  # + вылет + убрал
        "google": ('браузер', 'гугл', 'google'),  # +
        "timer": ('поставь', 'заведи', 'установи', "таймер"),  # +
        "stopwatch_start": ('запусти', 'секундомер'),  # +
        "stopwatch_stop": ('останови', 'None'),  # +
        "VK": ('вк', 'vk', 'вконтакте'),  # +
        "change_name": ("смени", "имя", "имени"),  # +
        "notes": ("заметки", "заметку", "заметках"),  # +
        "turn_off": ("пока", "выключись", "связи", "свидания", "прощай", "выключайся"),  # +
        "settings": {"настройки", "настрой", "настройка"},  # убрал
        "waiting_mode": {"ожидания", "ожидание", "спи", "спать", "беспокоить"},
        "hide_window": {"сверни", "свернуть", "сворачивай", "сворачивайся"},
        "show_window": {"разверни", "открой", "открывай", "откройте"},  # этого нет просто
        "hide_this_window": {"сверни", "свернуть", "сворачивай", "сворачивайся"},
        "next_window": {"следующее", "дальше", "вперёд", "следующая", "следующие"},  # мб lat_window, но не обязательно
        "open_window": {"разверни", "верни"},
        "screenshot": {"скрин", "скриншот", "фото", "снимок"},
        "programms": {"открой", "открыть", "открывай"},
        "tracks": {"from_pl": ("плейлист"),
                   "play": ("трек", "включи", "песня", "песни", "треки", "подкаст", "подкасты"),
                   "stop": ("стоп", "стой"), "volume": ("громкость", "звук"), "resume": ("продолжай", "играй"),
                   "pause": ("пауза", "паузу"), "playlist_add": ("плейлист", "playlist"), "playlist_del": "плейлиста",
                   "tracks": ("поток", "волна"),
                   "next": ("дальше", "следующий"), "last": ("предыдущий", "назад"), "favor": (
                "любимый", "любимого", "любимую", "жанр", "исполнителя", "исполнитель", "любимых", "любимые",
                "исполнителей"),
                   "favor_name": ("предпочтений", "предпочтения", "предпочтение"),
                   "playlists_name": ("плейлисты", "плейлистов")},
        "ai_gpt": {"question": ("вопрос", "вопросик"),
                   "school_task": ("задание", "задача", "задачу", "задания", "задачи", "сочинение", "напиши", "опиши")}
        # проверка на останови, но не должно быть слова секундомер
    }
}
can_open_progs = ["калькулятор", "dota", "cs", "honor", "проводник"]


def can_open(all_text):
    for i in all_text:
        if i in can_open_progs:
            return True
    return False


engine = pyttsx3.init()
device_d = {}
last_for_bot = False

USER_NAME = getpass.getuser()
drives = []
bitmask = ctypes.windll.kernel32.GetLogicalDrives()
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    if bitmask & 1:
        drives.append(letter)
    bitmask >>= 1

dwmapi = ctypes.WinDLL("dwmapi")
DWMWA_CLOAKED = 14
isCloacked = c_int(0)


def get_app_list():
    app_list = []

    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            dwmapi.DwmGetWindowAttribute(HWND(hwnd), DWORD(DWMWA_CLOAKED), ctypes.byref(isCloacked),
                                         ctypes.sizeof(isCloacked))
            if (isCloacked.value == 0):
                app_list.append((hwnd, win32gui.GetWindowText(hwnd)))
        return True

    win32gui.EnumWindows(callback, [])
    # print(*app_list, sep="\n")
    return app_list


def settext(text, col_num, shed=False):
    if text != "Вывел ваши предпочтения в диалог" and text != "Вывел ваши плейлисты в диалог":
        if (not ex.wt and col_num != 0) or col_num == 0:
            if not shed:
                text = text + "\n"
            if text == f"{d['bot_name']}: Говорите\n" and col_num == 0:
                say("Говорите")
            # print(text)
            row_c = ex.chat_table.rowCount()
            ex.chat_table.insertRow(row_c)
            # print(row_c)
            # ex.chat_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
            ex.chat_table.setItem(row_c, col_num, QTableWidgetItem(text))
            ex.chat_table.setVerticalHeaderItem(row_c, QTableWidgetItem(""))
            '''if "Ваши предпочтения:\n" in text or "Ваши плейлисты:\n" in text:
                #print("QWEQWE")
                ex.chat_table.setRowHeight(row_c + 1, 500)
            else:
                ex.chat_table.setRowHeight(row_c + 1, 75)'''
            ex.chat_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            ex.chat_table.scrollToBottom()
            # print(text)


# {'Discord.exe': '/Users\\Артём\\AppData\\Local\\Discord\\app-1.0.9010\\Discord.exe', 'steam.exe': '/Program Files (x86)\\Steam\\steam.exe'}
def find_file(file_name, path, disc):
    with open("programs.json", encoding="UTF8") as myfile:
        r = json.load(myfile)
    try:
        # print("ASDASDASD", r[file_name])
        subprocess.Popen(r[file_name])
        return "already_open"
    except Exception as e:
        # print(e)
        for d in drives[::-1]:
            os.chdir(d + ":")
            for root, dirs, files in os.walk(path):
                if file_name in files:
                    r[file_name] = f"{d}:{os.path.join(root, file_name)}".replace("/", r"\\")
                    return os.path.join(root, file_name), r


def add_to_startup(file_path=""):
    if file_path == "":
        # file_path = os.path.dirname(os.path.realpath(__file__))
        pass
        # C:\Users\Artem\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    # bat_path = r"C:\Users\Artem\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    with open(bat_path + '\\' + "GENA.bat", "w+") as bat_file:
        bat_file.write(r'start "" %s' % file_path)


class main20(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main20.ui', self)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.setFixedSize(self.size())
        self.setWindowTitle('Гена')
        self.hide_btn.clicked.connect(self.hide_it)
        # sleep = threading.Timer(1, sleep_before_start)
        # sleep.start()
        self.main_chat.clicked.connect(self.m_wind)
        self.sett_btn.clicked.connect(self.settings)
        self.exit_btn.clicked.connect(self.close_all)
        self.wait_box.stateChanged.connect(self.waiting)
        self.download_btn.clicked.connect(self.ai)
        self.check_token.clicked.connect(self.checktoken)
        self.rep_bug.clicked.connect(self.report_bug)
        # self.chat_table.setShowGrid(False)
        self.wt = False
        self.what_window = "main"
        ###for settings
        self.on_off_set(False)
        self.on_off_ai_wind(False)
        self.root = "|||"
        '''p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if i > 0:
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    self.change_mic_box.addItem(p.get_device_info_by_host_api_device_index(0, i).get('name'))
                    device_d[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i
        #print(device_d, "ASDFDGRGTSHGRSRGHTSSRGB")'''
        self.wait_slider.setValue(d["slider_value"])
        self.wait_number.display(d["slider_value"])
        # self.close_button.clicked.connect(self.clse)
        self.wait_slider.setMinimum(5)
        self.wait_slider.setMaximum(60)
        self.wait_slider.valueChanged.connect(self.valuechange)

        # self.close_button.clicked.connect(self.clse)
        self.sensitivity_slider.setMinimum(100)
        self.sensitivity_slider.setMaximum(1000)
        if d["sens_value"] <= 0:
            x = abs(d["sens_value"])
            self.sensitivity_slider.setValue(100)
            self.sensitivity_number.display(0)
            self.auto_noise.setChecked(True)
            d["sens_value"] = -1 * x
        else:
            self.auto_noise.setChecked(False)
            self.sensitivity_slider.setValue(d["sens_value"])
            self.sensitivity_number.display(d["sens_value"] / 100)
        self.sensitivity_slider.valueChanged.connect(self.senschange)

        self.refresh_ai.clicked.connect(self.refresh_ai_table)
        self.quest_token.clicked.connect(self.token_quest)
        self.aitoken.textChanged.connect(self.changestsh)
        self.ai_table.setColumnWidth(0, 130)
        self.ai_table.setColumnWidth(1, 42)
        self.ai_table.setColumnWidth(2, 42)
        self.cmd_list.clicked.connect(self.show_cmds)
        self.cmds_w.setColumnWidth(0, 50)
        self.cmds_w.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.cmds_w.header().setStretchLastSection(False)
        self.cmds_w.setWordWrap(True)
        self.auto_noise.stateChanged.connect(self.auto_noise_check)
        ###

    def changestsh(self):
        self.aitoken.setStyleSheet('''QLineEdit {
                    color: rgb(230, 230, 230);
                    background-color: rgba(0, 255, 0, 0);
                    border: 1px solid white;
                        border-radius: 7px;
                    }''')

    def token_quest(self):
        webbrowser.open("https://platform.openai.com/account/api-keys")

    def report_bug(self):
        webbrowser.open("https://taplink.cc/gena_support")

    def auto_noise_check(self):
        if self.auto_noise.isChecked():
            x = self.sensitivity_slider.value()
            self.sensitivity_slider.setValue(100)
            self.sensitivity_number.display(0)
            self.auto_noise.setChecked(True)
            d["sens_value"] = -1 * x
            # запись в словарь чего-то конкретного
        else:
            self.sensitivity_slider.setValue(abs(d["sens_value"]))
            d["sens_value"] = self.sensitivity_slider.value()
            # запись в словарь значение с слайдера
        json_write(d)

    def show_cmds(self):
        if self.what_window == "main":
            self.on_off_main(False)
        elif self.what_window == "ai_wind":
            self.on_off_ai_wind(False)
        elif self.what_window == "settings":
            self.on_off_set(False)
        self.cmds_w.setVisible(True)
        self.lab_cmds.setVisible(True)

    def checktoken(self):
        if check_token(self.aitoken.text()) == "valid":
            self.aitoken.setStyleSheet('''QLineEdit {
            color: rgb(230, 230, 230);
            background-color: rgba(0, 255, 0, 128);
            border: 1px solid white;
                border-radius: 7px;
            }''')
            d["gpt_token"] = self.aitoken.text()
            json_write(d)
        else:
            try:
                self.aitoken.setStyleSheet('''QLineEdit {
                            color: rgb(230, 230, 230);
                            background-color: rgba(255, 0, 0, 128);
                            border: 1px solid white;
                                border-radius: 7px;
                            }''')
                d["gpt_token"] = "invalid"
                json_write(d)
            except Exception as e:
                pass
                # print(e)

    def on_off_set(self, flag):
        self.lab_set.setVisible(flag)
        self.sensitivity.setVisible(flag)
        self.sensitivity_slider.setVisible(flag)
        self.sensitivity_number.setVisible(flag)
        self.change_micro.setVisible(flag)
        self.change_mic_box.setVisible(flag)
        self.lab_wait.setVisible(flag)
        self.wait_slider.setVisible(flag)
        self.wait_number.setVisible(flag)
        self.aitoken.setVisible(flag)
        self.check_token.setVisible(flag)
        self.ai_token_text.setVisible(flag)
        self.quest_token.setVisible(flag)
        self.cmds_w.setVisible(False)
        self.lab_cmds.setVisible(False)
        self.auto_noise.setVisible(flag)
        # self.quest_token.setToolTip(u'Тест-проверка')
        self.aitoken.setStyleSheet('''QLineEdit {
                    color: rgb(230, 230, 230);
                    background-color: rgba(0, 255, 0, 0);
                    border: 1px solid white;
                        border-radius: 7px;
                    }''')
        if d["gpt_token"] == "invalid":
            self.aitoken.setText("")
        else:
            self.aitoken.setText(d["gpt_token"])
        # self.save_set.setVisible(flag)

    def on_off_main(self, flag):
        self.wait_box.setVisible(flag)
        self.chat_table.setVisible(flag)
        self.verticalFrame.setVisible(flag)
        self.cmds_w.setVisible(False)
        self.lab_cmds.setVisible(False)

    def on_off_ai_wind(self, flag):
        self.verticalFrame_2.setVisible(flag)
        self.ai_table.setVisible(flag)
        self.refresh_ai.setVisible(flag)
        self.cmds_w.setVisible(False)
        self.lab_cmds.setVisible(False)

    '''def elem_to_ai_table(self):
        downloadButton = QPushButton('Скачать')
        self.ai_table.setCellWidget(0, 1, downloadButton)'''

    def set_to_ai_table(self, key, ai_d):
        self.ai_table.insertRow(0)
        self.ai_table.setItem(0, 0, QTableWidgetItem(key))
        # print(self.ai_table.rowCount())
        if ai_d[key] != "generating!@#":
            downloadButton = QPushButton('')
            downloadButton.setStyleSheet("background-color: transparent;")
            icon = QIcon()
            icon.addPixmap(QPixmap("images\eye_icon.png"))
            downloadButton.setIcon(icon)
            downloadButton.setIconSize(icon.actualSize(QSize(40, 40)))
            self.ai_table.setCellWidget(0, 1, downloadButton)
            downloadButton.clicked.connect(lambda: self.downloadFile(key, ai_d[key]))
        else:
            downloadButton = QPushButton('')
            downloadButton.setStyleSheet("background-color: transparent;")
            icon = QIcon()
            icon.addPixmap(QPixmap("images\wait_icon.png"))
            downloadButton.setIcon(icon)
            downloadButton.setIconSize(icon.actualSize(QSize(40, 40)))
            self.ai_table.setCellWidget(0, 1, downloadButton)
            # downloadButton.clicked.connect(lambda: self.downloadFile(key, ai_d[key]))
        delButton = QPushButton('')
        delButton.setStyleSheet("background-color: transparent;")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(r"images\trash_icon.png"))
        delButton.setIcon(icon1)
        delButton.setIconSize(icon1.actualSize(QSize(40, 40)))
        self.ai_table.setCellWidget(0, 2, delButton)
        delButton.clicked.connect(lambda: self.delFile(key, ai_d))
        self.ai_table.setVerticalHeaderItem(0, QTableWidgetItem(""))
        self.ai_table.resizeRowsToContents()

    def delFile(self, filename, ai_d):  # протестить
        try:
            items = self.ai_table.findItems(filename, QtCore.Qt.MatchExactly)
            if items:
                ai_d.pop(filename)
                with open("ai_tasks.json", "w", encoding="UTF8") as f:
                    json.dump(ai_d, f)
                    item = items[0]
                row_number = item.row()
                self.ai_table.removeRow(row_number)
                os.remove(f"{filename}.txt")
        except Exception as e:
            pass
            # print(e)

    def refresh_ai_table(self):
        try:
            with open("ai_tasks.json", encoding="UTF8") as myf:
                ai_d = json.load(myf)
            self.ai_table.setRowCount(0)
            self.ai_table.clear()
            self.ai_table.setHorizontalHeaderLabels(['', '', ''])
            # print(ai_d)
            for key in ai_d.keys():
                self.set_to_ai_table(key, ai_d)
        except Exception as e:
            pass
            # print(e)

        '''data = {}  # Инициализируем пустой словарь
        # Проходимся по каждой строке таблицы
        for row in range(self.ai_table.rowCount()):
            row_data = {}
            for col in range(self.ai_table.columnCount()):
                # Получаем данные из ячейки и добавляем их в словарь
                item = self.ai_table.item(row, col)
                if item is not None:
                    row_data[self.ai_table.horizontalHeaderItem(col).text()] = item.text()
                else:
                    row_data[self.ai_table.horizontalHeaderItem(col).text()] = ''
            data[row] = row_data
        #print(data)
        if ai_d != data:
            for key in data.keys():
                if data[key] not in ai_d:
                    pass
                else:
                    pass'''
        # берём данные из таблицы и сравниваем с тем, что уже есть, недоставляющее добавляем

    def downloadFile(self, filename, f_content):
        with open(f"{filename}.txt", "w+") as f:
            # print(filename, f_content)
            f.write(f_content)
        thr = threading.Thread(target=subprocess.run,
                               args=[['npad/notepad.exe', f"{filename}.txt"]])
        thr.start()
        # print('Скачивание файла:', filename)

    def ai(self):
        if self.what_window == "main":
            self.on_off_main(False)
        elif self.what_window == "settings":
            self.on_off_set(False)
        self.on_off_ai_wind(True)
        self.refresh_ai_table()
        self.what_window = "ai_wind"

    def settings(self):
        if self.what_window == "main":
            self.on_off_main(False)
        elif self.what_window == "ai_wind":
            self.on_off_ai_wind(False)
        self.on_off_set(True)
        self.what_window = "settings"
        '''sett = settings_()
        sett.setWindowFlag(Qt.WindowStaysOnTopHint)
        sett.setWindowModality(Qt.ApplicationModal)
        sett.exec_()'''

    def replace_device(self):
        try:
            # print("CHANGED MCRO")
            # print("CHANGED MCRO")
            if self.change_mic_box.currentText() != "":
                d["device"] = self.change_mic_box.currentText()
                # print("MICRO LOGS", "||", device_d, "||", d["device"])
                d["device_index"] = device_d[self.change_mic_box.currentText()]
                json_write(d)
        except Exception as e:
            pass
            #print(e, "WWWWWEERROR")

    def senschange(self):
        self.sensitivity_number.display(self.sensitivity_slider.value() / 100)
        d["sens_value"] = self.sensitivity_slider.value()
        self.auto_noise.setChecked(False)
        json_write(d)

    def valuechange(self):
        self.wait_number.display(self.wait_slider.value())
        d["slider_value"] = self.wait_slider.value()
        json_write(d)

    def m_wind(self):
        if self.what_window == "settings":
            self.on_off_set(False)
        elif self.what_window == "ai_wind":
            self.on_off_ai_wind(False)
        self.on_off_main(True)
        self.what_window = "main"

    def close_all(self):
        eexit = want_exit()
        eexit.setWindowFlag(Qt.WindowStaysOnTopHint)
        eexit.setWindowModality(Qt.ApplicationModal)
        eexit.exec_()

    def waiting(self):
        if self.wait_box.isChecked():
            self.wt = True
            self.wait_box.setIcon(QIcon("images/micro_off_icon.png"))
            # return True
        else:
            global last_for_bot, hear_C
            self.wt = False
            last_for_bot = True
            hear_C = 0
            self.wait_box.setIcon(QIcon("images/micro_on_icon.png"))
            # sleep_before_start()
            # sleep_before_start()

    def hide_it(self):
        self.setVisible(False)
        # if not self.wt:
        # sleep_before_start()


class want_exit(QDialog):
    def __init__(self):
        super(want_exit, self).__init__()
        # self.setupUi(self)
        uic.loadUi('want_to_exit.ui', self)
        self.setWindowTitle('Выход')
        self.yesButton.clicked.connect(self.wantext)
        self.noButton.clicked.connect(self.want_continue)

    def wantext(self):
        self.close()
        ex.close()
        ctypes.windll.user32.DestroyWindow(ctypes.windll.kernel32.GetConsoleWindow())
        exit()

    def want_continue(self):
        self.close()


class shedu(QDialog):
    def __init__(self):
        super().__init__()
        # self.setupUi(self)
        uic.loadUi('schedul.ui', self)
        self.setWindowTitle('Расписание')
        self.pushButton.clicked.connect(self.clse)

    def clse(self):
        self.close()


'''class settings_(sett.Ui_Form, QDialog):
    try:
        def __init__(self):
            super().__init__()
            # self.setupUi(self)
            uic.loadUi('settings.ui', self)
            self.setWindowTitle('Настройки')
            self.root = "|||"
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            device_d = {}
            for i in range(0, numdevices):
                if i > 0:
                    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                        self.comboBox.addItem(p.get_device_info_by_host_api_device_index(0, i).get('name'))
                        device_d[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i
            self.horizontalSlider.setValue(d["slider_value"])
            self.lcdNumber.display(d["slider_value"])
            index = self.comboBox.findText(d["device"], Qt.MatchFixedString)
            self.comboBox.setCurrentIndex(index)
            self.comboBox.currentTextChanged.connect(self.replace_device)
            self.close_button.clicked.connect(self.clse)
            self.horizontalSlider.setMinimum(5)
            self.horizontalSlider.setMaximum(60)
            self.horizontalSlider.valueChanged.connect(self.valuechange)

        def replace_device(self):
            d["device"] = self.comboBox.currentText()
            d["device_index"] = device_d[self.comboBox.currentText()]

        def valuechange(self):
            self.lcdNumber.display(self.horizontalSlider.value())
            d["slider_value"] = self.horizontalSlider.value()

        def clse(self):
            if self.root != "|||":
                self.root.destroy()
            json_write(d)
            self.close()
    except Exception as e:
        #print(e)'''

'''class dailyplanner(daily_planner.Ui_Dialog, QDialog):  # ежедневник
    def __init__(self):
        super(dailyplanner, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Ежедневник')
        self.con = sqlite3.connect("week.db")
        self.cur = self.con.cursor()
        self.res = self.cur.execute("""SELECT * FROM daily_planner""").fetchall()
        self.date = self.calendarWidget.selectedDate().toString("dd-MM-yyyy")
        self.closebutton.clicked.connect(self.close_it)
        self.calendar_show()
        if self.textBrowser.toPlainText() != "Задач нет.":
            say(f"Сегодня вам нужно: {self.textBrowser.toPlainText()}")
            # ex.settext(f"{d['bot_name']}: Сегодня вам нужно:\n{self.textBrowser.toPlainText()}", 0)
        else:
            say("Сегодня у вас нет задач")
            # ex.settext(f"{d['bot_name']}: Сегодня у вас нет задач", 0)
        self.calendarWidget.clicked.connect(self.calendar_show)

    def calendar_show(self):
        self.date = self.calendarWidget.selectedDate().toString("dd-MM-yyyy")
        if str(self.date[0]) == "0":
            self.date = self.date[1:]
        if self.date not in [i[0] for i in self.res] or \
                len([i[1] for i in self.res]) == 1 \
                and [i[1] for i in self.res] == [""]:
            self.textBrowser.setText("Задач нет.")
        else:
            result = []
            for el in self.res:
                el = list(el)
                for it in range(len(el)):
                    if it > 0:
                        el[it] = el[it].split("|")
                        for note in el[it]:
                            if "None" in note:
                                note = note.replace(" None", "")
                            result.append(note)
            # self.textBrowser.setText("\n".join(result))

    def close_it(self):
        self.close()'''

'''def getPossibleExePaths(appPath):
    if not appPath:
        raise Exception("App Path cannot be None")
    pattern = appPath + ":*exe"
    try:
        returned = subprocess.check_output(['where', pattern]).decode('utf-8')
        listOfPaths = filter(None, returned.split(os.linesep))
        return [i.strip() for i in list(listOfPaths)]
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error getting path for '{appPath}'")


def getAppPath(appName):
    for app in winapps.search_installed(appName):
        installPath = str(app.install_location)
        if installPath and installPath != "None":
            return installPath
    return None'''


def say(words):
    player.volume(30)
    settext(words, 0)
    engine.say(words)
    engine.runAndWait()
    #tts.speak(words)
    player.volume(d["volume"])


def timer():
    try:
        pygame.mixer.music.load("tindinalarm.mp3")
        pygame.mixer.music.play()
    except Exception:
        pass
    # settext(f"{d['bot_name']}: Таймер закончился", 0)


def json_write(d):
    with open("config.json", "w", encoding="UTF8") as f:
        json.dump(d, f)


fl = False

hear_C = 0

no_mic = False


def hear(flag=0):
    rec = sr.Recognizer()
    global last_for_bot, fl, hear_C, device_d, no_mic
    if d["user_name"] != "unknown_user":
        d["cmd_count"] += 1
        json_write(d)
    try:
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')  # defaultInputDevice
        ex.change_mic_box.clear()
        device_d = {}
        for i in range(numdevices):
            if i > 0:
                try:
                    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                        # print(p.get_device_info_by_host_api_device_index(0, i), "ASERFGGBRSDDNR")
                        # ex.change_mic_box.addItem(p.get_device_info_by_host_api_device_index(0, i).get('name'))

                        device_d[p.get_device_info_by_host_api_device_index(0, i).get('name')] = i
                except Exception:
                    pass
        p.terminate()
        try:
            #print(d)
            #print(d["device_index"], device_d[d["device"]], d["device"])
            #print(device_d, d["device_index"], d["device"], device_d[d["device"]], d)
            d["device_index"] = device_d[d["device"]]
            json_write(d)
        except Exception:
            pass
        ex.change_mic_box.addItems(device_d)
        index = ex.change_mic_box.findText(d["device"], Qt.MatchFixedString)
        ex.change_mic_box.setCurrentIndex(index)
        ex.change_mic_box.currentTextChanged.connect(ex.replace_device)
        # print(d)
        if device_d == {} and not no_mic:
            no_mic = True
            raise OSError
        elif device_d != {}:
            no_mic = False
        if last_for_bot:
            player.volume(30)
        with sr.Microphone(device_index=d["device_index"]) as source:  # вот тут падает
            # print("ASDAESFGHTREYHTYEJJYEJUYEEYTJUNHBJT")
            # Бот ожидает нашего голоса
            # Удаление фонового шума с записи
            if d["sens_value"] <= 0:
                rec.adjust_for_ambient_noise(source, duration=1.5)
            else:
                rec.energy_threshold = d["sens_value"]  # может в файл добавлять и тогда норм!!!!!!!!!!!!!!!!!!
            # rec.adjust_for_ambient_noise(source, duration=1.5)  # настройка щумов, может слайдер сделать
            # settext(f"{d['bot_name']}: Говорите", 0)
            # if last_for_bot:
            # say("Говорите")
            # print(hear_C)
            if last_for_bot and hear_C < 1:
                pygame.mixer.music.load("gena_in.mp3")
                pygame.mixer.music.play()
                settext("Говорите", 0)
            timeout = d["slider_value"]
            hear_C += 1
            # print(timeout)
            try:
                audio = rec.listen(source, timeout=timeout)
            except sr.WaitTimeoutError:
                if last_for_bot:
                    pygame.mixer.music.load("gena_out.mp3")
                    pygame.mixer.music.play()
                    player.volume(d["volume"])
                fl = False
                last_for_bot = False
                text = hear(flag)
                return text
        player.volume(d["volume"]) #тестировать
        try:
            # Распознание теста с помощью сервиса GOOGLE
            # fl = False
            try:
                text = rec.recognize_google(audio, language="ru-RU").lower()
            except speech_recognition.RequestError:
                say("Ошибка подключения к серверам google, попробуйте позже")
                global app
                app.quit()
                exit()
            hear_C = 0
            if flag == 2:
                return text
            # Вывод сказанного текста на экран
            for el in opts["alias"]:
                if el in text.split():
                    text = text.split()[text.split().index(el) + 1:]
                    text = " ".join(text)
                    fl = True  # это для того, есть ли обращение к гене
                    break
                else:
                    fl = False
            if fl or last_for_bot:
                # print(text)
                last_for_bot = True
                if flag == 1:
                    return text
                else:
                    main(text)
            '''elif not fl:
                last_for_bot = False
                return text'''
        # Если не распознался тест из аудио
        except sr.UnknownValueError:
            # text = f'{d["bot_name"]}: Не понимаю вас. Повторите.'
            # if last_for_bot:
            # say("Не понимаю вас. Повторите.")
            # settext(text, 0)
            # Начинаем заново слушать
            if last_for_bot:
                pygame.mixer.music.load("gena_out.mp3")
                pygame.mixer.music.play()
            fl = False
            last_for_bot = False
            text = hear(flag)
            return text
    except OSError as e:
        # print(e)
        say("У вас не подключен микрофон")
        say("Подключите микрофон")
        # exit()
    except AttributeError:
        d["device_index"] = 1
        json_write(d)


cc = 1
is_playing = 0
player = player_tracks.Player()


def new_track(player, all_text, text):
    if player.is_flow:
        import random
        with open("playlists.json", encoding="UTF8") as myf:
            pl_d = json.load(myf)
        name = f'{random.choice(pl_d["favorite"])} {random.choice(player.for_favorite)} слушать'
        name_dur = player_tracks.get_track(name)
    else:
        name = all_text[all_text.index(text) + 1:]
        name_dur = player_tracks.get_track(" ".join(name))
    player.add_to_playlist(name_dur[0], name, name_dur[2])
    player.play()
    #player.volume(d["volume"])


def text_to_table(all_text, is_command):
    if not is_command:
        t = " ".join(all_text)
        settext(f'{d["user_name"]}: {t}', 1)


def del_hot_worlds(elem, all_text):
    for i in range(len(all_text)):
        if all_text[i] in elem:
            all_text[i] = ""


def main(text):
    try:
        if not ex.wt:
            global startTime, is_playing, player
            d["cmd_true_count"] += 1
            json_write(d)
            all_text = text.split()
            is_command = False
            for text in all_text:
                if text in opts["cmds"]["change_name"]:
                    text_to_table(all_text, is_command)
                    say("Как мне вас называть?")
                    # settext(f'{d["bot_name"]}: Как мне вас называть?', 0)
                    name = hear(1)
                    d["user_name"] = name.title()
                    # ex.user_name.setText(d["user_name"])
                    say(f"Успешно. Теперь я буду называть вас {d['user_name']}")
                    # ex.settext(f"Успешно. Теперь я буду называть вас {d['user_name']}", 0)
                    json_write(d)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["change_name"], all_text)
                elif text in opts["cmds"]["ctime"]:
                    text_to_table(all_text, is_command)
                    now = datetime.now()
                    if now.minute < 10:
                        say("Сейчас " + str(now.hour) + ":" + '0' + str(now.minute))
                        # ex.settext(f'{d["bot_name"]}: Сейчас {str(now.hour)}:0{str(now.minute)}', 0)
                    else:
                        say("Сейчас " + str(now.hour) + ":" + str(now.minute))
                        # ex.settext(f'{d["bot_name"]}: Сейчас {str(now.hour)}:{str(now.minute)}', 0)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["ctime"], all_text)
                elif text in opts["cmds"]["ai_gpt"]["question"]:
                    if d["gpt_token"] != "invalid":
                        text_to_table(all_text, is_command)
                        t = " ".join(all_text)
                        say("секунду, сейчас подумаю")
                        ts = quest_or_task("short", t, d["gpt_token"])
                        say(ts.strip("\n"))
                    else:
                        say("Проверьте токен в настройках")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["ai_gpt"]["question"], all_text, ex)
                elif text in opts["cmds"]["ai_gpt"]["school_task"]:
                    if d["gpt_token"] != "invalid":
                        text_to_table(all_text, is_command)
                        t = " ".join(all_text)
                        # поток
                        say("Начинаю работать. Результат будет разделе работ chat GPT")
                        # ex.ai_table.insertRow(0)
                        # downloadButton = QPushButton('Скачать') #добавлять кнопку при выполнении функции в ai_gpt
                        # ex.ai_table.setCellWidget(0, 0, downloadButton) #не работаеееет
                        # ex.ai_table.setItem(0, 0, QTableWidgetItem(t))
                        # ex.ai_table.setItem(0, 1, QTableWidgetItem("Генерация"))
                        ex.ai_table.resizeRowsToContents()
                        ex.ai_table.setVerticalHeaderItem(0, QTableWidgetItem(""))
                        # это если делать полупрозрачное поле, пока генерируется
                        with open("ai_tasks.json", encoding="UTF8") as myf:
                            ai_d = json.load(myf)
                        for x in '\/:*?"<>|':
                            t = t.replace(x, " ")
                        ai_d[t] = "generating!@#"
                        # print(ai_d[t])
                        with open("ai_tasks.json", "w", encoding="UTF8") as f:
                            json.dump(ai_d, f)
                        thread1 = threading.Thread(target=quest_or_task,
                                                   args=(["long", t, d["gpt_token"]]))
                        thread1.start()
                    else:
                        say("Проверьте токен")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["ai_gpt"]["school_task"], all_text)
                elif text in opts["cmds"]["tracks"]["favor"]:
                    text_to_table(all_text, is_command)
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    name = all_text[all_text.index(text) + 1:]
                    n = ""
                    for i in name:
                        if i not in opts["cmds"]["tracks"]["favor"]:
                            n += f"{str(i)} "
                        else:
                            all_text.remove(i)
                    n = n.replace(" и ", "|").strip().split("|")
                    if "удали" not in all_text and "убери" not in all_text:
                        while True:
                            if n != [""]:
                                is_already_appended = True
                                for isp in n:
                                    print(isp, pl_d["favorite"])
                                    if isp not in pl_d["favorite"] and isp != "":
                                        pl_d["favorite"].append(isp)
                                        is_already_appended = False
                                with open("playlists.json", "w", encoding="UTF8") as f:
                                    json.dump(pl_d, f)
                                if is_already_appended:
                                    say("это уже добавлено в ваши предпочтения")
                                else:
                                    say("Добавлено")
                                break
                            else:
                                say("Что вам нравится слушать?")
                                n = hear(1)
                                n = n.replace(" и ", "|").strip().split("|")
                    else:
                        while True:
                            if n != [""]:
                                is_not_in_favorites = True
                                for del_it in n:
                                    if del_it in pl_d["favorite"] and del_it != "":
                                        pl_d["favorite"].remove(del_it)
                                        is_not_in_favorites = False
                                with open("playlists.json", "w", encoding="UTF8") as f:
                                    json.dump(pl_d, f)
                                if is_not_in_favorites:
                                    say("Не найдено такого в ваших предпочтениях")
                                else:
                                    say("Удалено")
                                break
                            else:
                                say("Что мне нужно удалить?")
                                n = hear(1)
                                n = n.replace(" и ", "|").strip().split("|")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["favor"], all_text)
                elif text in opts["cmds"]["tracks"]["from_pl"] and "включи" in all_text:
                    text_to_table(all_text, is_command)
                    from random import shuffle
                    # say("джарвис говно, он такого не умеет")
                    player.stop()
                    say("Включаю")
                    player = player_tracks.Player()
                    player.is_flow = False
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    # print(pl_d)
                    name = all_text[all_text.index(text) + 1:]
                    n = "<>!<>!"
                    for i in name:  # плейлист негр 1 и негр 2 будет конфликт
                        for x in pl_d.keys():
                            if i in x or i == x:
                                n = x
                                break
                    # print(n)
                    if n == "<>!<>!":
                        say("Такого плейлиста не существует")
                    else:
                        shuffle(pl_d[n])
                        for i in pl_d[n]:
                            # print(i)
                            player.add_to_playlist(f"/music/{i[0]}.m4a", i[0], i[1])  # доделать
                        player.play()
                        player.volume(d["volume"])
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["from_pl"], all_text)
                elif text in opts["cmds"]["tracks"]["next"]:
                    text_to_table(all_text, is_command)
                    player.next_track()
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["next"], all_text)
                elif text in opts["cmds"]["tracks"]["last"]:
                    text_to_table(all_text, is_command)
                    player.previous_track()
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["last"], all_text)
                elif text in opts["cmds"]["tracks"]["tracks"]:
                    text_to_table(all_text, is_command)
                    player.stop()
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    if len(pl_d["favorite"]) > 0:
                        say("Включаю")
                        player = player_tracks.Player()
                        player.is_flow = True
                        thread1 = threading.Thread(target=new_track,
                                                   args=([player, all_text, text]))  # вывод ошибки, что не скачал
                        thread1.start()
                    else:
                        say("Вы не добавили предпочтений, я не могу включить поток")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["tracks"], all_text)
                elif text in opts["cmds"]["tracks"][
                    "playlist_del"] and "удали" in all_text:  # обработка на существование плейлиста
                    text_to_table(all_text, is_command)
                    # print("QWE")
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    pl_name = all_text[all_text.index(text) + 1:]
                    pl_name = "_".join(pl_name)
                    name_url = player.playlist[player.current_track][7:-4]
                    # print(f"{os.getcwd()}\music\{name_url}.m4a")
                    while True:
                        # print("ЦИИИИИКЛ")
                        if pl_name == "":
                            say("Скажите название плейлиста")
                            pl_name = hear(1)
                        else:
                            # print("НАЧАЛ УДАЛЯТЬ", name_url, [i[0] for i in pl_d[pl_name]])
                            elem = ("", "")
                            for i in pl_d[pl_name]:
                                if name_url == i[0]:
                                    elem = i
                            if name_url in [i[0] for i in pl_d[pl_name]]:  # не попадает в иф даже
                                # print("QWEQWE")
                                player.next_track()
                                # print("WAAAT")
                                os.remove(
                                    f"{os.getcwd()}\music\{name_url}.m4a")  # тк трек может быть и в другом плейлисте
                                pl_d[pl_name].remove(list(elem))
                                if len(pl_d[pl_name]) == 0:
                                    pl_d.pop(pl_name)
                                with open("playlists.json", "w", encoding="UTF8") as f:
                                    # print(pl_d)
                                    json.dump(pl_d, f)
                                say("Удалено")
                                break
                            else:
                                say(f"Трека нет в плейлисте {pl_name.replace('_', ' ')}")
                                break
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["playlist_del"], all_text)
                elif text in opts["cmds"]["tracks"]["playlist_add"]:
                    text_to_table(all_text, is_command)
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    pl_name = all_text[all_text.index(text) + 1:]
                    pl_name = "_".join(pl_name)
                    # j_name = player.playlist[player.current_track][7:-4]
                    name_url = player.cur_track()
                    # print(pl_name)
                    while True:
                        try:
                            if pl_name != "" and list(name_url) != ["", ""] and name_url[-1] not in [i[-1] for i in
                                                                                                     pl_d[pl_name]]:
                                try:
                                    say("Добавляю трек")
                                    thread1 = threading.Thread(target=player_tracks.download_audio,
                                                               args=([name_url[1], name_url[0], pl_name,
                                                                      name_url]))  # если файл не скачается, но добавится, чё будет)))
                                    thread1.start()
                                    # #print(thread1)
                                except Exception:  # youtube_dl.utils.DownloadError:
                                    say("трек не скачан")
                                break
                            elif pl_name == "":
                                say("Скажите название плейлиста")
                                pl_name = hear(1)
                            elif list(name_url) == ["", ""]:
                                say("Сейчас ничего не играет")
                                break
                            else:
                                say("Трек уже находится в плейлисте")
                                break
                        except Exception as e:
                            # print(e)
                            say("Плейлист создан")
                            with open("playlists.json", encoding="UTF8") as myf:
                                pl_d = json.load(myf)
                            pl_d[pl_name.replace(" ", "_")] = []
                            with open("playlists.json", "w", encoding="UTF8") as f:
                                json.dump(pl_d, f)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["playlist_add"], all_text)
                elif text in opts["cmds"]["tracks"]["volume"]:
                    text_to_table(all_text, is_command)
                    vols = {"ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5, "шесть": 6, "семь": 7,
                            "восем": 8, "девять": 9}
                    vol = all_text[all_text.index(text) + 1:]
                    n = "!"
                    for i in vol:
                        if i.isdigit():
                            n = int(i)
                            break
                        elif i in vols.keys():
                            n = vols[i]
                            break
                    if n == "!":
                        say("Не понял вас")
                    else:
                        player.volume(n)
                        d["volume"] = n
                        json_write(d)
                        say("Успешно")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["volume"], all_text)
                elif text in opts["cmds"]["tracks"]["play"] and "плейлист" not in all_text and "поток" not in all_text and "волна" not in all_text:
                    text_to_table(all_text, is_command)
                    player.stop()
                    say("Включаю")
                    player = player_tracks.Player()
                    thread1 = threading.Thread(target=new_track,
                                               args=([player, all_text, text]))  # вывод ошибки, что не скачал
                    thread1.start()
                    player.is_flow = True
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["play"], all_text)
                elif text in opts["cmds"]["tracks"]["favor_name"]:
                    text_to_table(all_text, is_command)
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    if len(pl_d["favorite"]) > 0:
                        rs = '\n'.join(pl_d['favorite'])
                        settext(f"Ваши предпочтения:\n{rs}", 0)
                        say("Вывел ваши предпочтения в диалог")
                    else:
                        say("Вы не добавили предпочтения")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["favor_name"], all_text)
                elif text in opts["cmds"]["tracks"]["playlists_name"]:
                    text_to_table(all_text, is_command)
                    with open("playlists.json", encoding="UTF8") as myf:
                        pl_d = json.load(myf)
                    if len(list(pl_d.keys())[1::]) > 0:
                        rs = '\n'.join(list(pl_d.keys())[1::])
                        settext(f"Ваши плейлисты:\n{rs.replace('_', ' ')}", 0)
                        say("Вывел ваши плейлисты в диалог")
                    else:
                        say("У вас нет плейлистов")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["playlists_name"], all_text)
                elif text in opts["cmds"]["tracks"]["pause"]:
                    text_to_table(all_text, is_command)
                    player.pause()
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["pause"], all_text)
                elif text in opts["cmds"]["tracks"]["resume"]:
                    text_to_table(all_text, is_command)
                    player.resume()
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["resume"], all_text)
                elif text in opts["cmds"]["tracks"]["stop"]:
                    text_to_table(all_text, is_command)
                    player.stop()
                    is_playing = 0
                    is_command = True
                    del_hot_worlds(opts["cmds"]["tracks"]["stop"], all_text)
                # elif text in opts["cmds"]["find"]:
                #    text_to_table(all_text, is_command)
                #    all_text = all_text[all_text.index(text) + 1:]
                #    find = all_text
                #    if len(find) > 1:
                #        find = " ".join(find)
                #    else:
                #        find = find[0]
                #    say('Сейчас найду')
                #    # settext(f'{d["bot_name"]}: Сейчас найду', 0)
                #    webbrowser.open('https://www.google.com/search?safe=active&q=' + find, new=2)
                #    is_command = True
                elif text in opts["cmds"]["google"]:
                    text_to_table(all_text, is_command)
                    say("Открываю")
                    # ex.settext(f'{d["bot_name"]}: Открываю', 0)
                    webbrowser.open('https://www.google.com/', new=2)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["google"], all_text)
                elif text in opts["cmds"]["VK"]:
                    text_to_table(all_text, is_command)
                    say("Открываю")
                    # ex.settext(f'{d["bot_name"]}: Открываю', 0)
                    webbrowser.open('https://www.vk.com/feed', new=2)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["VK"], all_text)
                elif text in opts["cmds"]["YT"]:
                    text_to_table(all_text, is_command)
                    say("Открываю")
                    # ex.settext(f'{d["bot_name"]}: Открываю', 0)
                    webbrowser.open('https://youtube.com', new=2)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["YT"], all_text)
                elif text in opts["cmds"]["stopwatch_start"] and "запусти" in all_text:
                    text_to_table(all_text, is_command)
                    say("Секундомер запущен")
                    # ex.settext(f'{d["bot_name"]}: Секундомер запущен', 0)
                    startTime = time.time()
                    is_command = True
                    del_hot_worlds(opts["cmds"]["stopwatch_start"], all_text)
                elif text in opts["cmds"]["stopwatch_stop"] and "останови" in all_text:
                    text_to_table(all_text, is_command)
                    if startTime != 0:
                        morph = pymorphy2.MorphAnalyzer()
                        minutes = morph.parse('минута')[0]
                        hours = morph.parse('час')[0]
                        second = morph.parse('секунда')[0]
                        Time = time.time() - startTime
                        say(f"Прошло {round(Time // 3600)} "
                            f"{hours.make_agree_with_number(round(Time // 3600)).word} "
                            f"{round(Time // 60)} "
                            f"{minutes.make_agree_with_number(round(Time // 60)).word} {round(Time % 60)} "
                            f"{second.make_agree_with_number(round(Time % 60)).word}")
                        # ex.settext(
                        # f'{d["bot_name"]}: Прошло {round(Time // 3600)}'
                        # f' {hours.make_agree_with_number(round(Time // 3600)).word} '
                        # f'{round(Time // 60)} '
                        # f'{minutes.make_agree_with_number(round(Time // 60)).word} {round(Time % 60)} '
                        # f'{second.make_agree_with_number(round(Time % 60)).word}', 0)
                        startTime = 0
                    else:
                        say("Секундомер не включен")
                        # ex.settext(f'{d["bot_name"]}: Секундомер не включен', 0)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["stopwatch_stop"], all_text)
                elif text in opts["cmds"]["timer"]:
                    text_to_table(all_text, is_command)
                    # times = {60: "минуту минута минуты минут",
                    # 3600: "час часа часов",
                    # 1: "секунду сукунд секунды"}
                    times = {"минут": 60, "минута": 60, "минуты": 60, "минуту": 60, "час": 3600, "часа": 3600,
                             "часов": 3600, "секунду": 1, "секунд": 1, "секунды": 1}
                    # для того, чтобы можно было устанавливать время в разных величинах
                    # ex.settext(f'{d["bot_name"]}: На какое время поставить таймер?', 0)
                    # tim = hear(1)
                    for i in times.keys():
                        if i in " ".join(all_text):
                            flag = times[i]
                            for j in all_text:
                                if j.isdigit():
                                    item = int(j)
                                    texzt = "Таймер установлен"
                                    break
                            break
                        else:
                            flag = 60
                            item = 1
                            texzt = "Таймер на минуту установлен"
                    item = int(item) * flag
                    say(texzt)
                    # ex.settext(f'{d["bot_name"]}: Таймер установлен', 0)
                    Timer = threading.Timer(item, timer)
                    Timer.start()
                    # ex.settext(f'{d["bot_name"]}: Не понимаю вас, повторите', 0)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["timer"], all_text)
                elif text in opts["cmds"]["notes"]:
                    text_to_table(all_text, is_command)
                    if "добавь" in all_text or "добавить" \
                            in all_text or "запиши" in all_text or "записать" in all_text:
                        item = all_text[all_text.index(text) + 1:]
                        while True:
                            if len(item) > 0:  # если есть заметка, которую нужно добавить
                                with open("notes.txt", "a", encoding="UTF-8") as myfile:
                                    myfile.write(" ".join(item) + "\n")
                                say(f"Заметка {' '.join(item)} добавлена")
                                # ex.settext(f"{d['bot_name']}: Заметка {' '.join(item)} добавлена", 0)
                                break
                            else:
                                say(f"Вы не указали заметку, которую нужно добавить")
                                # ex.settext(f"{d['bot_name']}: Вы не указали заметку, которую нужно добавить", 0)
                                say("Какую замектку я должен добавить?")
                                # ex.settext(f"{d['bot_name']}: Какую замектку я должен добавить?", 0)
                                item = hear(1).split()
                    elif "удали" in all_text or "удалить" in all_text:
                        item = all_text[all_text.index(text) + 1:]
                        with open("notes.txt", "r", encoding="UTF-8") as myfile:
                            rd = myfile.readlines()
                        if " ".join(all_text) == "удали все заметки" or " ".join(all_text) == "удали заметки":
                            say("Вы точно хотите, чтобы я удалил все заметки?")
                            # ex.settext(f"{d['bot_name']}: Вы точно хотите, чтобы я удалил все заметки?", 0)
                            agree = hear(1)
                            if "да" in agree.split():
                                with open("notes.txt", "w", encoding="UTF-8") as myfile:
                                    myfile.writelines("")
                                say(f"Все заметки удалены")
                                # ex.settext(f"{d['bot_name']}: Все заметки удалены", 0)
                            elif "нет" in agree.split():
                                say("Заметки были сохранены")
                                # ex.settext(f"{d['bot_name']}: Заметки были сохранены", 0)
                        elif " ".join(item) + "\n" in rd:
                            rd.remove(" ".join(item) + "\n")
                            with open("notes.txt", "w", encoding="UTF-8") as myfile:
                                myfile.writelines(rd)
                            say(f"Заметка {' '.join(item)} удалена")
                            # ex.settext(f"{d['bot_name']}: Заметка {' '.join(item)} удалена", 0)
                        elif item not in rd:
                            say("Такой заметки не существует")
                            # ex.settext(f"{d['bot_name']}: Такой заметки не существует", 0)
                    else:
                        with open("notes.txt", "r", encoding="UTF-8") as myfile:
                            rd = myfile.read()
                        if rd != "":  # есть ли вообще заметки?
                            say(f"Ваши заметки: {rd}")
                            # ex.settext(f"{d['bot_name']}: Ваши заметки:\n{rd}", 0)
                        else:
                            say(f"у вас нет заметок")
                            # ex.settext(f"{d['bot_name']}: У вас нет заметок", 0)
                    '''                        else:
                            say("Я не понимаю, что мне нужно сделать с заметками. Повторите, пожалуйста")
                            # ex.settext(f"{d['bot_name']}: "
                            # f"Я не понимаю, что мне нужно сделать с заметками. "
                            # f"Повторите, пожалуйста", 0)
                            all_text = hear(1)'''
                    is_command = True
                    del_hot_worlds(opts["cmds"]["notes"], all_text)
                elif text in opts["cmds"]["turn_off"]:
                    text_to_table(all_text, is_command)
                    say(f"До свидания, {d['user_name']}")
                    global app
                    app.quit()
                    exit()
                elif text in opts["cmds"]["waiting_mode"]:  # переделать
                    text_to_table(all_text, is_command)
                    ex.wait_box.setChecked(True)
                    ex.wt = True
                    say("Я нахожусь в режиме ожидания")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["waiting_mode"], all_text)
                elif text in opts["cmds"]["hide_window"] and ("все" in all_text or "всё" in all_text):
                    text_to_table(all_text, is_command)
                    app_list = get_app_list()
                    for el in app_list:
                        win32gui.ShowWindow(el[0], win32con.SW_MINIMIZE)
                    say("Успешно")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["hide_window"], all_text)
                elif text in opts["cmds"]["open_window"]:  # добавить ещё несколько дефолтных прог
                    text_to_table(all_text, is_command)
                    app_list = get_app_list()

                    # print(all_text, app_list)

                    def open_prog(i):
                        el = i[0]
                        shell = win32com.client.Dispatch("WScript.Shell")
                        shell.SendKeys('%')
                        win32gui.ShowWindow(el, win32con.SW_MAXIMIZE)
                        win32gui.SetForegroundWindow(el)

                    if "все" in all_text or "всё" in all_text:
                        for el in app_list:
                            win32gui.ShowWindow(el[0], win32con.SW_MAXIMIZE)
                        say("Успешно")
                    else:
                        is_prog_open = False
                        if "опера" in all_text or "оперу" in all_text:
                            for i in app_list:
                                if "opera" in i[-1].lower():
                                    open_prog(i)
                                    is_prog_open = True
                                    break
                                else:
                                    is_prog_open = False
                        elif "discord" in all_text or "дискорд" in all_text:
                            for i in app_list:
                                if "discord" in i[-1].lower():
                                    open_prog(i)
                                    is_prog_open = True
                                    break
                                else:
                                    is_prog_open = False
                        elif "проводник" in all_text or "файлы" in all_text:
                            for i in app_list:
                                if "проводник" in i[-1].lower():
                                    open_prog(i)
                                    is_prog_open = True
                                    break
                                else:
                                    is_prog_open = False
                        elif "калькулятор" in all_text:
                            for i in app_list:
                                if "калькулятор" in i[-1].lower():
                                    open_prog(i)
                                    is_prog_open = True
                                    break
                                else:
                                    is_prog_open = False
                        if is_prog_open:
                            say("Успешно")
                        else:
                            say("Приложение не найдено")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["open_window"], all_text)
                elif text in opts["cmds"]["next_window"]:
                    text_to_table(all_text, is_command)
                    app_list = get_app_list()
                    global cc
                    # print(app_list)
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shell.SendKeys('%')
                    win32gui.SetForegroundWindow(app_list[cc][0])
                    hwnd = win32gui.GetForegroundWindow()
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    # win32gui.ShowWindow(app_list[cc][0], 5)
                    cc += 1
                    if cc >= len(app_list) - 1:
                        cc = 0
                    say("Успешно")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["next_window"], all_text)
                elif text in opts["cmds"]["hide_this_window"]:
                    text_to_table(all_text, is_command)
                    hwnd = win32gui.GetForegroundWindow()
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    say("Успешно")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["hide_this_window"], all_text)
                elif text in opts["cmds"]["screenshot"]:
                    text_to_table(all_text, is_command)
                    pyautogui.hotkey("win", "printscreen")
                    say("Успешно")  # мб добавить, чтобы говорил, куда сохраняет(дефолт путь изображения -> снимки экрана)
                    is_command = True
                    del_hot_worlds(opts["cmds"]["screenshot"], all_text)
                elif text in opts["cmds"]["programms"] and can_open(all_text):
                    text_to_table(all_text, is_command)
                    search_true = False
                    try:
                        say("запускаю")
                        assist_dir = os.path.dirname(os.path.abspath(__file__))
                        # print(text)
                        is_url = False
                        if "калькулятор" in all_text[all_text.index(text) + 1:]:
                            t = "calc"
                            subprocess.Popen(t)
                        elif "проводник" in all_text[all_text.index(text) + 1:]:
                            t = "explorer"
                            subprocess.Popen(t)
                        '''elif "диспетчер" in all_text[all_text.index(text) + 1:] and "задач" in all_text[
                                                                                               all_text.index(
                                                                                                   text) + 1:]:
                            t = "taskmgr"
                            subprocess.Popen(t)'''
                        if "dota" in all_text[all_text.index(text) + 1:] or "доту" in all_text[
                                                                                      all_text.index(text) + 1:]:
                            t = "steam://rungameid/570"
                            is_url = True
                            search_true = True
                        elif "cs" in all_text[all_text.index(text) + 1:] or "каэску" in all_text[
                                                                                        all_text.index(
                                                                                            text) + 1:] or "кс" in all_text[
                                                                                                                   all_text.index(
                                                                                                                       text) + 1:]:
                            t = "steam://rungameid/730"
                            is_url = True
                            search_true = True
                        elif "honor" in all_text[all_text.index(text) + 1:] or "ворона" in all_text[
                                                                                           all_text.index(text) + 1:]:
                            t = "steam://rungameid/304390"
                            is_url = True
                            search_true = True

                        def open_prog(name_exe, path, disc="D:"):
                            t = find_file(name_exe, path, "D:")  # последний аргумент никак не влияет
                            if t != "already_open":
                                with open("programs.json", "w",
                                          encoding="UTF8") as myfile:  # работает только с discord.exe
                                    # print("OK", t)
                                    json.dump(t[1], myfile)

                                t = os.path.abspath(t[0])
                                subprocess.Popen(t)

                        if "steam" in all_text[all_text.index(text) + 1:] or "стим" in all_text[
                                                                                       all_text.index(text) + 1:]:
                            say("Подождите немного")
                            open_prog("steam.exe", "/", "D:")
                            '''thread_pr = threading.Thread(target=open_prog, args=["steam.exe", "/", "D:"])
                            thread_pr.start()'''
                        if "discord" in all_text[all_text.index(text) + 1:] or "дискорд" in all_text[
                                                                                            all_text.index(text) + 1:]:
                            say("Подождите немного")
                            open_prog("Discord.exe", "/", "D:")
                            '''thread_pr = threading.Thread(target=open_prog("Discord.exe", "/", "D:"), args=())
                            thread_pr.start()'''
                        elif not search_true:
                            t = ""
                        os.chdir(assist_dir)
                        if is_url:
                            def run_game(t):
                                # print(t)
                                webbrowser.open(t)  # тест всех прог

                            thread_gm = threading.Thread(target=run_game, args=[t])
                            thread_gm.start()
                    except subprocess.CalledProcessError:
                        say("Такого приложения нет")
                    is_command = True
                    del_hot_worlds(opts["cmds"]["programms"], all_text)
                # else:
                # is_command = False
                # print(text, all_text, is_command)
            if not is_command:
                global fl, last_for_bot
                if not fl:
                    pygame.mixer.music.load("gena_out.mp3")
                    pygame.mixer.music.play()
                    fl = False
                    last_for_bot = False
                player.volume(d["volume"])
                hear()
    except Exception as e:
        import traceback
        with open("LOGS.txt", "a+") as f:
            f.write(f"DEF MAIN ERROR: {traceback.format_exc()}\n")
        # print(traceback.format_exc())
        # print(e, "ERROR", all_text, text)


# запуск

def sleep_before_start():
    global last_for_bot
    if d["user_name"] == "unknown_user" or d["user_name"] is None:
        say("Здравствуйте, как вас зовут?")
        pygame.mixer.music.load("gena_in.mp3")
        pygame.mixer.music.play()
        settext("Говорите", 0)
        oleg = 0
        while True:
            name = hear(2)
            if name is not None:
                break
            elif oleg == 0 and name is None: #тестировать
                say("Пожалуйста, включите доступ к микрофону в параметрах windows")
                oleg += 1
            # print(name)
        d["user_name"] = name
        json_write(d)
        say("Хорошо, я буду называть вас " + name)
        last_for_bot = True
        # add_to_startup()
    else:
        say('Здравствуйте!' + d["user_name"])
        last_for_bot = True
    while True:
        # #print(ex.waiting())
        # if not ex.waiting():
        if not ex.wt:
            try:
                # print("HEAR")
                hear()
            except speech_recognition.WaitTimeoutError:
                pass
        # беск цикл, если такой иф. обработать возможность открытия главного окна
        # asyncio.sleep(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = main20()
    # icon = app.style().standardIcon(QStyle.SP_DirOpenIcon)
    icon = QIcon('images/main logo.png')
    tray = QSystemTrayIcon(icon)
    menu = QMenu()
    action_open = menu.addAction("Открыть")
    action_open.triggered.connect(ex.show)
    action_quit = menu.addAction("Закрыть")
    action_quit.triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.activated.connect(lambda x: menu.exec(tray.geometry().center()))
    tray.show()
    tray.setToolTip("Гена")
    tray.showMessage("Гена", "Ассистент запущен и находится в трее")
    # обработка на 1 запуск
    # print("QWE")
    thread = threading.Thread(target=sleep_before_start, args=())
    thread.daemon = True
    thread.start()
    # print("QWEQWE")
    app.exec()

    '''# Для примера, иконка трея взята из стилей Qt
    icon = app.style().standardIcon(QStyle.SP_DirOpenIcon)

    # Иконка из файла
    # icon = QIcon('favicon.ico')

    tray = QSystemTrayIcon(icon)

    menu = QMenu()
    action_settings = menu.addAction("Open")
    action_settings.triggered.connect(lambda: QMessageBox.open(ex))

    action_quit = menu.addAction("Quit")
    action_quit.triggered.connect(app.quit)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda x: menu.exec(tray.geometry().center()))

    tray.show()

    app.exec()'''

'''        self.tray_icon = QSystemTrayIcon(self)
        icon = app.style().standardIcon(QStyle.SP_DirOpenIcon)
        self.tray_icon.setIcon(QIcon(icon))


        self.tray_menu = QMenu()
        self.action_open = self.tray_menu.addAction("Открыть")
        self.action_open.triggered.connect(self.show)
        #self.action_quit = self.tray_menu.addAction("Закрыть")
        #self.action_quit.triggered.connect(self.quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()'''
