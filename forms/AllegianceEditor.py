#import sip
# Copyright 2013 Simon Dominic Hibbs
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

import sys
#import math
from PySide.QtCore import *
from PySide.QtGui import *
from model import Models
from model import Foundation
#from reports import WorldReport
from resources import starmap_rc
from log import *

CHECKBOX = 0
AL_ABRV = 1
AL_NAME = 2
AL_COLOR = 3

class AbrevLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(AbrevLineEdit, self).__init__(parent)
        self.setMaxLength(2)
        self.setMaximumWidth(40)

class FullLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(FullLineEdit, self).__init__(parent)
        self.setMaxLength(30)
        self.setMinimumWidth(160)


class MergeTargetPicker(QDialog):
    def __init__(self, option_list, parent=None):
        super(MergeTargetPicker, self).__init__(parent)
        #Don't delete on close

        self.optionListWidget = QListWidget()
        for option in option_list:
            self.optionListWidget.addItem(option)

        self.targetNameWidget = FullLineEdit()
        self.result = None

        leftColumnLayout = QVBoxLayout()
        leftColumnLayout.addWidget(self.optionListWidget)
        my_text = 'All worlds with these allegiances will be set ' + \
                  'to have the following allegiance:'
        leftColumnLayout.addWidget(QLabel(my_text))
        leftColumnLayout.addWidget(self.targetNameWidget)

        self.okButton = QPushButton('OK')
        self.okButton.setDisabled(True)
        self.cancelButton = QPushButton('Cancel')

        rightColumnLayout = QVBoxLayout()
        rightColumnLayout.addStretch(10)
        rightColumnLayout.addWidget(self.cancelButton)
        rightColumnLayout.addWidget(self.okButton)

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addLayout(leftColumnLayout)
        horizontalLayout.addLayout(rightColumnLayout)

        self.setLayout(horizontalLayout)

        self.optionListWidget.currentRowChanged[int].connect(self.optionSelected)
        #self.connect(self.okButton, SIGNAL("clicked()"),
        #             self.okButtonClicked)
        self.okButton.clicked.connect(self.okButtonClicked)
        #self.connect(self.cancelButton, SIGNAL("clicked()"),
        #             self.cancelButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        
    def optionSelected(self, row):
        option_text = str(self.optionListWidget.item(row).text())
        self.targetNameWidget.setText(option_text)
        self.result = option_text
        self.okButton.setDisabled(False)

    def okButtonClicked(self):
        self.close()

    def cancelButtonClicked(self):
        self.result = None
        self.close()


class AllegianceWidgetSet(object):
    def __init__(self, code, name, color):
        self.checkBox = QCheckBox()
        
        self.code = AbrevLineEdit()
        self.code.setMaxLength(2)
        self.code.setText(code)
        
        self.name = FullLineEdit()
        self.name.setText(name)
        
        color_pixmap = QPixmap(64, 32)
        color_pixmap.fill(QColor(color))
        self.color = QLabel()
        self.color.setPixmap(color_pixmap)

    def setAllegianceColor(self, color):
        color_pixmap = QPixmap(64, 32)
        color_pixmap.fill(QColor(color))
        self.color.setPixmap(color_pixmap)


class AllegianceTableWidget(QTableWidget):
    def __init__(self, x, y, parent = None):
        super(AllegianceTableWidget, self).__init__(x, y, parent)

##    def viewOptions(self):
##        option = QTableWidget.viewOptions(self)
##        option.decorationAlignment = Qt.AlignHCenter
##        option.decorationPosition = QStyleOptionViewItem.Top
##        return option

    def sizeHint(self):
        width = 0
        for i in range(self.columnCount()):
            width += self.columnWidth(i)

        width += self.verticalHeader().sizeHint().width()

        width += self.verticalScrollBar().sizeHint().width()
        #width += self.frameWidth()*2

        height = QTableWidget.sizeHint(self).height()

        return QSize(width,height)


