from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QListWidgetItem
from codebase.client.client import Client
from codebase.utils.singleton import Singleton


class Events(metaclass=Singleton):
    def __init__(self, window):
        self.client = Client(username="koki")
        Client.WINDOW = window
        self.client.start()

    def push_button_event(self, main_window_instance):
        call_function = lambda: self.push_button_action(main_window_instance)
        main_window_instance.push_button.clicked.connect(call_function)

    def push_button_action(self, main_window_instance):
        line_text = main_window_instance.line_edit.text()
        item = QListWidgetItem(main_window_instance.listWidget)
        item.setText(line_text)
        self.client.send(line_text, None)
        main_window_instance.line_edit.clear()


class MainWindow(object):
    def __init__(self):
        self.central_widget = None
        self.list_view = None
        self.tab_widget = None
        self.model = None

    def setup_ui(self, window):
        window.setObjectName("MainWindow")
        window.resize(800, 600)
        
        self.set_central_widget(window)
        self.set_tab_widget()
        self.set_tab()
        self.set_list_view()
        self.set_list_widget()
        self.set_push_button()
        self.set_line_edit()
        
        window.setCentralWidget(self.central_widget)
        self.retranslate_ui(window)
        QtCore.QMetaObject.connectSlotsByName(window)

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
        ev = Events(self)
        ev.push_button_event(self)

    def set_tab(self):
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
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

    def set_tab_widget(self):
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab_widget.setGeometry(QtCore.QRect(280, 10, 471, 451))
        self.tab_widget.setObjectName("tabWidget")
        self.tab_widget.setCurrentIndex(0)

    def retranslate_ui(self, window):
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle("SkyPy")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab), "Tab 1")
        self.push_button.setText("Send Message")

if __name__ == "__main__":
    import sys, os
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setup_ui(main_window)
    main_window.show()
    val = app.exec()
    os._exit(val)
