import sys, os
from PySide.QtCore import *
from PySide.QtGui import *
from log import *


class ProjectInfo(object):
    def __init__(self):
        self.name = None
        self.has_ini = False
        self.width = 2
        self.height = 2
        self.description = ""
        self.rules_info = None

class RulesInfo(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.rules_template = None

class SizeWidget(QSpinBox):
    def __init__(self, parent=None):
        super(SizeWidget, self).__init__(parent)
        self.setMaximum(3)
        self.setValue(2)

class RulesWidget(QComboBox):
    def __init__(self, rules_list, parent=None):
        super(RulesWidget, self).__init__(parent)
        for item in rules_list:
            self.addItem(item.name)

class RulesDescriptionBox(QTextEdit):
    def __init__(self, parent=None):
        super(RulesDescriptionBox, self).__init__(parent)
        self.setReadOnly


class NewProjectDialog(QDialog):

    def __init__(self, model, rules_list, parent=None):
        super(NewProjectDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle('New Project Dialog')
        info_log("Initialising New Project Dialog")
        self.model = model
        self.rulesList = rules_list
        
        self.project_info = ProjectInfo()

        self.projectNameEdit = QLineEdit()
        self.widthWidget = SizeWidget()
        self.heightWidget = SizeWidget()
        self.rulesWidget = RulesWidget(self.rulesList)
        self.rulesDescriptionBox = RulesDescriptionBox()

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Project Name:'), 0, 0)
        grid_layout.addWidget(self.projectNameEdit, 0, 1)

        grid_layout.addWidget(QLabel('Sectors wide:'), 1, 0)
        grid_layout.addWidget(self.widthWidget, 1, 1)

        grid_layout.addWidget(QLabel('Sectors high:'), 2, 0)
        grid_layout.addWidget(self.heightWidget, 2, 1)

        grid_layout.addWidget(QLabel('Rules:'), 3, 0)
        grid_layout.addWidget(self.rulesWidget, 3, 1)

        grid_layout.addWidget(QLabel('Rules Description:'), 4, 0, Qt.AlignTop)
        grid_layout.addWidget(self.rulesDescriptionBox, 4, 1)

        self.widthWidget.valueChanged.connect(self.updateWidth)
        self.heightWidget.valueChanged.connect(self.updateHeight)
        self.rulesWidget.currentIndexChanged[int].connect(self.updateRulesSelected)

        self.okButton = QPushButton('OK')
        self.cancelButton = QPushButton('Cancel')
        
        hblayout = QHBoxLayout()
        hblayout.addWidget(self.okButton)
        hblayout.addWidget(self.cancelButton)

        vblayout = QVBoxLayout()
        vblayout.addLayout(grid_layout)
        vblayout.addLayout(hblayout)

        self.setLayout(vblayout)

        self.okButton.clicked.connect(self.ok)
        self.cancelButton.clicked.connect(self.cancel)

        for index, entry in enumerate(self.rulesList):
            if entry.name.rstrip().lower() == 'default':
                self.rulesWidget.setCurrentIndex(index)


    def updateWidth(self, value):
        self.project_info.width = value

    def updateHeight(self, value):
        self.project_info.height = value

    def updateRulesSelected(self, index):
        self.project_info.rules_info = self.rulesList[index]
        self.rulesDescriptionBox.setText(self.project_info.rules_info.description)


    def getProjectInfo(self):
        return self.project_info

    def ok(self):
        name = self.projectNameEdit.text()
        if name != "" and name != None:
            self.project_info.name = name
        else:
            self.project_info = None
        self.accept()

    def cancel(self):
        self.project = None
        self.close()



