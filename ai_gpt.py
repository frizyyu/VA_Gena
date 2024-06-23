import os
import openai
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog, QSystemTrayIcon, QMenu, QMessageBox, \
    QStyle, QWidget, QAction, QPushButton

'''#написание кода по тексту
code = openai.Completion.create(
  model="text-davinci-003",
  prompt="как на python написать код, который выводит привет мир",
  temperature=0,
  max_tokens=100,
  top_p=1.0,
  frequency_penalty=0.2,
  presence_penalty=0.0
)
#описание полученного кода
exp_code = openai.Completion.create(
  model="code-davinci-002",
  prompt=f'{code["choices"][0]["text"].strip()}\n\n\"\"\"\nHere is what the code is doing:\n1.',
  temperature=0,
  max_tokens=64,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0,
  stop=["\"\"\""]
)'''


def check_token(token):
    try:
        openai.api_key = token
        code = openai.Completion.create(
            model="text-davinci-003",
            prompt="как на python написать код, который выводит привет мир",
            temperature=0,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.2,
            presence_penalty=0.0
        )
        return "valid"
    except openai.error.AuthenticationError:
        return "invalid"


def to_ai_table(ex, text, token):
    openai.api_key = token
    # row_c = ex.ai_table.rowCount()
    ex.ai_table.insertRow(0)
    ex.ai_table.setItem(0, 0, QTableWidgetItem(text))
    downloadButton = QPushButton('Скачать')
    ex.ai_table.setCellWidget(0, 1, downloadButton)
    ex.ai_table.resizeRowsToContents()
    ex.ai_table.setVerticalHeaderItem(0, QTableWidgetItem(""))
    # ex.ai_table.scrollToBottom()

import json


def quest_or_task(about_lenght, text, token):
    try:
        print("НАЧАЛ ПИСАТЬ СОЧИНЕНИЕ")
        openai.api_key = token
        if about_lenght == "short":
            text += " кратко"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.3,
            max_tokens=1024,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        # response = {"choices": [{"text": "QWQWEQWE"}]}
        if about_lenght == "long":
            with open("ai_tasks.json", encoding="UTF8") as myf:
                ai_d = json.load(myf)
                myf.close()
            if text in ai_d.keys(): #тест
                ai_d[text] = response["choices"][0]["text"]
            print(response["choices"][0]["text"])
            with open("ai_tasks.json", "w", encoding="UTF8") as f:
                json.dump(ai_d, f)
            return 0
            # тут сохранение в json и может муз сигнал
        return response["choices"][0]["text"]
    except openai.error.AuthenticationError:
        with open("config.json", encoding="UTF8") as myf:
            ai_d = json.load(myf)
            myf.close()
        ai_d["gpt_token"] = "invalid" #оно будто не работает
        with open("config.json", "w", encoding="UTF8") as f:
            json.dump(ai_d, f)
        if about_lenght == "long":
            with open("ai_tasks.json", encoding="UTF8") as myf:
                ai_d = json.load(myf)
                myf.close()
            ai_d[text] = "Ошибка аутентификации. Проверьте токен"
            with open("ai_tasks.json", "w", encoding="UTF8") as f:
                json.dump(ai_d, f)
            return 0
        return "Ошибка аутентификации. Проверьте токен"


# print(response["choices"][0]["text"], response)
