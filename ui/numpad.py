# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'numpad.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Numpad(object):
    def setupUi(self, Numpad):
        Numpad.setObjectName("Numpad")
        Numpad.resize(348, 505)
        self.buttonBox = QtWidgets.QDialogButtonBox(Numpad)
        self.buttonBox.setGeometry(QtCore.QRect(0, 460, 341, 41))
        font = QtGui.QFont()
        font.setPointSize(25)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayoutWidget = QtWidgets.QWidget(Numpad)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 342, 457))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.numberToSet = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.numberToSet.setObjectName("numberToSet")
        self.horizontalLayout.addWidget(self.numberToSet)
        self.buttonBackspace = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.buttonBackspace.setMinimumSize(QtCore.QSize(80, 60))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.buttonBackspace.setFont(font)
        self.buttonBackspace.setObjectName("buttonBackspace")
        self.horizontalLayout.addWidget(self.buttonBackspace)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.button0 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button0.setMinimumSize(QtCore.QSize(80, 80))
        self.button0.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button0.setFont(font)
        self.button0.setObjectName("button0")
        self.gridLayout.addWidget(self.button0, 3, 1, 1, 1)
        self.button1 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button1.setMinimumSize(QtCore.QSize(80, 80))
        self.button1.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button1.setFont(font)
        self.button1.setObjectName("button1")
        self.gridLayout.addWidget(self.button1, 0, 0, 1, 1)
        self.button2 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button2.setMinimumSize(QtCore.QSize(80, 80))
        self.button2.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button2.setFont(font)
        self.button2.setObjectName("button2")
        self.gridLayout.addWidget(self.button2, 0, 1, 1, 1)
        self.button3 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button3.setMinimumSize(QtCore.QSize(80, 80))
        self.button3.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button3.setFont(font)
        self.button3.setObjectName("button3")
        self.gridLayout.addWidget(self.button3, 0, 2, 1, 1)
        self.button5 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button5.setMinimumSize(QtCore.QSize(80, 80))
        self.button5.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button5.setFont(font)
        self.button5.setObjectName("button5")
        self.gridLayout.addWidget(self.button5, 1, 1, 1, 1)
        self.button6 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button6.setMinimumSize(QtCore.QSize(80, 80))
        self.button6.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button6.setFont(font)
        self.button6.setObjectName("button6")
        self.gridLayout.addWidget(self.button6, 1, 2, 1, 1)
        self.button9 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button9.setMinimumSize(QtCore.QSize(80, 80))
        self.button9.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button9.setFont(font)
        self.button9.setObjectName("button9")
        self.gridLayout.addWidget(self.button9, 2, 2, 1, 1)
        self.button7 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button7.setMinimumSize(QtCore.QSize(80, 80))
        self.button7.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button7.setFont(font)
        self.button7.setObjectName("button7")
        self.gridLayout.addWidget(self.button7, 2, 0, 1, 1)
        self.button8 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button8.setMinimumSize(QtCore.QSize(80, 80))
        self.button8.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button8.setFont(font)
        self.button8.setObjectName("button8")
        self.gridLayout.addWidget(self.button8, 2, 1, 1, 1)
        self.button4 = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.button4.setMinimumSize(QtCore.QSize(80, 80))
        self.button4.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.button4.setFont(font)
        self.button4.setObjectName("button4")
        self.gridLayout.addWidget(self.button4, 1, 0, 1, 1)
        self.buttonSub = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.buttonSub.setMinimumSize(QtCore.QSize(80, 80))
        self.buttonSub.setMaximumSize(QtCore.QSize(80, 80))
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.buttonSub.setFont(font)
        self.buttonSub.setObjectName("buttonSub")
        self.gridLayout.addWidget(self.buttonSub, 3, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Numpad)
        self.buttonBox.accepted.connect(Numpad.accept)
        self.buttonBox.rejected.connect(Numpad.reject)
        QtCore.QMetaObject.connectSlotsByName(Numpad)

    def retranslateUi(self, Numpad):
        _translate = QtCore.QCoreApplication.translate
        Numpad.setWindowTitle(_translate("Numpad", "Dialog"))
        self.buttonBackspace.setText(_translate("Numpad", "<-"))
        self.button0.setText(_translate("Numpad", "0"))
        self.button1.setText(_translate("Numpad", "1"))
        self.button2.setText(_translate("Numpad", "2"))
        self.button3.setText(_translate("Numpad", "3"))
        self.button5.setText(_translate("Numpad", "5"))
        self.button6.setText(_translate("Numpad", "6"))
        self.button9.setText(_translate("Numpad", "9"))
        self.button7.setText(_translate("Numpad", "7"))
        self.button8.setText(_translate("Numpad", "8"))
        self.button4.setText(_translate("Numpad", "4"))
        self.buttonSub.setText(_translate("Numpad", "-"))

