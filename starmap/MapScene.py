# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

import sys
import os
import math
from PySide import QtCore, QtGui
import networkx as nx
from log import *
from model import Models
#from model import WorldLinkModel as Wlm
from starmap import MapGlyphs
from starmap import MapGrid
from starmap import AddLabel
from forms import WorldEditor, InterWorldLinkEditor
from reports import PreviewMap
from reports import WorldReport
#from reports import SubsectorReport
from reports import StatisticsDialog

WORLDS = 0
CELLS = 1
SUBSECTORS = 2
SECTORS = 3

## Deprecated
##class RegionManager(QtGui.QDialog):
##    def __init__(self, world_model, cell_list, parent=None):
##        super(UpdateRegionDialog, self).__init__(parent)
##        debug_log('Started Region Manager Dialog')
##        self.setAttribute(Qt.WA_DeleteOnClose)
##        self.setWindowTitle("Region Manager")
##        self.model = world_model
##        self.cell_list = cell_list
##
##        self.vlayout = QtGui.QVBoxLayout()
##        self.vlayout.addWidget(QtGui.QLabel('Select an existing region, or enter the name of a new region to create.'))
##        
##        self.line_edit = QtGui.QLineEdit(self)
##        self.line_edit.setMaxLength(20)
##        self.vlayout.addWidget(self.line_edit)
##
##        self.list_widget = QtGui.QListWidget(self)
##        for region_name in self.model.hexRegionNames:
##            if region_name != 'None':
##                self.list_widget.addItem(region_name)
##        self.vlayout.addWidget(self.list_widget)
##
##        self.hlayout = QtGui.QHBoxLayout()
##        self.ok_button = QtGui.QPushButton('Ok')
##        self.hlayout.addWidget(self.ok_button)
##        self.cancel_button = QtGui.QPushButton('Cancel')
##        self.hlayout.addWidget(self.cancel_button)
##
##        self.vlayout.addLayout(self.hlayout)
##
##        self.list_widget.itemSelectionChanged.connect(self.regionSelectionChanged)
##        self.ok_button.clicked.connect(self.okClicked)
##        self.cancel_button.clicked.connect(self.cancelClicked)
##
##
##    def addNewHexRegion(self, region_name, cell_list):
##        self.model.addNewHexRegion(region_name)
##        self.updateHexRegionName(region_name, cell_list)
##
##
##    def updateHexRegionName(self, region_name, cell_list):
##        if self.selectionType == 'Hexes':
##            cell_list = []
##            for cell in self.selectedItems():
##                cell_list.append(cell)
##
##        coord_list = []
##        for cell in cell_list:
##            coord_list.append((cell.col, cell.row))
##        self.model.updateHexRegionName(region_name, coord_list)
##
##
##    def regionSelectionChanged(self):
##        items = self.list_widget.selectedItems()
##        if len(items) != 1:
##            debug_log('UpdateRegionDialog: Number of selected items in region list not 1')
##        elif items[0].text() != '' and len(items[0].text()) > 0:
##            self.line_edit.setText(items[0].text())
##
##    def okClicked(self):
##        region_name = self.line_edit.text()
##        if region_name in self.model.hexRegionNames:
##            self.updateHexRegionName(region_name, self.cell_list)
##        else:
##            self.addNewHexRegion(region_name, self.cell_list)
##        
##    def cancelClicked(self):
##        self.close()



