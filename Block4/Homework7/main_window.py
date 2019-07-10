# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    """
    Класс описывающий параметры GUI основного окна клиента
    """
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(757, 460)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(0, 0, 2, 2))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget1 = QtWidgets.QWidget(self.centralwidget)
        self.widget1.setGeometry(QtCore.QRect(230, 350, 521, 91))
        self.widget1.setObjectName("widget1")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.widget1)
        self.pushButton_4.setMaximumSize(QtCore.QSize(16777215, 23))
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_3.addWidget(self.pushButton_4)
        self.pushButton_3 = QtWidgets.QPushButton(self.widget1)
        self.pushButton_3.setMaximumSize(QtCore.QSize(16777215, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        self.pushButton_5 = QtWidgets.QPushButton(self.widget1)
        self.pushButton_5.setMaximumSize(QtCore.QSize(16777215, 23))
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_3.addWidget(self.pushButton_5)
        self.pushButton_6 = QtWidgets.QPushButton(self.widget1)
        self.pushButton_6.setMaximumSize(QtCore.QSize(16777215, 23))
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_3.addWidget(self.pushButton_6)
        self.toolButton = QtWidgets.QToolButton(self.widget1)
        self.toolButton.setMaximumSize(QtCore.QSize(16777215, 19))
        self.toolButton.setToolTip("")
        self.toolButton.setObjectName("toolButton")
        self.horizontalLayout_3.addWidget(self.toolButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.textEdit = QtWidgets.QTextEdit(self.widget1)
        self.textEdit.setMinimumSize(QtCore.QSize(250, 30))
        self.textEdit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.textEdit.setAutoFillBackground(False)
        self.textEdit.setObjectName("textEdit")
        self.horizontalLayout_4.addWidget(self.textEdit)
        self.pushButton = QtWidgets.QPushButton(self.widget1)
        self.pushButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum,
            QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QtCore.QSize(30, 30))
        self.pushButton.setMaximumSize(QtCore.QSize(75, 50))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.widget2 = QtWidgets.QWidget(self.centralwidget)
        self.widget2.setGeometry(QtCore.QRect(230, 10, 521, 341))
        self.widget2.setObjectName("widget2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tabWidget = QtWidgets.QTabWidget(self.widget2)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.textBrowser = QtWidgets.QTextBrowser(self.tab)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 491, 311))
        self.textBrowser.setObjectName("textBrowser")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.horizontalLayout_5.addWidget(self.tabWidget)
        self.verticalScrollBar = QtWidgets.QScrollBar(self.widget2)
        self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.horizontalLayout_5.addWidget(self.verticalScrollBar)
        self.widget3 = QtWidgets.QWidget(self.centralwidget)
        self.widget3.setGeometry(QtCore.QRect(10, 10, 211, 421))
        self.widget3.setObjectName("widget3")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget3)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(self.widget3)
        self.listWidget.setMinimumSize(QtCore.QSize(150, 200))
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Add_user = QtWidgets.QPushButton(self.widget3)
        self.Add_user.setMinimumSize(QtCore.QSize(75, 23))
        self.Add_user.setMaximumSize(QtCore.QSize(16777215, 23))
        self.Add_user.setObjectName("Add_user")
        self.horizontalLayout_2.addWidget(self.Add_user)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget3)
        self.pushButton_2.setMinimumSize(QtCore.QSize(75, 23))
        self.pushButton_2.setMaximumSize(QtCore.QSize(16777215, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setEnabled(True)
        self.statusbar.setAutoFillBackground(False)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate(
                "MainWindow",
                "Python Chat v.0.1"))
        self.pushButton_4.setText(_translate("MainWindow", "Who online"))
        self.pushButton_3.setText(_translate("MainWindow", "History"))
        self.pushButton_5.setText(_translate("MainWindow", "Private"))
        self.pushButton_6.setText(_translate("MainWindow", "Help"))
        self.toolButton.setText(_translate("MainWindow", "..."))
        self.textEdit.setHtml(
            _translate(
                "MainWindow",
                "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic; color:#9e9e9e;\">Type here...</span></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Send"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(
                self.tab), _translate(
                "MainWindow", "Main chat"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(
                self.tab_2), _translate(
                "MainWindow", "+"))
        self.Add_user.setText(_translate("MainWindow", "Add user"))
        self.pushButton_2.setText(_translate("MainWindow", "Del user"))
