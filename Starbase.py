#!/usr/bin/env python
# Copyright 2013 Simon Dominic Hibbs
# Email: simon.hibbs@gmail.com
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys
import math
from PySide import QtCore, QtGui
#from PyQt4 import QtOpenGL
from model import Models
from model import NetworkModel as NWM
from starmap import MapGlyphs
from starmap import MapScene
from projects import ProjectManager
#from forms import WorldBrowser
from forms import AllegianceEditor
from forms import NetworkManager as nm
#from forms import Trade
#from forms import Trade
from resources import starmap_rc
import log

log.set_logger()


InsertTextButton = 10

class OccurrenceSpinBox(QtGui.QSpinBox):
    def __init__(self):
        QtGui.QSpinBox.__init__(self)
        self.setMinimum(-2)
        self.setMaximum(2)
        self.setValue(0)
        self.lineEdit().setReadOnly(True)

    def textFromValue(self, value):
        if value >= 0:
            text = '+' + str(value)
            return text
        elif value < 0:
            text = str(value)
            return text


class OccurrenceSpinBoxPC(QtGui.QSpinBox):
    def __init__(self):
        QtGui.QSpinBox.__init__(self)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setValue(50)
        self.setSingleStep(10)
        self.setSuffix("%")
        #self.lineEdit().setReadOnly(True)




class MapView(QtGui.QGraphicsView):
    
    changeZoomLevel = QtCore.Signal(QtGui.QWheelEvent)
    
    def __init__(self,  scene=None):
        QtGui.QGraphicsView.__init__(self,  scene)
        #self.setViewportUpdateMode(self.SmartViewportUpdate)
        self.setViewportUpdateMode(self.FullViewportUpdate)
        #self.setViewport(QtOpenGL.QGLWidget())
        self.hzsb = self.horizontalScrollBar()
        self.vtsb = self.verticalScrollBar()
        self.hzsb.valueChanged[int].connect(scene.viewMoveDetected)
        self.vtsb.valueChanged[int].connect(scene.viewMoveDetected)

    def wheelEvent(self,  event):
        view_pos = event.pos()
        scene_pos = self.mapToScene(view_pos)
        self.centerOn(scene_pos)
        self.changeZoomLevel.emit(event)

    def setupMatrix(self, ml):
        self.setMatrix(QtGui.QMatrix(ml[0], ml[1], ml[2], ml[3], ml[4], ml[5]))


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.model = Models.WorldModel()

        self.model.regionAdded.connect(self.regionAdded)
        self.model.regionDisbanded.connect(self.regionDisbanded)

        self.createActions()
        self.createMenus()
        #self.menuWidget().installEventFilter(self)
        #self.installEventFilter(self)

        #self.beginCreateRegion = False
        self.createToolbars()

        layout = QtGui.QHBoxLayout()

        # Select and load a project
        self.projectManager()

        # Now we have a project loaded, finish setting up the main window
        layout.addWidget(self.view)
        self.view.changeZoomLevel.connect(self.wheelScrollZoom)

        self.widget = QtGui.QWidget()
        self.widget.setLayout(layout)

        self.setCentralWidget(self.widget)
        self.setWindowTitle("StarBase")
        self.pointerGroupClicked(1)

        self.sceneScaleCombo.setCurrentIndex(self.model.initialZoomLevel)
        self.sceneScaleChanged(self.sceneScaleCombo.currentText())
        
        self.view.horizontalScrollBar().setValue(self.model.horizontalScroll)
        self.view.verticalScrollBar().setValue(self.model.verticalScroll)
        #self.view.setupMatrix(self.model.initalDisplayMatrix)
        self.selectionTypeCombo.setCurrentIndex(0)
        self.selectionTypeChanged(self.selectionTypeCombo.currentText())

        #self.scene.setFromTradeWorld.connect(self.setFromTradeWorld)
        #self.scene.setToTradeWorld.connect(self.setToTradeWorld)
        #self.generateCargoButton.clicked.connect(self.generateCargo)
        #self.tradeButton.clicked.connect(self.openTradeDialog)
        

    def selectionTypeChanged(self, selectionType):
        self.scene.setSelectionType(selectionType)
        if selectionType == 'Hexes':
            self.quickLinkCheckBox.setDisabled(False)
        else:
            self.quickLinkCheckBox.setDisabled(True)

    # Deprecated
    def setWorldOccurrenceDM(self, value):
        self.model.worldOccurrenceDM = value

    def setWorldOccurrence(self, value):
        print value
        self.model.worldOccurrence = value

    def toggleAutoName(self, flag):
        if flag == QtCore.Qt.Checked:
            self.model.toggleAutoName(True)
        else:
            self.model.toggleAutoName(False)

    def toggleQuickLink(self, flag):
        if flag == QtCore.Qt.Checked:
            self.scene.toggleQuickLink(True)
        else:
            self.scene.toggleQuickLink(False)

    def toggleDisplayNetworkLinks(self, flag):
        if flag == QtCore.Qt.Checked:
            self.model.network_model.setLinksVisible(True)
        else:
            self.model.network_model.setLinksVisible(False)

    def toggleAllegianceDisplay(self, flag):
        if flag == QtCore.Qt.Checked:
            self.scene.toggleAllegianceDisplay(True)
        else:
            self.scene.toggleAllegianceDisplay(False)

