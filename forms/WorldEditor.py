# Copyright 2013 Simon Dominic Hibbs
from PySide.QtCore import *
from PySide.QtGui import *
from model import Models
from model import Foundation
from model import FromWorldLinkModel as LM
from forms import FromWorldLinkTableView as LTV
from log import *

# Manual submit not working. Need to investigate
MAPPER_MODE = QDataWidgetMapper.AutoSubmit


class WorldNameLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(WorldNameLineEdit, self).__init__(parent)
        #self.setPlaceholderText('world name')
        self.setMaxLength(20)

class SectorCoords(QLineEdit):
    def __init__(self, parent=None):
        super(SectorCoords, self).__init__(parent)
        self.setReadOnly(True)
        metrics = QFontMetrics(QApplication.font())
        self.setFixedSize((metrics.width("8888") + 8), (metrics.height() + 8))

class OwningSector(QLineEdit):
    def __init__(self, parent=None):
        super(OwningSector, self).__init__(parent)
        self.setReadOnly(True)

class OwningSubsector(QLineEdit):
    def __init__(self, parent=None):
        super(OwningSubsector, self).__init__(parent)
        self.setReadOnly(True)

class AllegianceNameComboBox(QComboBox):
    def __init__(self, parent=None):
        super(AllegianceNameComboBox, self).__init__(parent)
        self.setModel(QStringListModel(Foundation.allegiance_names))

# For an article on using QComboBox with QDataWidgetMapper:
# http://doc.qt.nokia.com/qq/qq21-datawidgetmapper.html
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


class DescriptionTextEdit(QPlainTextEdit):
    def __init__(self, parent=None):
        super(DescriptionTextEdit, self).__init__(parent)
        #self.setReadOnly(True)
        self.setGeometry(0, 0, 300, 100)

# Custom delegate to handle displaying and modifying an attribute's Description role
class AttributeDescriptionDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(AttributeDescriptionDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        #if index.column() >= Models.ATTRIBUTE_BASE:
        #    return DescriptionTextEdit(parent)
        #else:
        QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        if index.column() >= Models.ATTRIBUTE_BASE:
            data = index.data(Models.DESCRIPTION_ROLE)
            editor.setPlainText(data)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        if index.column() >= Models.ATTRIBUTE_BASE:
            model.setData(index, editor.toPlainText(), Models.DESCRIPTION_ROLE)
        else:
             QStyledItemDelegate.setModelData(self, editor, model, index)



class AttributeWidgetGroup(object):
    def __init__(self,
                 name=None,
                 codes=None,
                 labels=None,
                 description=None
                 ):
        self.name = name
        self.codes = codes
        self.labels = labels
        self.description = description



class WorldDataFrame(QFrame):
    def __init__(self, pmi, parent=None, moveable=False):
        super(WorldDataFrame, self).__init__(parent)
        self.pmi = pmi
        w = self.pmi.model().getWorld(self.pmi)
        #self.setFrameShape(QFrame.StyledPanel)

        self.nameLineEdit = WorldNameLineEdit()
        #self.nameLineEdit.setReadOnly(True)

        self.sectorCoords = SectorCoords()
        self.sectorCoords.setDisabled(True)
        self.owningSector = OwningSector()
        self.owningSector.setDisabled(True)
        self.owningSubsector = OwningSubsector()
        self.owningSubsector.setDisabled(True)
        self.allegianceComboBox = AllegianceNameComboBox()
        #self.worldAttributesFrame = WorldAttributeFrame(self.pmi)
        #self.attributeLabels = []
        self.attributeWidgetList = []
        #self.attributeSelectors = []

        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.pmi.model())
        self.mapper.setSubmitPolicy(MAPPER_MODE)

        # separate mapper to handle attribute Description role data
        self.descriptionMapper = QDataWidgetMapper(self)
        self.descriptionMapper.setModel(self.pmi.model())
        self.descriptionMapper.setSubmitPolicy(MAPPER_MODE)
        self.descriptionMapper.setItemDelegate(AttributeDescriptionDelegate())

        self.mapper.addMapping(self.nameLineEdit, Models.NAME)
        self.mapper.addMapping(self.sectorCoords, Models.SECTOR_COORDS)
        self.mapper.addMapping(self.owningSector, Models.OWNING_SECTOR)
        self.mapper.addMapping(self.owningSubsector, Models.OWNING_SUBSECTOR)
        self.mapper.addMapping(self.allegianceComboBox,
                               Models.ALLEGIANCE_NAME,
                               "currentIndex")

        # World summary data grid
        self.summaryGrid = QGridLayout()
        self.summaryGrid.addWidget(QLabel('World Name:'),0,0)
        self.summaryGrid.addWidget(self.nameLineEdit,0,1)
        self.summaryGrid.addWidget(QLabel('Sector:'),0,2)
        self.summaryGrid.addWidget(self.owningSector,0,3)
        self.summaryGrid.addWidget(QLabel('Sector Hex:'),0,4)
        self.summaryGrid.addWidget(self.sectorCoords,0,5)

        self.summaryGrid.addWidget(QLabel('Allegiance:'),1,0)
        self.summaryGrid.addWidget(self.allegianceComboBox,1,1)
        self.summaryGrid.addWidget(QLabel('Subsector:'),1,2)
        self.summaryGrid.addWidget(self.owningSubsector,1,3)

        # World attributes data grid        
        self.attributeGrid = QGridLayout()
        self.attributeGrid.expandingDirections()
