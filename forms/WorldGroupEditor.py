# Copyright 2013 Simon Dominic Hibbs
from PySide.QtCore import *
from PySide.QtGui import *
from model import Models
from log import *

# Attribute change types
INVALID = -1
SET = 0
ADJUST = 1
MAX = 2
MIN = 3

class ValueSelector(QComboBox):
    def __init__(self, values, parent=None):
        super(ValueSelector, self).__init__(parent)
        self.setModel(QStringListModel(values))
        self.details_button = None

    def setDetailsButton(self, button):
        self.details_button = button
        # Move focus to force the widget mapper to update the model
        self.activated[int].connect(self.giveFocus)

    def giveFocus(self, value):
        # Force a model update by moving focus, and also display
        # the description for the new attribute value (click() doesn't give focus by itself).
        self.details_button.setFocus()
        self.details_button.click()


class ValueAdjuster(QSpinBox):
    def __init__(self, parent=None):
        super(ValueAdjuster, self).__init__(parent)
        self.setMinimum(-99)

        self.valueChanged[int].connect(self.updatePrefix)

    def updatePrefix(self, value):
        if value >= 0:
            self.setPrefix('+')
        else:
            self.setPrefix('-')

class AttributeChange(object):
    def __init__(self, index=-1, change_type=INVALID, change_value=-1, value_text=-1):
        self.definition_index = index
        self.type = change_type
        self.value = change_value
        self.value_text = value_text