##    def eventFilter(self, obj, event):
##        if obj == self.menuWidget() :
##            try :
##                if event.key() ==  QtCore.Qt.Key_Z:
##                    
##                    if event.type() == QtCore.QEvent.KeyPress:
##                        if self.pointerTypeGroup.checkedId() != self.scene.HandDrag:
##                            print "Enabling Drag"
##                            self.view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
##                            self.view.setInteractive(False)
##                            self.scene.setMode(self.pointerTypeGroup.checkedId())
##
##                    elif event.type() == QtCore.QEvent.KeyRelease:
##                        if self.pointerTypeGroup.checkedId() != self.scene.HandDrag:
##                            print "Disabling Drag"
##                            self.view.setDragMode(QtGui.QGraphicsView.NoDrag)
##                            self.view.setInteractive(True)
##                            self.scene.setMode(self.pointerTypeGroup.checkedId())
##                
##                    return True
##                else:
##                    return False
##            except:
##                return False
###        False
##        return QtGui.QMainWindow.eventFilter(self, obj, event)
##
##    def keyPressEvent(self, event):
##        if event.key() == QtCore.Qt.Key_Z:
##            print 'Drag Key Pressed'
##            if self.pointerTypeGroup.checkedId() != self.scene.HandDrag:
##                print "Enabling Drag"
##                self.view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
##                self.view.setInteractive(False)
##                self.scene.setMode(self.pointerTypeGroup.checkedId())
##                event.accept()
##        super(MainWindow, self).keyPressEvent(event)
##
##    def keyReleaseEvent(self, event):
##        if event.key() == QtCore.Qt.Key_Z:
##            print 'Drag Key Released'
##            if self.pointerTypeGroup.checkedId() != self.scene.HandDrag:
##                print "Disabling Drag"
##                self.pointerGroupClicked(self.pointerTypeGroup.checkedId())
##                event.accept()
##        super(MainWindow, self).keyPressEvent(event)

    def pointerGroupClicked(self, i):
        if self.pointerTypeGroup.checkedId() == self.scene.SelectCells:
            self.view.setDragMode(QtGui.QGraphicsView.NoDrag)
            self.view.setInteractive(True)
            self.scene.setMode(self.pointerTypeGroup.checkedId())
            
        elif self.pointerTypeGroup.checkedId() == self.scene.RubberBand:
            self.view.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
            self.view.setInteractive(True)
            self.scene.setMode(self.pointerTypeGroup.checkedId())
            
        elif self.pointerTypeGroup.checkedId() == self.scene.HandDrag:
            self.view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self.view.setInteractive(False)
            #self.scene.setCellsSelectable(False)
            self.scene.setMode(self.pointerTypeGroup.checkedId())
            
        else:
            self.view.setDragMode(QtGui.QGraphicsView.NoDrag)
            self.view.setInteractive(True)
            self.scene.setMode(self.pointerTypeGroup.checkedId())


    def bringToFront(self):
        if len(self.scene.selectedItems()) == 0:
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if (item.zValue() >= zValue and
                isinstance(item, StarMap.MapItem)):
                zValue = item.zValue() + 0.1
        selectedItem.setZValue(zValue)

    def sendToBack(self):
        if len(self.scene.selectedItems()) == 0:
            return

        selectedItem = self.scene.selectedItems()[0]
        overlapItems = selectedItem.collidingItems()

        zValue = 0
        for item in overlapItems:
            if (item.zValue() <= zValue and
                isinstance(item, StarMap.MapItem)):
                zValue = item.zValue() - 0.1
        selectedItem.setZValue(zValue)

