# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Tutor2.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(1400, 676)
        mainWindow.setMinimumSize(QtCore.QSize(1400, 676))
        mainWindow.setMaximumSize(QtCore.QSize(1400, 676))
        self.centralwidget = QtWidgets.QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 260, 1371, 361))
        self.tableWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.tableWidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableWidget.setAutoFillBackground(False)
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableWidget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerItem)
        self.tableWidget.setGridStyle(QtCore.Qt.SolidLine)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(8, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(140)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(10)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(680, 90, 711, 61))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(680, 160, 711, 61))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(680, 10, 541, 71))
        self.pushButton_3.setObjectName("pushButton_3")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(20, 10, 321, 211))
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans")
        font.setPointSize(12)
        self.listWidget.setFont(font)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setObjectName("listWidget")
        self.listWidget_2 = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_2.setGeometry(QtCore.QRect(350, 10, 321, 211))
        font = QtGui.QFont()
        font.setFamily("DejaVu Sans")
        font.setPointSize(12)
        self.listWidget_2.setFont(font)
        self.listWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget_2.setObjectName("listWidget_2")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 230, 321, 17))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(350, 230, 321, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(680, 230, 111, 23))
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.checkBox_2 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_2.setGeometry(QtCore.QRect(780, 230, 131, 23))
        self.checkBox_2.setChecked(True)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_3.setGeometry(QtCore.QRect(910, 230, 101, 23))
        self.checkBox_3.setChecked(True)
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_4.setGeometry(QtCore.QRect(1030, 230, 111, 23))
        self.checkBox_4.setChecked(True)
        self.checkBox_4.setObjectName("checkBox_4")
        self.checkBox_5 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_5.setGeometry(QtCore.QRect(1140, 230, 131, 23))
        self.checkBox_5.setChecked(True)
        self.checkBox_5.setObjectName("checkBox_5")
        self.checkBox_6 = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_6.setGeometry(QtCore.QRect(1230, 230, 161, 23))
        self.checkBox_6.setChecked(True)
        self.checkBox_6.setObjectName("checkBox_6")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1230, 20, 161, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox.setGeometry(QtCore.QRect(1230, 40, 161, 31))
        self.doubleSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.doubleSpinBox.setDecimals(0)
        self.doubleSpinBox.setMinimum(10.0)
        self.doubleSpinBox.setMaximum(10000.0)
        self.doubleSpinBox.setSingleStep(100.0)
        self.doubleSpinBox.setProperty("value", 100.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 22))
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(mainWindow)
        self.statusbar.setObjectName("statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "IBOS Tutor"))
        self.tableWidget.setSortingEnabled(True)
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("mainWindow", "Студент"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("mainWindow", "Дата"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("mainWindow", "№ работы"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("mainWindow", "Результат"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("mainWindow", "Сложность"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("mainWindow", "Временной режим"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("mainWindow", "Начало"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("mainWindow", "Завершение"))
        item = self.tableWidget.horizontalHeaderItem(8)
        item.setText(_translate("mainWindow", "Лимит времени"))
        self.pushButton.setText(_translate("mainWindow", "Показать результаты выбранных компьютеров"))
        self.pushButton_2.setText(_translate("mainWindow", "Открыть экзамен для выбранных компьютеров"))
        self.pushButton_3.setText(_translate("mainWindow", "Получить список доступные компьютеры"))
        self.label.setText(_translate("mainWindow", "Компьютеры из файла конфигурации"))
        self.label_2.setText(_translate("mainWindow", "Доступные компьютеры"))
        self.checkBox.setText(_translate("mainWindow", "Простой у."))
        self.checkBox_2.setText(_translate("mainWindow", "Нормальный у."))
        self.checkBox_3.setText(_translate("mainWindow", "Сложный у."))
        self.checkBox_4.setText(_translate("mainWindow", "Без времени"))
        self.checkBox_5.setText(_translate("mainWindow", "Норматив"))
        self.checkBox_6.setText(_translate("mainWindow", "Уменьшенное время"))
        self.label_3.setText(_translate("mainWindow", "Таймаут проверки (мс)"))

