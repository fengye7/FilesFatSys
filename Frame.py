# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Frame.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FileSysFrame(object):
    def setupUi(self, FileSysFrame):
        FileSysFrame.setObjectName("FileSysFrame")
        FileSysFrame.resize(1098, 790)
        self.centralwidget = QtWidgets.QWidget(FileSysFrame)
        self.centralwidget.setObjectName("centralwidget")
        self.SearchBar = QtWidgets.QLineEdit(self.centralwidget)
        self.SearchBar.setGeometry(QtCore.QRect(730, 10, 301, 31))
        self.SearchBar.setText("")
        self.SearchBar.setClearButtonEnabled(True)
        self.SearchBar.setObjectName("SearchBar")
        self.SearchLabel = QtWidgets.QLabel(self.centralwidget)
        self.SearchLabel.setGeometry(QtCore.QRect(1041, 0, 41, 41))
        self.SearchLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.SearchLabel.setObjectName("SearchLabel")
        self.AddressBar = QtWidgets.QLineEdit(self.centralwidget)
        self.AddressBar.setGeometry(QtCore.QRect(180, 10, 441, 31))
        self.AddressBar.setObjectName("AddressBar")
        self.RecoverButton = QtWidgets.QPushButton(self.centralwidget)
        self.RecoverButton.setGeometry(QtCore.QRect(632, 10, 91, 31))
        self.RecoverButton.setObjectName("RecoverButton")
        self.BackButton = QtWidgets.QPushButton(self.centralwidget)
        self.BackButton.setGeometry(QtCore.QRect(10, 10, 41, 28))
        self.BackButton.setObjectName("BackButton")
        self.ForwardButton = QtWidgets.QPushButton(self.centralwidget)
        self.ForwardButton.setGeometry(QtCore.QRect(60, 10, 41, 28))
        self.ForwardButton.setObjectName("ForwardButton")
        self.BackUp = QtWidgets.QPushButton(self.centralwidget)
        self.BackUp.setGeometry(QtCore.QRect(110, 10, 61, 28))
        self.BackUp.setObjectName("BackUp")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 40, 1081, 671))
        self.groupBox.setObjectName("groupBox")
        self.treeWidget = QtWidgets.QTreeWidget(self.groupBox)
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 261, 671))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.tableWidget = QtWidgets.QTableWidget(self.groupBox)
        self.tableWidget.setGeometry(QtCore.QRect(260, 0, 821, 671))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 700, 101, 41))
        self.label.setObjectName("label")
        self.item_num_label = QtWidgets.QLabel(self.centralwidget)
        self.item_num_label.setGeometry(QtCore.QRect(90, 700, 101, 41))
        self.item_num_label.setObjectName("item_num_label")
        self.selected_item_num = QtWidgets.QLabel(self.centralwidget)
        self.selected_item_num.setGeometry(QtCore.QRect(230, 700, 111, 41))
        self.selected_item_num.setObjectName("selected_item_num")
        self.selected_item_size = QtWidgets.QLabel(self.centralwidget)
        self.selected_item_size.setGeometry(QtCore.QRect(340, 700, 221, 41))
        self.selected_item_size.setObjectName("selected_item_size")
        FileSysFrame.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(FileSysFrame)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1098, 26))
        self.menubar.setObjectName("menubar")
        self.menu_write = QtWidgets.QMenu(self.menubar)
        self.menu_write.setObjectName("menu_write")
        self.menu_exit = QtWidgets.QMenu(self.menubar)
        self.menu_exit.setObjectName("menu_exit")
        self.menu_format = QtWidgets.QMenu(self.menubar)
        self.menu_format.setObjectName("menu_format")
        FileSysFrame.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(FileSysFrame)
        self.statusbar.setObjectName("statusbar")
        FileSysFrame.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menu_write.menuAction())
        self.menubar.addAction(self.menu_exit.menuAction())
        self.menubar.addAction(self.menu_format.menuAction())

        self.retranslateUi(FileSysFrame)
        QtCore.QMetaObject.connectSlotsByName(FileSysFrame)

    def retranslateUi(self, FileSysFrame):
        _translate = QtCore.QCoreApplication.translate
        FileSysFrame.setWindowTitle(_translate("FileSysFrame", "MainWindow"))
        self.SearchBar.setToolTip(_translate("FileSysFrame", "<html><head/><body><p>Search:</p></body></html>"))
        self.SearchBar.setPlaceholderText(_translate("FileSysFrame", "Search:"))
        self.SearchLabel.setText(_translate("FileSysFrame", "TextLabel"))
        self.RecoverButton.setText(_translate("FileSysFrame", "recover"))
        self.BackButton.setText(_translate("FileSysFrame", "<"))
        self.ForwardButton.setText(_translate("FileSysFrame", ">"))
        self.BackUp.setText(_translate("FileSysFrame", "上一级"))
        self.groupBox.setTitle(_translate("FileSysFrame", "GroupBox"))
        self.label.setText(_translate("FileSysFrame", "项目数量："))
        self.item_num_label.setText(_translate("FileSysFrame", "TextLabel"))
        self.selected_item_num.setText(_translate("FileSysFrame", "选中0个项目："))
        self.selected_item_size.setText(_translate("FileSysFrame", "TextLabel"))
        self.menu_write.setTitle(_translate("FileSysFrame", "写入"))
        self.menu_exit.setTitle(_translate("FileSysFrame", "退出程序"))
        self.menu_format.setTitle(_translate("FileSysFrame", "格式化"))