##    def itemInserted(self, item):
##        self.scene.setMode(self.pointerTypeGroup.checkedId())
##        self.buttonGroup.button(item.diagramType).setChecked(False)
##
##    def textInserted(self, item):
##        self.buttonGroup.button(InsertTextButton).setChecked(False)
##        self.scene.setMode(pointerTypeGroup.checkedId())

##    def currentFontChanged(self, font):
##        self.handleFontChange()
##
##    def fontSizeChanged(self, font):
##        self.handleFontChange()

    def wheelScrollZoom(self,  event):
        index = self.sceneScaleCombo.currentIndex()
        if event.delta() > 0:
            if index < 16:
                index = index + 1 
        elif event.delta() < 0:
            if index >0:
                index = index - 1
        self.sceneScaleCombo.setCurrentIndex(index)

    def sceneScaleChanged(self, scale):
        #newScale = scale.left(scale.indexOf("%")).toDouble()[0] / 100.0
        newScale = float(scale[0:scale.index('%')]) / 100.0
        #self.scene.rebuild(newScale)
        oldMatrix = self.view.matrix()
        self.view.resetMatrix()
        self.view.translate(oldMatrix.dx(), oldMatrix.dy())
        self.scene.setScale(newScale)
        self.view.scale(newScale, newScale)


    def projectManager(self):
        projectManager = ProjectManager.ProjectManager(self.model, self)
        # Run the project manager dialog to select a project
        # If valid project was selected and loaded into model, returns 1
        result = projectManager.exec_()
        app.processEvents()

        if result == 1:
            self.worldItemView = MapScene.WorldItemView(self.model)
            self.scene = self.worldItemView.scene

            self.view = MapView(self.scene)
            self.view.setRenderHints(QtGui.QPainter.Antialiasing)
            
            self.view.setScene(self.scene)
            self.view.changeZoomLevel.connect(self.wheelScrollZoom)
            self.pointerGroupClicked(1)
            self.sceneScaleCombo.setCurrentIndex(self.model.initialZoomLevel)
            self.sceneScaleChanged(self.sceneScaleCombo.currentText())
            self.view.horizontalScrollBar().setValue(self.model.horizontalScroll)
            self.view.verticalScrollBar().setValue(self.model.verticalScroll)
            self.selectionTypeCombo.setCurrentIndex(0)
            self.quickLinkCheckBox.setChecked(self.scene.quickLink)
            self.displayLinksCheckBox.setChecked(True)
            self.selectionTypeChanged(self.selectionTypeCombo.currentText())
            self.refreshRegionComboBox()
            
        elif result == 0:
            log.debug_log('Application closing. No project opened.')
            sys.exit()

# Some stuff left over from experimental MGT trade system support

        #self.model.worldLinks.testLinkChanged()
##    #@QtCore.pyqtSlot(str)
##    def setFromTradeWorld(self):
##        name = self.model.getWorld(self.model.fromTradeWorldPmi).name
##        self.tradeFromWorldName.setText(name)

##    def setToTradeWorld(self):
##        name = self.model.getWorld(self.model.toTradeWorldPmi).name
##        self.tradeToWorldName.setText(name)

    def generateCargo(self):
        pass
##        fromWorld = self.model.getWorld(self.model.fromTradeWorldPmi)
##        toWorld = self.model.getWorld(self.model.toTradeWorldPmi)
##        log.debug_log('Trade from ' + fromWorld.name + ' to ' + toWorld.name)
##        self.tradeDialog = Trade.TradeDialog(self.model, self.scene)
##        self.tradeDialog.show()
##        self.tradeDialog.activateWindow()
##        app.processEvents()

