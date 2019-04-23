# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ledsButton = QtWidgets.QToolButton(self.centralwidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/images/led.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ledsButton.setIcon(icon1)
        self.ledsButton.setIconSize(QtCore.QSize(32, 32))
        self.ledsButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.ledsButton.setObjectName("ledsButton")
        self.horizontalLayout.addWidget(self.ledsButton)
        self.testSoundButton = QtWidgets.QToolButton(self.centralwidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/images/speaker.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.testSoundButton.setIcon(icon2)
        self.testSoundButton.setIconSize(QtCore.QSize(32, 32))
        self.testSoundButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.testSoundButton.setObjectName("testSoundButton")
        self.horizontalLayout.addWidget(self.testSoundButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAbout = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/images/info.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon3)
        self.actionAbout.setObjectName("actionAbout")
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Emergency - Control Monitor"))
        self.ledsButton.setText(_translate("MainWindow", "LEDs"))
        self.testSoundButton.setText(_translate("MainWindow", "Test Sound"))
        self.menuAbout.setTitle(_translate("MainWindow", "Help"))
        self.actionAbout.setText(_translate("MainWindow", "About"))

import monitor_rc