class MapScene(QtGui.QGraphicsScene):
    SelectCells, RubberBand, HandDrag, InsertText, MoveItem  = range(5)

    changeCellsSelectable = QtCore.Signal(bool)
    setFromTradeWorld = QtCore.Signal()
    setToTradeWorld = QtCore.Signal()

    def __init__(self, model, parent=None):
        QtGui.QGraphicsScene.__init__(self, parent)

        self.model = model

        # Moved worldLinks to model
        #self.worldLinks = Wlm.WorldLinkModel()
        
        self.myMode = self.SelectCells
        self.selectionType = 'Worlds'

        self.dialogs = {}
        self.lastScale = 0.12

        self.grid = MapGrid.Grid(self.model.secsWide, self.model.secsHigh)
        self.addItem(self.grid)
        self.grid.config()
        self.quickLink = False

        for subsector in self.model.getSubsectorList():
            self.setSubsectorData(subsector.name,
                                  subsector.subsectorCol,
                                  subsector.subsectorRow)

        for sector in self.model.getSectorList():
            self.setSectorData(sector.name,
                                  sector.sectorCol,
                                  sector.sectorRow)

        self.model.network_model.linksChanged.connect(self.linksChanged)
        self.selectionChanged.connect(self.checkNetworkEditMode)
        # Force initial redraw
        self.linksChanged()


    def setSubsectorData(self, name, subsectorCol, subsectorRow):
        self.grid.setSubsectorData(name, subsectorCol, subsectorRow)

    def setSectorData(self, name, sectorCol, sectorRow):
        self.grid.setSectorData(name, sectorCol, sectorRow)

    def worldChanged(self, row):
        self.grid.worldChanged(row)

    def linksChanged(self):
        self.grid.linksChanged()

    def insertWorld(self, pmi):
        # Used for all addition and updating of world data.
        if self.selectionType == 'Worlds':
            selectable = True
        else:
            selectable = False
        self.grid.insertWorld(pmi, selectable)


    def removeWorld(self, row):
        self.grid.removeWorld(row)

    def deleteWorldsFromModel(self, pmi_list):
        msgBox = QtGui.QMessageBox()
        world_name_text = ""
        for pmi in pmi_list:
            world_name = pmi.model().index(pmi.row(), Models.NAME).data()
            world_name_text += "        " + str(world_name) + "\n"
        if len(pmi_list) <= 10:
            msgBox.setText("The following worlds will be deleted:")
            msgBox.setInformativeText(world_name_text)
        else:
            numtext = str(len(pmi_list))
            msgBox.setText("The following number of worlds will be deleted:")
            msgBox.setInformativeText("          " + numtext + " worlds.")
            msgBox.setDetailedText(world_name_text)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok |
                                  QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret == QtGui.QMessageBox.Ok:
            for pmi in pmi_list:
                self.model.removeRow(pmi.row())

    def displaySectorGrid(self, toggle):
        item_type = MapGlyphs.SECTOR_GLYPH_TYPE
        self.setItemVisible(item_type, toggle)

    def displaySubsectorGrid(self, toggle):
        item_type = MapGlyphs.SUBSECTOR_GLYPH_TYPE
        self.setItemVisible(item_type, toggle)

    # Intended as an internal method. External callers should use the nethods above
    def setItemVisible(self, item_type, toggle):
        for item in self.items():
            try:
                if item._type == item_type:
                    item.setVisible(toggle)
            except AttributeError:
                pass

    def clearWorlds(self):
        self.grid.clearWorlds()


    def setCellsSelectable(self, flag):
        self.changeCellsSelectable.emit(flag)

    def selectRegion(self, index):
        if index <= (len(self.model.hexRegionNames) - 1):
            self.setCellsSelectable(False)
            self.setCellsSelectable(True)
            self.grid.selectCells(self.model.hexRegionCells[index])
            self.model.selectedRegionIndex = index
        else:
            debug_log('Group index ' + str(index) + ' not valid.')
            debug_log('model.hexRegionNames: ' + str(self.model.hexRegionNames))