##    def openTradeDialog(self):
##        self.tradeDialog = Trade.MerchantDetailsDialog(self.model, self)
##        self.tradeDialog.show()
##        self.tradeDialog.activateWindow()
##        app.processEvents()

    def selectRegion(self, index):
        #if self.beginCreateRegion == False:
        self.scene.selectRegion(index)

    def createRegion(self):
        # Temporarily disable clearing of currently selected hexes
        #self.beginCreateRegion = True
        #ok = 0
        region_name, name_ok = QtGui.QInputDialog.getText(self, 'Crate New Region',
                                                'New Region Name:',
                                                QtGui.QLineEdit.Normal)
        if name_ok and region_name:
            added_ok = self.model.addNewHexRegion(str(region_name))
            #debug_log('App: New group "' + str(group_name) + '" added')
            if added_ok:
                self.refreshRegionComboBox()
                last_item = self.regionSelectionCombo.count() - 1
                self.regionSelectionCombo.setCurrentIndex(last_item)
        else:
            log.debug_log('App: Adding new region failed. Name: ' + str(region_name))
        #self.beginCreateRegion = False

    def updateRegion(self):
        index = self.regionSelectionCombo.currentIndex()
        if index != 0:
            self.scene.updateHexRegionIndex(index)

    def disbandRegion(self):
        index = self.regionSelectionCombo.currentIndex()
        self.model.disbandRegion(index)
        self.refreshRegionComboBox()

    def regionAdded(self, region_name):
        index = self.regionSelectionCombo.currentIndex()
        self.regionSelectionCombo.addItem(region_name)
        self.regionSelectionCombo.setCurrentIndex(index)

    def regionDisbanded(self, index):
        if index == self.regionSelectionCombo.currentIndex():
            self.regionSelectionCombo.setCurrentIndex(0)
        self.regionSelectionCombo.removeItem(index)   
        

    def refreshRegionComboBox(self):
        self.regionSelectionCombo.clear()
        self.regionSelectionCombo.addItems(self.model.hexRegionNames)