##        self.attributeGrid.addWidget(QLabel('Code'),0,1,Qt.AlignLeft)
##        self.attributeGrid.addWidget(QLabel('Label'),0,1,Qt.AlignLeft)

        self.detailsButtonGroup = QButtonGroup()
        self.detailsButtonGroup.setExclusive(True)

        self.descriptionStack = QStackedWidget()
        
        #self.attributeGrid.addWidget(QLabel('Value'),0,4,Qt.AlignLeft)
        for (count, attribute) in enumerate(self.pmi.model().attributeDefinitions):
            column = count + Models.ATTRIBUTE_BASE
            info_log("Count:" + str(count) +  " Column:" + str(column))

            if self.pmi.model().codedLabels:
                label_list = [(attribute.codes[i] + ' - ' + attribute.labels[i]) for i in range(len(attribute.codes))]
            else:
                label_list = attribute.labels
            self.attributeWidgetList.append(AttributeWidgetGroup(name=QLabel(attribute.name),
                                                                codes=ValueSelector(attribute.codes),
                                                                labels=ValueSelector(label_list),
                                                                description=DescriptionTextEdit()))
##            self.mapper.addMapping(self.attributeWidgetList[count].codes,
##                                   base_column,
##                                   "currentIndex")
            self.mapper.addMapping(self.attributeWidgetList[count].labels,
                                   column,
                                   "currentIndex")
            self.descriptionMapper.addMapping(self.attributeWidgetList[count].description,
                                   column)

            self.descriptionStack.addWidget(self.attributeWidgetList[count].description)

            self.detailsButtonGroup.addButton(QToolButton(), count)

            # The following is to force the mapper to update the model when the attribute value is changed
            self.attributeWidgetList[count].labels.setDetailsButton(self.detailsButtonGroup.button(count))
            
            self.detailsButtonGroup.button(count).setArrowType(Qt.NoArrow)
            self.detailsButtonGroup.button(count).setCheckable(True)
            # Add AttributeSelector widget and it's label to the grid layout
            self.attributeGrid.addWidget(self.attributeWidgetList[count].name,count,0,Qt.AlignLeft)
            ## self.attributeGrid.addWidget(self.attributeWidgetList[count].codes,count,1,Qt.AlignLeft)
            self.attributeGrid.addWidget(self.attributeWidgetList[count].labels,count,1,Qt.AlignLeft)
            self.attributeGrid.addWidget(self.detailsButtonGroup.button(count),count,2,Qt.AlignLeft)

        num_definitions = len(self.pmi.model().attributeDefinitions)

        #self.attributeGrid.addItem(QSpacerItem(1,1,QSizePolicy.Minimum,QSizePolicy.Minimum),(num_definitions + 1),0,Qt.AlignTop|Qt.AlignLeft)
        self.descriptionLabel = QLabel()
        self.attributeGrid.addWidget(self.descriptionLabel, 0, 3, Qt.AlignLeft)
        #self.attributeGrid.addWidget(self.descriptionStack, 1, 3, (num_definitions - 1), 1, Qt.AlignLeft)
        if num_definitions < 10:
            row_stretch = 10
        else:
            row_stretch = -1
        self.attributeGrid.addWidget(self.descriptionStack, 1, 3, row_stretch, 1, 0)
        
        #attributeHBox = QHBoxLayout()
        #attributeHBox.addLayout(self.attributeGrid)
        #attributeHBox.addWidget(self.descriptionStack)

        masterLayout = QVBoxLayout()
        masterLayout.addLayout(self.summaryGrid)
        masterLayout.addLayout(self.attributeGrid)
        self.setLayout(masterLayout)

        self.detailsButtonGroup.buttonClicked[int].connect(self.descriptionStack.setCurrentIndex)
        self.detailsButtonGroup.buttonClicked[int].connect(self.setDescriptionLabel)
        self.detailsButtonGroup.buttonClicked[int].connect(self.moveArrow)
        
        info_log('WorldDataFrame: Row is ' + str(self.pmi.row()))
        self.mapper.setCurrentIndex(self.pmi.row())
        self.descriptionMapper.setCurrentIndex(self.pmi.row())

        self.detailsButtonGroup.buttons()[0].click()


    def resetMappedRow(self, new_pmi):
        # Deprecated?
        self.pmi = new_pmi
        self.mapper.setModel(self.pmi.model())
        self.mapper.setCurrentIndex(self.pmi.row())
        self.descriptionMapper.setModel(self.pmi.model())
        self.descriptionMapper.setCurrentIndex(self.pmi.row())

    def setDescriptionLabel(self, value):
        text = self.attributeWidgetList[value].name.text()
        self.descriptionLabel.setText(text)

    def moveArrow(self, value):
        for button in self.detailsButtonGroup.buttons():
            button.setArrowType(Qt.NoArrow)
        self.detailsButtonGroup.checkedButton().setArrowType(Qt.RightArrow)



