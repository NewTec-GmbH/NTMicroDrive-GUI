# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingsWindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AppSettings(object):
    def setupUi(self, AppSettings):
        AppSettings.setObjectName("AppSettings")
        AppSettings.setWindowModality(QtCore.Qt.ApplicationModal)
        AppSettings.resize(350, 150)
        AppSettings.setMinimumSize(QtCore.QSize(350, 150))
        AppSettings.setMaximumSize(QtCore.QSize(350, 150))
        AppSettings.setSizeGripEnabled(False)
        AppSettings.setModal(True)
        self.verticalLayoutWidget = QtWidgets.QWidget(AppSettings)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 331, 137))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.comboBoxComPorts = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.comboBoxComPorts.setMinimumSize(QtCore.QSize(0, 50))
        self.comboBoxComPorts.setMaximumSize(QtCore.QSize(250, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboBoxComPorts.setFont(font)
        self.comboBoxComPorts.setObjectName("comboBoxComPorts")
        self.comboBoxComPorts.addItem("")
        self.comboBoxComPorts.addItem("")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBoxComPorts)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(25)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AppSettings)
        self.comboBoxComPorts.setCurrentIndex(1)
        self.buttonBox.accepted.connect(AppSettings.accept)
        self.buttonBox.rejected.connect(AppSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(AppSettings)

    def retranslateUi(self, AppSettings):
        _translate = QtCore.QCoreApplication.translate
        AppSettings.setWindowTitle(_translate("AppSettings", "Select COM Port"))
        self.label.setText(_translate("AppSettings", "Select COM Port LIN-Adapter is connected to:"))
        self.label_2.setText(_translate("AppSettings", "COM-Port"))
        self.comboBoxComPorts.setItemText(0, _translate("AppSettings", "LIN0"))
        self.comboBoxComPorts.setItemText(1, _translate("AppSettings", "LIN1"))