##    def refreshNetworkComboBox(self):
##        """Repopulate the network selecttion combo box in the networks toolbar"""
##        self.networkSelectionCombo.clear()
##        self.groupSelectionCombo.addItems(self.model.worldLinks.networkNames)

    def manageNetworks(self):
        self.networkManager = nm.NetworkManager(
            self.model.network_model, self)
        self.networkManager.show()
        self.networkManager.activateWindow()


    def save(self):
        self.model.storeZoomLevel(self.sceneScaleCombo.currentIndex())
        h = self.view.horizontalScrollBar().value()
        v = self.view.verticalScrollBar().value()
        self.model.storeHorizontalScroll(h)
        self.model.storeVerticalScroll(v)
        self.model.save()

    def about(self):
        QtGui.QMessageBox.about(self, ("About StarBase"),
            ("<b>StarBase</b>, the science fiction star mapping application by Simon D. Hibbs."))


    def createActions(self):

        # File Menu actions
        projectManagerAction = QtGui.QAction(QtGui.QIcon(":/images/undefined.png"),
                                    "&Project Manager", self)
        projectManagerAction.setShortcut("Ctrl+M")
        projectManagerAction.setStatusTip("Open the Project Manager")
        projectManagerAction.triggered.connect(self.projectManager)
        self.projectManagerAction = projectManagerAction
        
        saveWorldDataAction = QtGui.QAction(QtGui.QIcon(":/images/undefined.png"),
                                    "&Save World Data", self)
        saveWorldDataAction.setShortcut("Ctrl+S")
        saveWorldDataAction.setStatusTip("Save the World Data")
        saveWorldDataAction.triggered.connect(self.save)
        self.saveWorldDataAction = saveWorldDataAction


        worldBrowserAction = QtGui.QAction(QtGui.QIcon(":/images/undefined.png"),
                                    "&World Browser", self)
        worldBrowserAction.setShortcut("Ctrl+W")
        worldBrowserAction.setStatusTip("Open the World Browser")
        worldBrowserAction.triggered.connect(self.openWorldBrowser)
        self.worldBrowserAction = worldBrowserAction

        ###
        sectorBrowserAction = QtGui.QAction(QtGui.QIcon(":/images/undefined.png"),
                                    "&Sector Browser", self)
        sectorBrowserAction.setShortcut("Ctrl+W")
        sectorBrowserAction.setStatusTip("Open the Sector Browser")
        sectorBrowserAction.triggered.connect(self.openSectorBrowser)
        self.sectorBrowserAction = sectorBrowserAction

        subsectorBrowserAction = QtGui.QAction(QtGui.QIcon(":/images/undefined.png"),
                                    "S&ubsector Browser", self)
        subsectorBrowserAction.setShortcut("Ctrl+W")
        subsectorBrowserAction.setStatusTip("Open the Subsector Browser")
        subsectorBrowserAction.triggered.connect(self.openSubsectorBrowser)
        self.subsectorBrowserAction = subsectorBrowserAction

	###
        allegianceEditorAction = QtGui.QAction(QtGui.QIcon(":/images/undefined.png"),
                                    "Allegiance Colors", self)
        allegianceEditorAction.setShortcut("Ctrl+A")
        allegianceEditorAction.setStatusTip("Open the Allegiance Editor")
        allegianceEditorAction.triggered.connect(self.openAllegianceEditor)
        self.allegianceEditorAction =  allegianceEditorAction

        exitAction = QtGui.QAction("E&xit", self)
        exitAction.setShortcut("Ctrl+X")
        exitAction.setStatusTip("Quit StarBase")
        exitAction.triggered.connect(self.close)
        self.exitAction = exitAction

        aboutAction = QtGui.QAction("A&bout", self)
        aboutAction.setShortcut("Ctrl+B")
        aboutAction.triggered.connect(self.about)
        self.aboutAction = aboutAction

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        #self.fileMenu.addAction(self.projectManagerAction)
        self.fileMenu.addAction(self.saveWorldDataAction)
        self.fileMenu.addAction(self.exitAction)

        self.configMenu = self.menuBar().addMenu("&Config")
        self.configMenu.addAction(self.allegianceEditorAction)