class AttributeEditDialog(QDialog):
    def __init__(self, definition_index, definition, parent=None):
        super(AttributeEditDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Attribute Adjustment Dialog')
        self.definition_index = definition_index
        self.definition = definition
        self.parent = parent

        self.grid = QGridLayout()

        self.grid.addWidget(QLabel('Attribute Name'), 0, 0)
        self.grid.addWidget(QLabel(self.definition.name), 0, 1)

        self.setRadioButton = QRadioButton('Set value:')
        self.setSelector = ValueSelector(self.definition.codes)
        self.grid.addWidget(self.setRadioButton, 1, 0)
        self.grid.addWidget(self.setSelector, 1, 1)

        self.adjustRadioButton = QRadioButton('Adjust value:')
        self.valueAdjuster = ValueAdjuster()
        self.grid.addWidget(self.adjustRadioButton, 2, 0)
        self.grid.addWidget(self.valueAdjuster, 2, 1)

        self.maxRadioButton = QRadioButton('Set Maximum:')
        self.maxSelector = ValueSelector(self.definition.codes)
        self.grid.addWidget(self.maxRadioButton, 3, 0)
        self.grid.addWidget(self.maxSelector, 3, 1)

        self.minRadioButton = QRadioButton('Set Minimum:')
        self.minSelector = ValueSelector(self.definition.codes)
        self.grid.addWidget(self.minRadioButton, 4, 0)
        self.grid.addWidget(self.minSelector, 4, 1)

        self.noChangeButton = QRadioButton('No Change:')
        self.grid.addWidget(self.minRadioButton, 5, 0)

        self.buttonGroup = QButtonGroup()
        self.buttonGroup.addButton(self.setRadioButton)
        self.buttonGroup.addButton(self.adjustRadioButton)
        self.buttonGroup.addButton(self.maxRadioButton)
        self.buttonGroup.addButton(self.minRadioButton)
        self.buttonGroup.addButton(self.noChangeButton)

        self.setRadioButton.toggled.connect(self.selectSet)
        self.adjustRadioButton.toggled.connect(self.selectAdjust)
        self.maxRadioButton.toggled.connect(self.selectMax)
        self.minRadioButton.toggled.connect(self.selectMin)
        self.noChangeButton.toggled.connect(self.noChange)

        self.okButton = QPushButton('OK')
        self.cancelButton = QPushButton('Cancel')
        self.hLayout = QHBoxLayout()
        self.hLayout.addLayout(self.grid)
        self.hLayout.addWidget(self.okButton)
        self.hLayout.addWidget(self.cancelButton)
        self.setLayout(self.hLayout)

        self.okButton.clicked.connect(self.okClicked)
        self.cancelButton.clicked.connect(self.cancelClicked)


    def selectSet(self):
        if self.setRadioButton.isChecked():
            self.setSelector.setEnabled(True)
        else:
            self.setSelector.setEnabled(False)

    def selectAdjust(self):
        if self.adjustRadioButton.isChecked():
            self.valueAdjuster.setEnabled(True)
        else:
            self.valueAdjuster.setEnabled(False)

    def selectMax(self):
        if self.maxRadioButton.isChecked():
            self.maxSelector.setEnabled(True)
        else:
            self.maxSelector.setEnabled(False)

    def selectMin(self):
        if self.minRadioButton.isChecked():
            self.minSelector.setEnabled(True)
        else:
            self.minSelector.setEnabled(False)

    def noChange(self):
        if self.minRadioButton.isChecked():
            self.noChangeButton.setEnabled(True)
        else:
            self.noChangeButton.setEnabled(False)
            

    def okClicked(self):
        if self.setRadioButton.isChecked():
            change = AttributeChange(index=self.definition_index,
                                     change_type=SET,
                                     change_value=self.setSelector.currentIndex(),
                                     value_text=self.setSelector.currentText())
        elif self.adjustRadioButton.isChecked():
            change = AttributeChange(index=self.definition_index,
                                     change_type=ADJUST,
                                     change_value=self.valueAdjuster.value(),
                                     value_text=self.valueAdjuster.prefix() + str(self.valueAdjuster.value()))
        elif self.maxRadioButton.isChecked():
            change = AttributeChange(index=self.definition_index,
                                     change_type=MAX,
                                     change_value=self.maxSelector.currentIndex(),
                                     value_text=self.maxSelector.currentText())
        elif self.minRadioButton.isChecked():
            change = AttributeChange(index=self.definition_index,
                                     change_type=MIN,
                                     change_value=self.minSelector.currentIndex(),
                                     value_text=self.minSelector.currentText())
        else:
            change = 0
        self.parent.new_change = change
        QDialog.done(self, 1)


    def cancelClicked(self):
        self.parent.new_change = 0
        QDialog.done(self, 0)




class AttributeGridFrame(QFrame):
    def __init__(self, world_model, title_text, parent=None, moveable=False):
        super(AttributeGridFrame, self).__init__(parent)
        self.world_model = world_model
        self.new_change = 0

        self.editButtonGroup = QButtonGroup()
        self.changeDetailsList = []
        self.changes = [None] * len(self.world_model.attributeDefinitions)

        self.attributeGrid = QGridLayout()
        # Title row
        title_label = QLabel(title_text)
        title_label.setWordWrap(True)
        self.attributeGrid.addWidget(title_label, 0, 0, 1, 3)
        # Header row
        self.attributeGrid.addWidget(QLabel('Attributes'), 1, 0)
        self.attributeGrid.addWidget(QLabel(''), 1, 1)
        self.attributeGrid.addWidget(QLabel('Selected Changes'), 1, 2)
        
        for index, definition in enumerate(self.world_model.attributeDefinitions):
            row = index + 2   # Allow for header row
            self.attributeGrid.addWidget(QLabel(definition.name), row, 0)
            
            self.editButtonGroup.addButton(QPushButton('Edit'), index)
            self.attributeGrid.addWidget(self.editButtonGroup.button(index), row, 1)

            self.changeDetailsList.append(QLabel('No Change'))
            self.attributeGrid.addWidget(self.changeDetailsList[index], row, 2)

        self.setLayout(self.attributeGrid)

        self.editButtonGroup.buttonClicked[int].connect(self.openAttributeEditor)
            
    def openAttributeEditor(self, index):
        result = AttributeEditDialog(index,
                                     self.world_model.attributeDefinitions[index],
                                     parent=self).exec_()
        attribute_name = self.world_model.attributeDefinitions[index].name
        text = 'No Changes'
        if result != 0:
            if self.new_change == 0:
                pass
            elif self.new_change.type == SET:
                text = 'Set ' + attribute_name + ' to ' + str(self.new_change.value_text)
            elif self.new_change.type == ADJUST:
                text = 'Adjust ' + attribute_name + ' by ' + str(self.new_change.value_text)
            elif self.new_change.type == MAX:
                text = 'Cap the maximum value of ' + attribute_name + ' to ' + str(self.new_change.value_text)
            elif self.new_change.type == MIN:
                text = 'Raise the minimum value of ' + attribute_name + ' to ' + str(self.new_change.value_text)
            else:
                text = 'No Changes'
                self.new_change = 0

        if self.new_change != 0:
            self.changes[index] = self.new_change
            self.changeDetailsList[index].setText(text)
        else:
            self.changes[index] = None
            self.changeDetailsList[index].setText(text)




class WorldGroupEditDialog(QDialog):
    def __init__(self, pmi_list, numcells, title_text, parent=None):
        super(WorldGroupEditDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('World Group Editor')
        self.pmi_list = pmi_list
        self.world_model = pmi_list[0].model()

        self.attributeEditFrame = AttributeGridFrame(self.world_model, title_text)
        self.applyButton = QPushButton('Apply All Changes')
        self.cancelButton = QPushButton('Cancel')

        masterLayout = QVBoxLayout()
        masterLayout.addWidget(self.attributeEditFrame)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)

        masterLayout.addLayout(self.buttonLayout)
        self.setLayout(masterLayout)

        self.applyButton.clicked.connect(self.applyClicked)
        self.cancelButton.clicked.connect(self.cancelClicked)

        
    def applyClicked(self):
        for attribute_index, change in enumerate(self.attributeEditFrame.changes):
            if change is not None and change != 0:
                for pmi in self.pmi_list:
                    world = self.world_model.getWorld(pmi)
                    data_index = self.world_model.createIndex(pmi.row(), (Models.ATTRIBUTE_BASE + change.definition_index))
                    if change.type == SET:
                        # Set the attribute to the new vattribute code index
                        self.world_model.setData(data_index, change.value)
                    elif change.type == ADJUST:
                        # Retrieve the current code, determine it's index value, then compute and apply the new index value
                        old_code = self.world_model.data(data_index)
                        code_list = self.world_model.attributeDefinitions[attribute_index].codes
                        old_value = code_list.index(old_code)
                        new_value = old_value + change.value
                        if new_value < 0:
                            new_value = 0
                        elif new_value > (len(code_list) - 1):
                            new_value = (len(code_list) - 1)
                        self.world_model.setData(data_index, new_value)
                    elif change.type == MAX:
                        old_code = self.world_model.data(data_index)
                        print 'old_code:', old_code, ' change value:', change.value
                        code_list = self.world_model.attributeDefinitions[attribute_index].codes
                        print 'code_list:', code_list
                        old_value = code_list.index(old_code)
                        print 'old_value:', old_value
                        if old_value > change.value:
                            self.world_model.setData(data_index, change.value)
                    elif change.type == MIN:
                        old_code = self.world_model.data(data_index)
                        code_list = self.world_model.attributeDefinitions[attribute_index].codes
                        old_value = code_list.index(old_code)
                        if old_value < change.value:
                            self.world_model.setData(data_index, change.value)

        self.accept()
                        


    def cancelClicked(self):
        self.close()
