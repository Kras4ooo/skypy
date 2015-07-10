import socket
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QFont, QIcon
from PyQt5.QtWidgets import QListWidgetItem, QAbstractItemView, QFileDialog
import struct
from codebase.client.client import Client
from codebase.utils.singleton import Singleton
import json


class Events(metaclass=Singleton):
    def __init__(self, window, username, sock):
        self.username = username
        self.client = Client(username=self.username, parent=window,
                             socket=sock)
        Client.WINDOW = window
        self.client.start()
        self.client.add_tab_signal.connect(self.add_tab_from_client)
        self.window = window

    def push_button_event(self, main_window_instance):
        call_function = lambda: self.push_button_action(main_window_instance)
        call_function2 = lambda tab: self.on_listView_clicked(main_window_instance, tab)
        call_function3 = lambda tab: self.close_tab(main_window_instance, tab)
        call_function4 = lambda: self.send_file(main_window_instance)
        main_window_instance.push_button.clicked.connect(call_function)
        main_window_instance.list_view.doubleClicked.connect(call_function2)
        main_window_instance.tab_widget.tabCloseRequested.connect(call_function3)
        main_window_instance.browse_button.clicked.connect(call_function4)

    def push_button_action(self, main_window_instance):
        line_text = main_window_instance.line_edit.text()
        current_tab = main_window_instance.tab_widget.currentWidget()
        current_widget = current_tab.children()[0]
        item = QListWidgetItem(current_widget)
        check_for_icon = Client.check_text(line_text)
        if check_for_icon is True:
            path = os.path.dirname(os.path.abspath(__file__))
            item.setIcon(QIcon(path + "/codebase/client/pictures/python.jpg"))
        item.setText("%s: %s" % (self.username, line_text))
        self.client.send(line_text, current_tab)
        main_window_instance.line_edit.clear()

    def on_listView_clicked(self, main_window_instance, tab):
        username = main_window_instance.model.data(tab)
        count_tabs = main_window_instance.tab_widget.count()
        for count in range(count_tabs):
            tab = main_window_instance.tab_widget.widget(count)
            if tab.objectName() == username:
                return
        tab_1 = QtWidgets.QWidget()
        tab_1.setObjectName(username)
        main_window_instance.tab_widget.addTab(tab_1, username)
        list_widget = QtWidgets.QListWidget(tab_1)
        list_widget.setGeometry(QtCore.QRect(0, 10, 461, 192))

    def close_tab(self, main_window_instance, tab):
        if tab != 0:
            main_window_instance.tab_widget.removeTab(tab)

    def send_file(self, main_window_instance):
        index_first_tab = main_window_instance.tab_widget.currentIndex()
        if index_first_tab != 0:
            file_text = QFileDialog().getOpenFileName()
            current_tab = main_window_instance.tab_widget.currentWidget()
            current_widget = current_tab.children()[0]
            font = QFont()
            font.setStyle(QFont.StyleItalic)
            item = QListWidgetItem(current_widget)
            item.setFont(font)
            item.setText("%s: %s" % (self.username, "Sending File..."))
            self.client.send(file_text, current_tab, is_file=True)

    def add_tab_from_client(self, username):
        tab_1 = QtWidgets.QWidget(self.window.tab_widget)
        tab_1.setObjectName(username)
        list_widget = QtWidgets.QListWidget(tab_1)
        list_widget.setGeometry(QtCore.QRect(0, 10, 461, 192))
        self.window.tab_widget.addTab(tab_1, username)