class EditWorldDialog(QDialog):
    def __init__(self, pmi, parent=None):
        super(EditWorldDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Edit World')
        self.pmi = pmi

        self.worldDataFrame = WorldDataFrame(pmi)

        self.link_model = LM.FromWorldLinkModel(self.pmi)
        self.linkTableView = LTV.FromWorldLinkTableView(self.link_model)
        self.linkTableView.setItemDelegateForColumn(LTV.LINK_LINE,
                                                    LTV.NetworkLineStyleDelegate(self))
        
        self.okButton = QPushButton("OK")
        self.applyButton = QPushButton("Apply")
        self.randomRollButton = QPushButton("Random Roll")
##        self.reportButton = QPushButton("View Report")
        self.deleteWorldButton = QPushButton("Delete World")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.applyButton)
##        buttonLayout.addWidget(self.reportButton)
        buttonLayout.addWidget(self.randomRollButton)
        buttonLayout.addWidget(self.deleteWorldButton)
        buttonLayout.addStretch()

        dataLayout = QHBoxLayout()
        dataLayout.addWidget(self.worldDataFrame)
        dataLayout.addWidget(self.linkTableView)

        masterLayout = QVBoxLayout()
        masterLayout.addLayout(dataLayout)
        masterLayout.addLayout(buttonLayout)
        self.setLayout(masterLayout)

        self.okButton.clicked.connect(self.okButtonClicked)
        self.applyButton.clicked.connect(self.applyButtonClicked)
##        self.reportButton.clicked.connect(self.reportButtonClicked)
        self.randomRollButton.clicked.connect(self.randomRollButtonClicked)
        self.deleteWorldButton.clicked.connect(self.deleteWorldButtonClicked)
        self.pmi.model().rowsAboutToBeRemoved.connect(self.checkWorldRemoved)

    def okButtonClicked(self):
        self.close()

    def applyButtonClicked(self):
        info_log('EditWorldDialog: mapper.submit()')
        self.worldDataFrame.mapper.submit()
        self.worldDataFrame.descriptionMapper.submit()

##    def reportButtonClicked(self):
##        self.reportDialog = WorldReport.WorldReportDialog(self.pmi, self)
##        self.reportDialog.show()
##        self.reportDialog.raise_()
##        self.reportDialog.activateWindow()

    def deleteWorldButtonClicked(self):
        self.pmi.model().removeRow(self.pmi.row())
        self.close()

    def randomRollButtonClicked(self):
        self.pmi.model().regenerateWorld(self.pmi.row())

    def checkWorldRemoved(self, parent, start, end):
        if self.pmi.row() in range(start, (end + 1)):
            info_log('Closing World Editor: world deleted')
            self.close()