##        self.itemMenu = self.menuBar().addMenu("&Item")
##        self.itemMenu.addAction(self.addWorldAction)
##        self.itemMenu.addAction(self.deleteWorldAction)
##
##        self.dataMenu = self.menuBar().addMenu("&Data")
##        self.dataMenu.addAction(self.worldBrowserAction)
##        self.dataMenu.addAction(self.subsectorBrowserAction)
##        self.dataMenu.addAction(self.sectorBrowserAction)
        
        self.aboutMenu = self.menuBar().addMenu("&Help")
        self.aboutMenu.addAction(self.aboutAction)

    def createToolbars(self):
        # Pointers
        self.selectionTypeCombo = QtGui.QComboBox()
        self.selectionTypeCombo.setToolTip('Sets the type of map items that will be selected.')
        selectionTypes = ['Hexes', 'Subsectors', 'Sectors']
        self.selectionTypeCombo.addItems(selectionTypes)
        self.selectionTypeCombo.currentIndexChanged[str].connect(self.selectionTypeChanged)
        
        pointerButton = QtGui.QToolButton()
        pointerButton.setToolTip('Select Mode.\nClick on map items to select them.')
        pointerButton.setCheckable(True)
        pointerButton.setChecked(True)
        pointerButton.setIcon(QtGui.QIcon(":/images/pointer.png"))

        rubberBandPointerButton = QtGui.QToolButton()
        rubberBandPointerButton.setCheckable(True)
        rubberBandPointerButton.setIcon(QtGui.QIcon(":/images/rubber_band.png"))
        
        handDragPointerButton = QtGui.QToolButton()
        handDragPointerButton.setToolTip('Hand Drag Mode.\nClick and drag on the map to move the view.')
        handDragPointerButton.setCheckable(True)
        handDragPointerButton.setIcon(QtGui.QIcon(":/images/grab_hand.png"))

        pointerTypeGroup = QtGui.QButtonGroup()
        pointerTypeGroup.addButton(pointerButton,
                                    int(MapScene.MapScene.SelectCells))
        pointerTypeGroup.addButton(rubberBandPointerButton,
                                    int(MapScene.MapScene.RubberBand))
        pointerTypeGroup.addButton(handDragPointerButton,
                                    int(MapScene.MapScene.HandDrag))
        pointerTypeGroup.buttonClicked[int].connect(self.pointerGroupClicked)
        self.pointerTypeGroup = pointerTypeGroup

        quickLinkCheckBox = QtGui.QCheckBox('QuickLink')
        quickLinkCheckBox.setToolTip('Whenever two worlds are selected,\nthe Edit Link dialog will open automaticaly.')
        quickLinkCheckBox.setChecked(False)
        quickLinkCheckBox.stateChanged[int].connect(self.toggleQuickLink)
        self.quickLinkCheckBox = quickLinkCheckBox

        self.sceneScaleCombo = QtGui.QComboBox()
        self.sceneScaleCombo.setToolTip('Show/Select the map zoom level.')
        #scales = ["3%","6%","12%","25%", "50%", "65%", "75%", "100%", "133%", "200%"]
        scales = ['3%', '5%', '8%', '12%', '18%', '25%', '37%', '50%', '60%', '70%', \
                   '80%', '90%', '100%', '120%', '140%', '160%', '200%']
        self.sceneScaleCombo.addItems(scales)
        self.sceneScaleCombo.currentIndexChanged[str].connect(self.sceneScaleChanged)

        pointerToolbar = self.addToolBar("Pointer type")
        pointerToolbar.addWidget(QtGui.QLabel('Edit Mode:  '))
        pointerToolbar.addWidget(self.selectionTypeCombo)
        pointerToolbar.addWidget(QtGui.QLabel('   Pointer Mode: '))
        pointerToolbar.addWidget(pointerButton)
        #pointerToolbar.addWidget(rubberBandPointerButton)
        pointerToolbar.addWidget(handDragPointerButton)
        pointerToolbar.addWidget(quickLinkCheckBox)
        pointerToolbar.addWidget(QtGui.QLabel(' Zoom level: '))
        pointerToolbar.addWidget(self.sceneScaleCombo)
        self.pointerToolbar = pointerToolbar

        occurrenceSpinBox = OccurrenceSpinBoxPC()
        occurrenceSpinBox.setToolTip('Increase or decreates the chance a hex contains a world.')
        #self.connect(occurrenceSpinBox,
        #             QtCore.SIGNAL("valueChanged(int)"),
        #             self.setWorldOccurrenceDM)
        occurrenceSpinBox.valueChanged[int].connect(self.setWorldOccurrence)
        worldsToolbar = self.addToolBar("Worlds Toolbar")
        worldsToolbar.addWidget(QtGui.QLabel('World Occurrence:  '))
        worldsToolbar.addWidget(occurrenceSpinBox)
        
        autoNameCheckBox = QtGui.QCheckBox('AutoName')
        autoNameCheckBox.setToolTip('World names are randomly chosen from a list,\ninstead of based on their grid coordinates.')
        autoNameCheckBox.setChecked(self.model.auto_name)
        autoNameCheckBox.stateChanged[int].connect(self.toggleAutoName)
        worldsToolbar.addWidget(autoNameCheckBox)
        
        self.worldsToolbar = worldsToolbar

        allegianceToolbar = self.addToolBar("Allegiance Toolbar")
        self.manageAllegiancesButton = QtGui.QPushButton("Manage Allegiances")
        self.manageAllegiancesButton.setToolTip('Open the Allegiance Manager.\n' +\
                                                'Create, Delete and modify the attributes of world allegiances.')
        self.manageAllegiancesButton.clicked.connect(self.openAllegianceEditor)
        allegianceToolbar.addWidget(self.manageAllegiancesButton)
        allegianceCheckBox = QtGui.QCheckBox('Display Allegiances')
        allegianceCheckBox.setToolTip('Colours hex backgrounds to indicate the world allegiance.')
        allegianceCheckBox.stateChanged[int].connect(self.toggleAllegianceDisplay)
        allegianceToolbar.addWidget(allegianceCheckBox)

        self.allegianceToolbar = allegianceToolbar

        self.addToolBarBreak()

        regionToolbar = self.addToolBar("Region Toolbar")
        regionToolbar.addWidget(QtGui.QLabel('Select Hex Region: '))
        self.regionSelectionCombo = QtGui.QComboBox()
        self.regionSelectionCombo.setToolTip("Selects all the hexes in a Region.\n" +\
                                            "The current hex selection can then be changed, but the Region itself\n" +\
                                            "is not updated unless/until you click the 'Update' button.")
        self.regionSelectionCombo.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        #self.groupSelectionCombo.currentIndexChanged[int].connect(self.selectGroup)
        self.regionSelectionCombo.currentIndexChanged[int].connect(self.selectRegion)
        regionToolbar.addWidget(self.regionSelectionCombo)
        
        self.createRegionButton = QtGui.QPushButton('New (empty)')
        self.createRegionButton.setToolTip('Create a new, empty Region.')
        self.createRegionButton.clicked.connect(self.createRegion)
        regionToolbar.addWidget(self.createRegionButton)

        self.updateRegionButton = QtGui.QPushButton('Update')
        self.updateRegionButton.setToolTip('Assigns the currently selected hexes to the current Region')
        self.updateRegionButton.clicked.connect(self.updateRegion)
        regionToolbar.addWidget(self.updateRegionButton)
        
        self.disbandRegionButton = QtGui.QPushButton('Disband')
        self.disbandRegionButton.setToolTip('Deletes the currently selected Region.\n' +\
                                           'The hexes/worlds themselves are not affected.')
        self.disbandRegionButton.clicked.connect(self.disbandRegion)
        regionToolbar.addWidget(self.disbandRegionButton)


        networksToolbar = self.addToolBar("Networks Toolbar")
        self.manageNetworksButton = QtGui.QPushButton('Manage Networks')
        self.manageNetworksButton.setToolTip('Open the Network Manager.\n' +\
                                             'Create, Delete and modify the attributes of network link types.')
        self.manageNetworksButton.clicked.connect(self.manageNetworks)
        networksToolbar.addWidget(self.manageNetworksButton)
        
        self.displayLinksCheckBox = QtGui.QCheckBox('Display Links')
        self.displayLinksCheckBox.setToolTip('Displays or hides all network links.')
        self.displayLinksCheckBox.stateChanged[int].connect(self.toggleDisplayNetworkLinks)
        networksToolbar.addWidget(self.displayLinksCheckBox)