class EventsTwo(metaclass=Singleton):
    def __init__(self, window):
        self.window = window
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((Client.HOST, Client.PORT))

    def push_button_event(self, main_window_instance):
        call_function_register = lambda: self.push_register_action(main_window_instance)
        call_function_login = lambda: self.push_login_action(main_window_instance)
        main_window_instance.pushButton_2.clicked.connect(call_function_register)
        main_window_instance.pushButton.clicked.connect(call_function_login)

    def receive(self):
        try:
            size = struct.unpack("i", self.sock.recv(struct.calcsize("i")))
            data = ""
            while len(data) < size[0]:
                msg = self.sock.recv(size[0] - len(data))
                if not msg:
                    return None
                data += msg.decode('utf-8')
        except OSError as e:
            return False
        return data

    def push_register_action(self, main_window_instance):
        data = {
            'first_name': main_window_instance.lineEdit_3.text(),
            'username': main_window_instance.lineEdit_4.text(),
            'password': main_window_instance.lineEdit_5.text(),
            'public_key': Client.get_or_generate_key()[1].decode('utf-8'),
        }
        Client.register_user(data, self.sock)
        response = self.receive()
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
        Client.login_user(data, self.sock)
        response = self.receive()
        response = json.loads(response)

        if response['is_correct'] is True:
            """
            Close this Window and open main
            """
            main_window_instance.label_7.setText("Correct User")
            main_window_instance.Form.close()
            main_window_instance.Form = QtWidgets.QMainWindow()
            ui = MainWindow(sock=self.sock)
            ui.setup_ui(main_window_instance.Form, data['username'])
            main_window_instance.Form.show()
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

        ev = EventsTwo(self)
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


class MainWindow(QtCore.QObject):
    def __init__(self, parent=None, sock=None):
        self.central_widget = None
        self.list_view = None
        self.tab_widget = None
        self.model = None
        self.sock = sock
        super(MainWindow, self).__init__(parent)

    def setup_ui(self, window, username):
        window.setObjectName("MainWindow")
        window.resize(900, 600)

        self.set_central_widget(window)
        self.set_tab_widget()
        self.set_tab()
        self.set_list_view()
        self.set_list_widget()
        self.set_push_button()
        self.set_browse_button()
        self.set_line_edit()

        window.setCentralWidget(self.central_widget)
        self.retranslate_ui(window)
        QtCore.QMetaObject.connectSlotsByName(window)

        ev = Events(self, username, self.sock)
        ev.push_button_event(self)

    def set_list_widget(self):
        self.listWidget = QtWidgets.QListWidget(self.tab)
        self.listWidget.setGeometry(QtCore.QRect(0, 10, 461, 192))
        self.listWidget.setObjectName("listWidget")

    def set_line_edit(self):
        self.line_edit = QtWidgets.QLineEdit(self.central_widget)
        self.line_edit.setGeometry(QtCore.QRect(290, 490, 371, 20))
        self.line_edit.setObjectName("lineEdit")

    def set_push_button(self):
        self.push_button = QtWidgets.QPushButton(self.central_widget)
        self.push_button.setGeometry(QtCore.QRect(680, 490, 91, 23))
        self.push_button.setObjectName("pushButton")

    def set_browse_button(self):
        self.browse_button = QtWidgets.QPushButton(self.central_widget)
        self.browse_button.setGeometry(QtCore.QRect(771, 490, 91, 23))
        self.browse_button.setObjectName("browseButton")

    def set_tab(self):
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("broadcast")
        self.tab_widget.addTab(self.tab, "")

    def set_central_widget(self, window):
        self.central_widget = QtWidgets.QWidget(window)
        self.central_widget.setObjectName("centralwidget")

    def set_list_view(self):
        self.list_view = QtWidgets.QListView(self.central_widget)
        self.list_view.setGeometry(QtCore.QRect(10, 10, 256, 451))
        self.list_view.setObjectName("listView")

        self.model = QStandardItemModel(self.list_view)

        self.list_view.setModel(self.model)
        self.list_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def set_tab_widget(self):
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab_widget.setGeometry(QtCore.QRect(280, 10, 471, 451))
        self.tab_widget.setObjectName("tabWidget")
        self.tab_widget.setCurrentIndex(0)
        self.tab_widget.setTabsClosable(True)

    def retranslate_ui(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle("SkyPy")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), "All")
        self.push_button.setText("Send Message")
        self.browse_button.setText("Send File")

"""
if __name__ == "__main__":
    import sys, os
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setup_ui(main_window)
    main_window.show()
    val = app.exec()
    os._exit(val)
"""

if __name__ == '__main__':
    import sys, os
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    val = app.exec()
    os._exit(val)