class AllegianceEditor(QDialog):
    def __init__(self, world_model, scene, parent=None):
        super(AllegianceEditor, self).__init__(parent)
        debug_log('Started Allegiance Editor init.')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Allegiance Editor")
        self.model = world_model
        self.scene = scene

        debug_log('Setting up Allegiance Editor controlls')
        self.mergeButton = QPushButton('Merge')
        self.colorButton = QPushButton('Change Colour')
        self.addButton = QPushButton('Add New')
        self.setAllegianceButton = QPushButton('Apply to selection')
        self.okButton = QPushButton('OK')
        
        self.buttonRow = QVBoxLayout()
        self.buttonRow.addWidget(self.mergeButton)
        self.buttonRow.addWidget(self.colorButton)
        self.buttonRow.addWidget(self.addButton)
        self.buttonRow.addWidget(self.setAllegianceButton)
        self.buttonRow.addStretch(10)
        self.buttonRow.addWidget(self.okButton)
        self.buttonRow.addStretch()

        self.allegianceTable = AllegianceTableWidget(0, 4, self)
        self.allegianceControlls = []

        self.leftVLayout = QVBoxLayout()
        self.leftVLayout.addWidget(self.allegianceTable)
        self.leftVLayout.addStretch(10)
        
        self.hLayout = QHBoxLayout()
        self.hLayout.addLayout(self.leftVLayout)
        self.hLayout.addLayout(self.buttonRow)
        self.setLayout(self.hLayout)

        debug_log('About to populate Allegiances')
        self.populateAllegiances()

        self.allegianceTable.horizontalHeader().setVisible(False)
        self.allegianceTable.verticalHeader().setVisible(False)
        self.allegianceTable.horizontalHeader().setStretchLastSection(True)
        self.allegianceTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.allegianceTable.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.allegianceTable.setShowGrid(False)
        self.allegianceTable.setSizePolicy(QSizePolicy.MinimumExpanding,
                                           QSizePolicy.MinimumExpanding)

        self.mergeButton.clicked.connect(self.mergeButtonClicked)
        self.colorButton.clicked.connect(self.colorButtonClicked)
        self.addButton.clicked.connect(self.addButtonClicked)
        self.setAllegianceButton.clicked.connect(self.setAllegiance)
        self.okButton.clicked.connect(self.okButtonClicked)

        #self.setMinimumWidth(400)
        debug_log('About to check Allegiance check box states')
        self.checkStateChanged()
        debug_log('Allegiance check box states checked')


    def setAllegiance(self):
        for index in range(len(self.allegianceControlls)):
            if self.allegianceControlls[index].checkBox.checkState():
                code = str(self.allegianceControlls[index].code.text())
                self.scene.setAllegiance(code)

    def checkStateChanged(self):
        count = 0
        for controll in self.allegianceControlls:
            if controll.checkBox.checkState():
                count += 1
        if count == 0:
            self.mergeButton.setDisabled(True)
            self.colorButton.setDisabled(True)
            self.setAllegianceButton.setDisabled(True)
        elif count == 1:
            self.mergeButton.setDisabled(True)
            self.setAllegianceButton.setDisabled(False)
            self.colorButton.setDisabled(False)
        elif count > 1:
            self.mergeButton.setDisabled(False)
            self.colorButton.setDisabled(True)
            self.setAllegianceButton.setDisabled(True)

    def abbreviationChanged(self):
        for index in range(self.allegianceTable.rowCount()):
            if Foundation.allegiance_codes[index] != str(self.allegianceControlls[index].code.text()):
                Foundation.allegiance_codes[index] = str(self.allegianceControlls[index].code.text())
                self.model.allegianceDataChanged()

    def nameChanged(self):
        for index in range(self.allegianceTable.rowCount()):
            if Foundation.allegiance_names[index] != str(self.allegianceControlls[index].name.text()):
                Foundation.allegiance_names[index] = str(self.allegianceControlls[index].name.text())
                self.model.allegianceDataChanged()

    def colorButtonClicked(self):
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid():
            for index in range(len(self.allegianceControlls)):
                if self.allegianceControlls[index].checkBox.checkState():
                    Foundation.allegiance_colors[index] = str(color.name())
                    self.allegianceControlls[index].setAllegianceColor(color)
                    self.model.allegianceDataChanged()
        

    def addButtonClicked(self):
        color = QColor('#000000')
        a = AllegianceWidgetSet('', '', color)
        
        end = len(self.allegianceControlls)
        self.allegianceTable.insertRow(end)
        
        self.allegianceTable.setCellWidget(end, CHECKBOX, a.checkBox)
        self.allegianceTable.setCellWidget(end, AL_ABRV, a.code)
        self.allegianceTable.setCellWidget(end, AL_NAME, a.name)
        self.allegianceTable.setCellWidget(end, AL_COLOR, a.color)
        
        self.allegianceControlls.append(a)
        a.checkBox.stateChanged[int].connect(self.checkStateChanged)
        a.code.editingFinished.connect(self.abbreviationChanged)
        a.name.editingFinished.connect(self.nameChanged)

        Foundation.allegiance_codes.append('')
        Foundation.allegiance_names.append('')
        Foundation.allegiance_colors.append('#000000')

        self.updateGeometry()


    def mergeButtonClicked(self):
        merge_list = []
        for row in range(self.allegianceTable.rowCount()):
            if self.allegianceControlls[row].checkBox.checkState():
                merge_list.append(str(self.allegianceControlls[row].name.text()))
##            if self.allegianceTable.cellWidget(row, CHECKBOX).checkState():
##                merge_list.append(str(self.allegianceTable.cellWidget(row, AL_NAME).text()))
        if len(merge_list) > 1:
            picker = MergeTargetPicker(merge_list)
            picker.exec_()
            target = picker.result
            del picker
            if target != None and target in merge_list:
                for allegiance in merge_list:
                    if allegiance != target:
                        self.model.mergeAllegiance(allegiance, target)
                        
                        delist = []
                        for row in range(self.allegianceTable.rowCount()):
                            if allegiance == str(self.allegianceTable.cellWidget(
                                    row, AL_NAME).text()):
                                delist.append(row)

                        delist.reverse()
                        for row in delist:
                            self.allegianceTable.removeRow(row)
                            del self.allegianceControlls[row]
                #self.close()
                #self.populateAllegiances()

    def okButtonClicked(self):
        self.close()


    def populateAllegiances(self):
        for index in range(len(Foundation.allegiance_codes)):
            a = AllegianceWidgetSet(Foundation.allegiance_codes[index],
                                    Foundation.allegiance_names[index],
                                    Foundation.allegiance_colors[index])

            self.allegianceTable.insertRow(index)
            wdg = QWidget()
            layout = QHBoxLayout()
            layout.addWidget(a.checkBox)
            layout.setAlignment(Qt.AlignCenter)
            wdg.setLayout(layout)
            self.allegianceTable.setCellWidget(index, CHECKBOX, wdg)
            self.allegianceTable.setCellWidget(index, AL_ABRV, a.code)
            self.allegianceTable.setCellWidget(index, AL_NAME, a.name)
            self.allegianceTable.setCellWidget(index, AL_COLOR, a.color)

            self.allegianceControlls.append(a)
            a.checkBox.stateChanged[int].connect(self.checkStateChanged)
            a.code.editingFinished.connect(self.abbreviationChanged)
            a.name.editingFinished.connect(self.nameChanged)
            
        self.allegianceTable.resizeColumnsToContents()
        self.updateGeometry()