##        self.tradeFromWorldName = QtGui.QLineEdit()
##        self.tradeFromWorldName.setMaximumWidth(100)
##        self.tradeFromWorldName.setReadOnly(True)
##        
##        self.tradeToWorldName = QtGui.QLineEdit()
##        self.tradeToWorldName.setMaximumWidth(100)
##        self.tradeToWorldName.setReadOnly(True)
##        
##        #self.generateCargoButton = QtGui.QPushButton('Generate Cargo')
##        self.tradeButton = QtGui.QPushButton('Trade')
##
##        tradeToolbar = self.addToolBar("Trade Toolbar")
##        tradeToolbar.addWidget(QtGui.QLabel('Trade From:'))
##        tradeToolbar.addWidget(self.tradeFromWorldName)
##        tradeToolbar.addWidget(QtGui.QLabel('To:'))
##        tradeToolbar.addWidget(self.tradeToWorldName)
##        #tradeToolbar.addWidget(self.generateCargoButton)
##        tradeToolbar.addWidget(self.tradeButton)
##
##        self.tradeToolbar = tradeToolbar


    def createBackgroundCellWidget(self, text, image):
        button = QtGui.QToolButton()
        button.setText(text)
        button.setIcon(QtGui.QIcon(image))
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.backgroundButtonGroup.addButton(button)

        layout = QtGui.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtGui.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        return widget

    def createCellWidget(self, text, diagramType):
        item = StarMap.MapItem(diagramType, self.dataMenu)
        icon = QtGui.QIcon(item.image())

        button = QtGui.QToolButton()
        button.setIcon(icon)
        button.setIconSize(QtCore.QSize(50, 50))
        button.setCheckable(True)
        self.buttonGroup.addButton(button, diagramType)

        layout = QtGui.QGridLayout()
        layout.addWidget(button, 0, 0, QtCore.Qt.AlignHCenter)
        layout.addWidget(QtGui.QLabel(text), 1, 0, QtCore.Qt.AlignCenter)

        widget = QtGui.QWidget()
        widget.setLayout(layout)

        return widget

    def createColorMenu(self, slot, defaultColor):
        colors = [QtCore.Qt.black, QtCore.Qt.white, QtCore.Qt.red, QtCore.Qt.blue, QtCore.Qt.yellow]
        names = ["black", "white", "red", "blue", "yellow"]

        colorMenu = QtGui.QMenu(self)
        for color, name in zip(colors, names):
            action = QtGui.QAction(name, self)
            #need to specifically create a QColor from "color", since the "color" is a GlobalColor
            # and not a QColor object
            action.setData(QtGui.QColor(color))
            #action.setData(QtCore.QVariant(QtGui.QColor(color)))
            action.setIcon(self.createColorIcon(color))
            self.connect(action, QtCore.SIGNAL("triggered()"), slot)
            colorMenu.addAction(action)
            if color == defaultColor:
                colorMenu.setDefaultAction(action)
        return colorMenu

    def createColorToolButtonIcon(self, imageFile, color):
        pixmap = QtGui.QPixmap(50, 80)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        image = QtGui.QPixmap(imageFile)
        target = QtCore.QRect(0, 0, 50, 60)
        source = QtCore.QRect(0, 0, 42, 42)
        painter.fillRect(QtCore.QRect(0, 60, 50, 80), color)
        painter.drawPixmap(target, image, source)
        painter.end()
        return QtGui.QIcon(pixmap)

    def setScrollHandDragAction(self):
        self.view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)

    def setRubberBandDragAction(self):
        self.view.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

    def createColorIcon(self, color):
        pixmap = QtGui.QPixmap(20, 20)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtCore.Qt.NoPen)
        painter.fillRect(QtCore.QRect(0, 0, 20, 20), color)
        painter.end()
        return QtGui.QIcon(pixmap)

    def openAllegianceEditor(self):
        self.allegianceEditor = AllegianceEditor.AllegianceEditor(
            self.model, self.scene, self)
        self.allegianceEditor.show()
        self.allegianceEditor.activateWindow()
        #app.processEvents()
        

    def openWorldBrowser(self):
        self.worldBrowser = WorldBrowser.WorldBrowser(self.model, self)
        #worldBrowser.exec_()
        self.worldBrowser.show()
        #worldBrowser.raise()
        self.worldBrowser.activateWindow()
        
        app.processEvents()
    
    def openSectorBrowser(self):
        sectorBrowser = SectorBrowser.SectorBrowser(sector_model)
        sectorBrowser.exec_()
        app.processEvents()
    
    def openSubsectorBrowser(self):
        subsectorBrowser = SubsectorBrowser.SubsectorBrowser(subsector_model)
        subsectorBrowser.exec_()
        app.processEvents()

    def closeEvent(self, event=QtGui.QCloseEvent()):
        saveDialog = QtGui.QMessageBox()
        saveDialog.setText('Do you want to save any changes before exiting?')
        saveDialog.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)
        saveDialog.setDefaultButton(QtGui.QMessageBox.Save)
        ret = saveDialog.exec_()
        if ret == QtGui.QMessageBox.Save:
            self.save()
            log.debug_log('If built using PySide it takes a while to exit, be patient.')
            event.accept()
        elif ret == QtGui.QMessageBox.Discard:
            log.debug_log('If built using PySide it takes a while to exit, be patient.')
            event.accept()
        elif ret == QtGui.QMessageBox.Cancel:
            event.ignore()
            app.processEvents()
            
            
        


if __name__ == "__main__":

    log.info_log("=== Application Started ===")
    app = QtGui.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.setGeometry(100, 100, 1000, 600)
    mainWindow.show()

    sys.exit(app.exec_())
