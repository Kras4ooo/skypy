# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginDesign.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!
import json

from PyQt5 import QtCore, QtGui, QtWidgets
from codebase.client.client import Client
from codebase.frontend.main import MainWindow
from codebase.utils.singleton import Singleton


class Events(metaclass=Singleton):
    def __init__(self, window):
        self.window = window

    def push_button_event(self, main_window_instance):
        call_function_register = lambda: self.push_register_action(main_window_instance)
        call_function_login = lambda: self.push_login_action(main_window_instance)
        main_window_instance.pushButton_2.clicked.connect(call_function_register)
        main_window_instance.pushButton.clicked.connect(call_function_login)

    def push_register_action(self, main_window_instance):
        data = {
            'first_name': main_window_instance.lineEdit_3.text(),
            'username': main_window_instance.lineEdit_4.text(),
            'password': main_window_instance.lineEdit_5.text(),
            'public_key': Client.get_or_generate_key()[1].decode('utf-8'),
        }
        sock = Client.register_user(data)
        response = sock.recv(1024).decode('utf-8')
        response = json.loads(response)

        if response['is_success'] is True:
            main_window_instance.label_6.setText("Register successfully")
        else:
            main_window_instance.label_6.setText("User exist")

    def push_login_action(self, main_window_instance):
        data = {
            'username': main_window_instance.lineEdit.text(),
            'password': main_window_instance.lineEdit_2.text(),
            'public_key': Client.get_or_generate_key()[1].decode('utf-8'),
        }
        sock = Client.login_user(data)
        response = sock.recv(1024).decode('utf-8')
        response = json.loads(response)

        if response['is_correct'] is True:
            """
            Close this Window and open main
            """
            main_window_instance.label_7.setText("Correct User")
            main_window_instance.Form.close()
            main_window = QtWidgets.QMainWindow()
            w = MainWindow()
            w.setup_ui(main_window)
            app.setActiveWindow(main_window)
            main_window.show()
            app.exec()
        else:
            main_window_instance.label_7.setText("Not Correct")


class Ui_Form(object):
    def setupUi(self, Form):
        self.Form = Form
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 401, 301))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(130, 50, 201, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 100, 201, 20))
        self.lineEdit_2.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton = QtWidgets.QPushButton(self.tab)
        self.pushButton.setGeometry(QtCore.QRect(180, 180, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(60, 50, 61, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(60, 100, 61, 16))
        self.label_2.setObjectName("label_2")
        self.label_7 = QtWidgets.QLabel(self.tab)
        self.label_7.setGeometry(QtCore.QRect(80, 10, 211, 16))
        self.label_7.setText("")
        self.label_7.setObjectName("label_7")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.label_3 = QtWidgets.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(50, 80, 61, 16))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(50, 110, 61, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(50, 50, 71, 16))
        self.label_5.setObjectName("label_5")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(130, 50, 231, 20))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_4.setGeometry(QtCore.QRect(130, 80, 231, 20))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.lineEdit_5 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_5.setGeometry(QtCore.QRect(130, 110, 231, 20))
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.pushButton_2 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_2.setGeometry(QtCore.QRect(190, 160, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label_6 = QtWidgets.QLabel(self.tab_2)
        self.label_6.setGeometry(QtCore.QRect(90, 10, 221, 16))
        self.label_6.setText("")
        self.label_6.setObjectName("label_6")
        self.tabWidget.addTab(self.tab_2, "")

        ev = Events(self)
        ev.push_button_event(self)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "Login"))
        self.label.setText(_translate("Form", "Username:"))
        self.label_2.setText(_translate("Form", "Password:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Login"))
        self.label_3.setText(_translate("Form", "Username:"))
        self.label_4.setText(_translate("Form", "Password:"))
        self.label_5.setText(_translate("Form", "First Name:"))
        self.pushButton_2.setText(_translate("Form", "Register"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Register"))

if __name__ == '__main__':
    import sys, os
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    val = app.exec()
    os._exit(val)