##    def focusOutEvent(self, event):
##        self.clearSelection()
##        QGraphicsScene.focusOutEvent(event)

    def toggleAllegianceDisplay(self, checked):
        self.grid.toggleAllegianceDisplay(checked)

    def toggleQuickLink(self, flag):
        self.quickLink = flag

    def setAllegiance(self, code):
        cell_list = []
        
        if self.selectionType == 'Hexes':
            for cell in self.selectedItems():
                cell_list.append(cell)

        elif self.selectionType == 'Sectors':
            for sector in self.selectedItems():
                cell_list = cell_list + sector.cells

        elif self.selectionType == 'Subsectors':
            for subsector in self.selectedItems():
                cell_list = cell_list + subsector.cells

        for cell in cell_list:
            pmi = self.grid.worldPmiAt(cell.col, cell.row)
            if pmi is not None:
                self.model.setAllegianceCode(pmi, code)


    def viewMoveDetected(self, value):
        pass
        #print 'View Moved!', value

    def setMode(self, mode):
        self.myMode = mode

    def setScale(self, scale):
        if scale > 0.12:
            self.grid.setHexGridVisible(True)
        else:
            self.grid.setHexGridVisible(False)

        if scale >= 0.80:
            self.grid.setCoordsVisible(True)
        else:
            self.grid.setCoordsVisible(False)

        if scale > 0.18:
            self.grid.showWorldDetails(True)
        else:
            self.grid.showWorldDetails(False)
        
        if 0.18 <= scale <= 0.37:
            self.grid.showSubsectorNames(True)
        else:
            self.grid.showSubsectorNames(False)

        if scale < 0.18:
            self.grid.showSectorNames(True)
        else:
            self.grid.showSectorNames(False)

        self.lastScale = scale

    def setSelectionType(self, selectionType):
        self.selectionType = selectionType
        for item in self.items():
            item.setSelected(False)
            item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)

            try:
                if (selectionType == 'Hexes')\
                   and item.itemType == MapGlyphs.GRID_CELL_TYPE:
                    item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
                elif selectionType == 'Subsectors' \
                   and item.itemType == MapGlyphs.SUBSECTOR_GLYPH_TYPE:
                    item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
                elif selectionType == 'Sectors' \
                   and item.itemType == MapGlyphs.SECTOR_GLYPH_TYPE:
                    item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
            except:
                pass


    def updateHexRegionIndex(self, index):
        if self.selectionType == 'Hexes':
            cell_list = []
            for cell in self.selectedItems():
                cell_list.append(cell)

        coord_list = []
        for cell in cell_list:
            coord_list.append((cell.col, cell.row))
        self.model.updateHexRegionIndex(index, coord_list)


    def addNewHexRegion(self, region_name, cell_list):
        self.model.addNewHexRegion(region_name)
        self.updateHexRegionName(region_name, cell_list)

    def updateHexRegionName(self, region_name, cell_list):
        if self.selectionType == 'Hexes':
            cell_list = []
            for cell in self.selectedItems():
                cell_list.append(cell)

        coord_list = []
        for cell in cell_list:
            coord_list.append((cell.col, cell.row))
        self.model.updateHexRegionName(region_name, coord_list)


    def populateCells(self, cell_list, random_occurrence=True):
        progress = QtGui.QProgressDialog('Populating selected region',
                                                     'Abort',
                                                     0,
                                                     len(cell_list))
        progress.setWindowTitle('World Generation')
        count = 0
        for cell in cell_list:
            pmi = self.grid.worldPmiAt(cell.col, cell.row)
            if pmi != None:
                self.model.removeRow(pmi.row())
            
            if self.model.rollToPopulate() or not random_occurrence:
                last_row = self.model.rowCount()
                self.model.currentCell =(cell.col, cell.row)
                self.model.insertRandomWorld(last_row)

            count = count + 1
            progress.setValue(count)


    # Methods called by the link network view

    def linkNetworkChanged(self, row):
        print "scene:linkNetworkChanged", row
        #Pass to MapGrid to redraw the network on the scene, if it's visible.

    def insertLinkNetwork(self, network_pmi):
        print "scene:insertLinkNetwork", network_pmi

    def removeLinkNetwork(self, row):
        print "scene:removeLinkNetwork", row

    def clearLinkNetworks(self):
        print "scene:clearLinkNetworks"
        pass


    # methods invoked by the scene context menu

    def addLink(self, pmi_list):
        if len(pmi_list) != 2:
            debug_log('MapScene:addLink: Error, wrong number of PMIs: ' + \
                      str(pmi_list))
        else:
            world1 = self.model.getWorld(pmi_list[0])
            world2 = self.model.getWorld(pmi_list[1])
            network_name = self.model.network_model.selectedNetworkName
            self.model.network_model.addLink((world1.col, world1.row),
                                          (world2.col, world2.row),
                                          network_name)


    def removeLink(self, pmi_list):
        if len(pmi_list) != 2:
            debug_log('MapScene:removeLink: Error, wrong number of PMIs: ' + \
                      str(pmi_list))
        else:
            world1 = self.model.getWorld(pmi_list[0])
            world2 = self.model.getWorld(pmi_list[1])
            network_name = self.model.network_model.selectedNetworkName
            self.model.network_model.removeLink((world1.col, world1.row),
                                             (world2.col, world2.row),
                                             network_name)

    def checkNetworkEditMode(self):
        if self.selectionType == 'Hexes' and self.quickLink == True:
            cell_list = self.selectedItems()
            if len(cell_list) == 2:
                pmi_list = []
                for cell in cell_list:
                    pmi = self.grid.worldPmiAt(cell.col, cell.row)
                    if pmi is not None:
                        pmi_list.append(pmi)
                if len(pmi_list) == 2:
                    debug_log('MapScene.checkNetworkEditMode: Two worlds selected!')
                    myView = self.views()[0]
                    self.dialog = InterWorldLinkEditor.InterWorldLinkEditor(
                                            self.model,
                                            pmi_list,
                                            cell_list,
                                            parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()
                    self.dialog.move((self.dialog.x() + 500), self.dialog.y())


    def contextMenuEvent(self, event):

        region_menu = QtGui.QMenu('Select Region')
        for region_name in self.model.hexRegionNames:
            if region_name == 'None':
                region_menu.addAction(region_name)
            else:
                region_menu.addAction(region_name)
        
        if len(self.selectedItems()) == 0:
            menu = QtGui.QMenu()
            menu.addMenu(region_menu)
            selectedAction = menu.exec_(event.screenPos())

            if selectedAction is not None:
                if selectedAction.text() in self.model.hexRegionNames:
                    region_index = self.model.hexRegionNames.index(selectedAction.text())
                    self.setCellsSelectable(False)
                    self.setCellsSelectable(True)
                    self.grid.selectCells(self.model.hexRegionCells[region_index])
            

        if self.selectionType == 'Hexes' or self.selectionType == 'Links':
            
            cell_list = []
            for cell in self.selectedItems():
                cell_list.append(cell)



            # Single cell selected
            if len(cell_list) == 1:
                
                x = cell_list[0].col
                y = cell_list[0].row
                pmi = self.grid.worldPmiAt(x, y)

                menu = QtGui.QMenu()
                addWorld = False
                editWorld = False
                worldReport = False
                #tradeFrom = False
                #tradeTo = False
                deleteWorld = False
                addLabel = False

                if pmi is not None:
                    editWorld = menu.addAction('Edit World')
                    worldReport = menu.addAction('View Report')
                    #tradeFrom = menu.addAction('Trade From Here')
                    #tradeTo = menu.addAction('Trade To Here')
                    separator = menu.addSeparator()
                    deleteWorld = menu.addAction('Delete World')
                else:
                    addWorld = menu.addAction('Add World')
                    addLabel = menu.addAction('Add Label')

                menu.addMenu(region_menu)

                selectedAction = menu.exec_(event.screenPos())
        
                if selectedAction == None:
                    pass

                elif selectedAction == editWorld:
                    myView = self.views()[0]
                    self.dialog = WorldEditor.EditWorldDialog(
                                                pmi,
                                                parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()

                elif selectedAction == worldReport:
                    myView = self.views()[0]
                    self.dialog = WorldReport.WorldReportDialog(pmi,
                                                                parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()

##                elif selectedAction == tradeFrom:
##                    self.model.fromTradeWorldPmi = pmi
##                    self.setFromTradeWorld.emit()
##
##                elif selectedAction == tradeTo:
##                    self.model.toTradeWorldPmi = pmi
##                    self.setToTradeWorld.emit()

                elif selectedAction == addWorld:
                    self.populateCells(cell_list, False)

                elif selectedAction == addLabel:
                    myView = self.views()[0]
                    self.dialog = AddLabel.AddLabelDialog(cell_list,
                                                          parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()

                elif selectedAction == deleteWorld:
                    #self.model.removeRow(pmi.row())
                    self.deleteWorldsFromModel([pmi])

                elif selectedAction is not None:
                    if selectedAction.text() in self.model.hexRegionNames:
                        region_index = self.model.hexRegionNames.index(selectedAction.text())
                        self.setCellsSelectable(False)
                        self.setCellsSelectable(True)
                        self.grid.selectCells(self.model.hexRegionCells[region_index])
                    

            # Multiple cells selected
            elif len(cell_list) > 1:
                
                pmi_list = []
                for cell in cell_list:
                    pmi = self.grid.worldPmiAt(cell.col, cell.row)
                    if pmi is not None:
                        pmi_list.append(pmi)

                menu = QtGui.QMenu()

                generateRegion = False
                deleteWorlds = False
                reGenerateWorlds = False
                reGenerateRegion = False
                statistics = False
                removeLink = False
##                addLink = False
                editLinks = False

                if len(pmi_list) == 2 and len(cell_list) == 2:
                    world1 = self.model.getWorld(pmi_list[0])
                    world2 = self.model.getWorld(pmi_list[1])
                    
                    editLinks = menu.addAction('Edit Links')
                    
##                    network_name = self.model.network_model.selectedNetworkName
##                    if network_name is not None:
##                        if self.model.network_model.linkExists((world1.col, world1.row),
##                                                            (world2.col, world2.row),
##                                                            network_name):
##                            removeLink = menu.addAction('Remove Link')
##                            remove_link = True
##                        else:
##                            addLink = menu.addAction('Create Link')
##                            add_link = True

                if len(pmi_list) == 0:
                    generateRegion = menu.addAction('Generate Region')
                    populateAll = menu.addAction('Populate All Hexes')
                else:
                    deleteWorlds = menu.addAction('Delete Selected Worlds')
                    populateAll = menu.addAction('Populate All Hexes')
                    reGenerateWorlds = menu.addAction('Re-Generate Selected Worlds')
                    reGenerateRegion = menu.addAction('Re-Generate Region')
                    statistics = menu.addAction('Statistics')

                createHexRegion = menu.addAction('Create Hex Region')
                menu.addMenu(region_menu)
                selectedAction = menu.exec_(event.screenPos())

                if selectedAction == editLinks:
                    myView = self.views()[0]
                    self.dialog = InterWorldLinkEditor.InterWorldLinkEditor(
                                            self.model,
                                            pmi_list,
                                            cell_list,
                                            parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()

                if selectedAction == populateAll:
                    self.populateCells(cell_list, random_occurrence=False)

                if selectedAction == generateRegion \
                        or selectedAction == reGenerateRegion:
                    self.populateCells(cell_list, random_occurrence=True)

                elif selectedAction == deleteWorlds:
                    #for pmi in pmi_list:
                    #    self.model.removeRow(pmi.row())
                    self.deleteWorldsFromModel(pmi_list)

                elif selectedAction == reGenerateWorlds:
                    for pmi in pmi_list:
                        pmi.model().regenerateWorld(pmi.row())

                elif selectedAction == statistics:
                    myView = self.views()[0]
                    title, ok = QtGui.QInputDialog.getText(myView, self.tr("Report Title"),
                                                       self.tr("Statistics Report Title:"),
                                                       QtGui.QLineEdit.Normal)
                    self.dialog = StatisticsDialog.StatisticsDialog(
                                             pmi_list,
                                             len(cell_list),
                                             title,
                                             parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()

                elif selectedAction == createHexRegion:
                    region_name, ok = QtGui.QInputDialog.getText(QtGui.QWidget(), 'Crate New Hex Region',
                                                                'New Region Name:',
                                                                QtGui.QLineEdit.Normal)
                    if ok and region_name:
                        self.addNewHexRegion(str(region_name), cell_list)
                    else:
                        debug_log('MapScene: Adding new region failed. Name: ' + str(region_name))

                elif selectedAction is not None:
                    if selectedAction.text() in self.model.hexRegionNames:
                        region_index = self.model.hexRegionNames.index(selectedAction.text())
                        self.setCellsSelectable(False)
                        self.setCellsSelectable(True)
                        self.grid.selectCells(self.model.hexRegionCells[region_index])


        elif self.selectionType == 'Sectors':
            sector_list = []
            for sector in self.selectedItems():
                sector_list.append(sector)

            menu = QtGui.QMenu()
            renameSector = False
            previewMap = False
            populateSector = False
            deleteWorlds = False
            statistics = False
##            importSec = False
            
            if len(sector_list) == 1:
                renameSector = menu.addAction('Rename Sector')
                previewMap = menu.addAction('Preview Map')
                populateSector = menu.addAction('Generate Sector')
                deleteWorlds = menu.addAction('Delete Worlds')
                statistics = menu.addAction('Show Statistics')
##                importSEC = menu.addAction('Import SEC file')

            elif len(sector_list) > 1:
                populateSector = menu.addAction('Generate Sectors')
                deleteWorlds = menu.addAction('Delete Worlds')
                statistics = menu.addAction('Show Statistics')
                
            selectedAction = menu.exec_(event.screenPos())

            if selectedAction == renameSector:
                sector = sector_list[0]
                col = sector.sectorCol
                row = sector.sectorRow
                myView = self.views()[0]
                new_name, ok = QtGui.QInputDialog.getText(myView,
                                                    'New Sector Name',
                                                    'Sector Name:',
                                                    QtGui.QLineEdit.Normal,
                                                    sector.name)
                self.model.renameSector(col, row, new_name)
                self.setSectorData(new_name, col, row)
                
            elif selectedAction == previewMap:
                col = sector_list[0].sectorCol
                row = sector_list[0].sectorRow
                myView = self.views()[0]
                self.dialog = PreviewMap.PreviewDialog(
                                         glyph=sector_list[0],
                                         region_type=PreviewMap.SECTOR, 
                                         map_scene=self,
                                         parent=myView)
                self.dialog.show()
                self.dialog.raise_()
                self.dialog.activateWindow()

            if selectedAction == populateSector:
                cell_list = []
                for sector in sector_list:
                    cell_list = cell_list + sector.cells
                self.populateCells(cell_list, random_occurrence=True)

            elif selectedAction == deleteWorlds:
                pmi_list = []
                for sector in sector_list:
                    for cell in sector.cells:
                        x = cell.col
                        y = cell.row
                        pmi = self.grid.worldPmiAt(x, y)
                        if pmi != None:
                            #self.model.removeRow(pmi.row())
                            pmi_list.append(pmi)
                if len(pmi_list) > 0:
                       self.deleteWorldsFromModel(pmi_list)

            elif selectedAction == statistics:
                cell_list = []
                names = ""
                for sector in sector_list:
                    cell_list = cell_list + sector.cells
                    if names == "":
                        prefix = "Sector: "
                        names = sector.name
                    else:
                        prefix = "Sectors: "
                        names += ", " + sector.name
                names = prefix + names
                
                pmi_list = []
                for cell in cell_list:
                    pmi = self.model.getPmiAt(cell.col, cell.row)
                    if pmi != None:
                        pmi_list.append(pmi)
                if len(pmi_list) > 0:
                    myView = self.views()[0]
                    self.dialog = StatisticsDialog.StatisticsDialog(
                                             pmi_list,
                                             len(cell_list),
                                             names,
                                             parent=myView)
                    self.dialog.show()
                    self.dialog.raise_()
                    self.dialog.activateWindow()


##            elif selectedAction == importSEC:
##                sector = sector_list[0]
##                myView = self.views()[0]
##                default_path = self.model.project_path
##                filename = QtGui.QFileDialog.getOpenFileName(myView,
##                                                'Open .SEC file',
##                                                default_path,
##                                                'SEC Files (*.SEC)')
##                self.model.importSEC(filename,
##                                     sector.sectorCol,
##                                     sector.sectorRow)
##                debug_log('SEC import complete')


        elif self.selectionType == 'Subsectors':
            subsector_list = []
            for subsector in self.selectedItems():
                subsector_list.append(subsector)

            menu = QtGui.QMenu()
            renameSubsector = False
            previewMap = False
            #subsectorReport = False
            populateSubsector = False
            deleteWorlds = False
            statistics = False

            if len(subsector_list) == 1:
                renameSubsector = menu.addAction('Rename Subsector')
                previewMap = menu.addAction('Preview Map')
                #subsectorReport = menu.addAction('Subsector Report')
                populateSubsector = menu.addAction('Generate Subsector')
                deleteWorlds = menu.addAction('Delete Worlds')
                statistics = menu.addAction('Show Statistics')

            elif len(subsector_list) > 1:
                populateSubsector = menu.addAction('Generate Subsector')
                deleteWorlds = menu.addAction('Delete Worlds')
                statistics = menu.addAction('Show Statistics')
                
            selectedAction = menu.exec_(event.screenPos())

            if selectedAction == renameSubsector:
                subsector = subsector_list[0]
                col = subsector.subsectorCol
                row = subsector.subsectorRow
                myView = self.views()[0]
                new_name, ok = QtGui.QInputDialog.getText(myView,
                                                    'New Subsector Name',
                                                    'Subsector Name:',
                                                    QtGui.QLineEdit.Normal,
                                                    subsector.name)
                self.model.renameSubsector(col, row, new_name)
                self.setSubsectorData(new_name, col, row)

            elif selectedAction == previewMap:
                col = subsector_list[0].subsectorCol
                row = subsector_list[0].subsectorRow
                myView = self.views()[0]
                self.dialog = PreviewMap.PreviewDialog(
                                         glyph=subsector_list[0],
                                         region_type=PreviewMap.SUBSECTOR, 
                                         map_scene=self,
                                         parent=myView)
                self.dialog.show()
                self.dialog.raise_()
                self.dialog.activateWindow()

##            elif selectedAction == subsectorReport:
##                pmi_list = []
##                for subsector in subsector_list:
##                     for cell in subsector.cells:
##                        x = cell.col
##                        y = cell.row
##                        pmi = self.grid.worldPmiAt(x, y)
##                        if pmi != None:
##                            pmi_list.append(pmi)
##                myView = self.views()[0]
##                col = subsector_list[0].subsectorCol
##                row = subsector_list[0].subsectorRow
##                self.dialog = SubsectorReport.SubsectorReportDialog(
##                                    subsector_glyph=subsector_list[0],
##                                    pmi_list=pmi_list,
##                                    model=self.model,
##                                    parent=myView)
##                self.dialog.show()
##                self.dialog.raise_()
##                self.dialog.activateWindow()

            
            elif selectedAction == populateSubsector:
                cell_list = []
                for subsector in subsector_list:
                    cell_list = cell_list + subsector.cells
                self.populateCells(cell_list, random_occurrence=True)

            elif selectedAction == deleteWorlds:
                pmi_list = []
                for subsector in subsector_list:
                    for cell in subsector.cells:
                        x = cell.col
                        y = cell.row
                        pmi = self.grid.worldPmiAt(x, y)
                        if pmi != None:
                            #self.model.removeRow(pmi.row())
                            pmi_list.append(pmi)
                if len(pmi_list) > 0:
                       self.deleteWorldsFromModel(pmi_list)

            elif selectedAction == statistics:
                cell_list = []
                names = ""
                for subsector in subsector_list:
                    cell_list = cell_list + subsector.cells
                    if names == "":
                        prefix = "Subsector: "
                        names = subsector.name
                    else:
                        prefix = "Subsectors: "
                        names += ", " + subsector.name
                names = prefix + names
                pmi_list = []
                for cell in cell_list:
                    pmi = self.model.getPmiAt(cell.col, cell.row)
                    if pmi != None:
                        pmi_list.append(pmi)
                myView = self.views()[0]
                self.dialog = StatisticsDialog.StatisticsDialog(
                                         pmi_list,
                                         len(cell_list),
                                         names,
                                         parent=myView)
                self.dialog.show()
                self.dialog.raise_()
                self.dialog.activateWindow()


    def mousePressEvent(self, mouseEvent):
        if (mouseEvent.button() != QtCore.Qt.LeftButton):
            return

        if self.myMode == self.SelectCells:
            QtGui.QGraphicsScene.mousePressEvent(self, mouseEvent)

        elif self.myMode == self.RubberBand:
            pass    # Don't propagate mouse events to the default handler
        elif self.myMode == self.HandDrag:
            pass    # Don't propagate mouse events to the default handler
        else:
            QtGui.QGraphicsScene.mousePressEvent(self, mouseEvent)

# Unsure about this. Probably deprecated
##    def isItemChange(self, type):
##        for item in self.selectedItems():
##            if isinstance(item, type):
##                return True
##        return False




class WorldItemView(QtGui.QAbstractItemView):
    """ Hidden view which interfaces between the model and the scene.
    """
    def __init__(self, model, parent=None):
        QtGui.QAbstractItemView.__init__(self, parent)
        self.hide()
        self.setModel(model)
        self.my_model = model
        self.scene = MapScene(self.my_model)
        self.resetWorlds()
        #self.linkNetworkView = LinkNetworkItemView(self.my_model.linkNetworks, self.scene)

    def dataChanged(self, topLeft, bottomRight):
        top_row = topLeft.row()
        bottom_row = bottomRight.row()
        #debug_log("Top row " + str(top_row) + " Bottom row " + str(bottom_row))
        for row in range(top_row, (bottom_row + 1)):
            self.scene.worldChanged(row)

    def rowsInserted(self, parent, start, end):
        for row in range(start, (end + 1) ):
            pmi = self.my_model.getPMI(row)
            self.scene.insertWorld(pmi)

    def rowsAboutToBeRemoved(self, parent, start, end):
        for row in range(start, (end + 1)):
            self.scene.removeWorld(row)

    def resetWorlds(self):
        self.scene.clearWorlds()
        # Add worlds to scene
        last_row = self.my_model.rowCount() - 1
        self.rowsInserted(None, 0, last_row)


