# Copyright 2013 Simon Dominic Hibbs
from PySide.QtCore import *
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PySide.QtGui import *
#from PyQt4.QtSvg import *
import os
from model import Models
from starmap import MapGlyphs
from starmap import MapGrid

SUBSECTOR = 1
SECTOR = 2

class BoundaryRectangle(QGraphicsPolygonItem):
    def __init__(self, rectF=QRectF(), parent=None):
        QGraphicsPolygonItem.__init__(self, parent)
        self.rectF = rectF
        pen = QPen()
        pen.setWidth(2)
        self.setPen(pen)
        self.setBrush(Qt.transparent)
        myPolygon = QPolygonF(rectF)
        self.setPolygon(myPolygon)
        self.myPolygon = myPolygon
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def boundingRect(self):
        return self.rectF




class PreviewDialog(QDialog):
    def __init__(self, glyph,  region_type,  map_scene, parent=None):
        super(PreviewDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Preview Map')
        
        self.region_type = region_type
        self.glyph = glyph

        self.map_scene = map_scene

        if self.region_type == SUBSECTOR:
            self.base_scale = 0.5
        elif self.region_type == SECTOR:
            self.base_scale = 0.25

        self.display_image = self.getMapImage(2)
        
        
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setPixmap(QPixmap.fromImage(self.display_image))
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        #self.scrollArea.setWidgetResizable(True)

        zoomInButton = QPushButton('Zoom In (25%)')
        zoomOutButton = QPushButton('Zoom Out (25%)')
        normalSizeButton = QPushButton('Normal Size')
        printButton = QPushButton('Print')
        pngButton = QPushButton('Save As PNG')
##        svgButton = QPushButton('Save As SVG')
        closeButton = QPushButton('Close')
        #self.fitToWindowCB = QCheckBox('Fit To Window')
        self.decorateCB = QCheckBox('Decorate')

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(zoomInButton)
        buttonLayout.addWidget(zoomOutButton)
        buttonLayout.addWidget(normalSizeButton)
        buttonLayout.addWidget(printButton)
        buttonLayout.addWidget(pngButton)
##        buttonLayout.addWidget(svgButton)
        buttonLayout.addWidget(closeButton)
        buttonLayout.addStretch()
        #buttonLayout.addWidget(self.fitToWindowCB)
        buttonLayout.addWidget(self.decorateCB)

        layout = QHBoxLayout()
        layout.addWidget(self.scrollArea)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        zoomInButton.clicked.connect(self.zoomIn)
        zoomOutButton.clicked.connect(self.zoomOut)
        normalSizeButton.clicked.connect(self.normalSize)
        
        printButton.clicked.connect(self.printMap)
        pngButton.clicked.connect(self.saveMapPNG)
        closeButton.clicked.connect(self.closeDialog)

        printButton.setEnabled(False)

        self.createActions()

        #self.fitToWindowCB.toggled.connect(self.fitToWindowAct.setChecked)
        #self.fitToWindowAct.toggled.connect(self.fitToWindowCB.setChecked)

        #self.fitToWindowCB.toggled.connect(self.fitToWindow)

        self.decorateCB.setChecked(True)
        #self.fitToWindowCB.setChecked(False)

        #self.resize(400, 500)
        self.scaleImage(self.base_scale)
        


    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = self.base_scale
        self.scaleImage(1.0)

##    def fitToWindow(self):
##        fitToWindow = self.fitToWindowAct.isChecked()
##        self.scrollArea.setWidgetResizable(fitToWindow)
##        if not fitToWindow:
##            self.normalSize()
##
##        self.updateActions()

    def fitToWindow(self, toggle):
        self.scrollArea.setWidgetResizable(self.fitToWindowCB.isChecked())
        if not self.fitToWindowCB.isChecked():
            self.normalSize()
            #self.imageLabel.adjustSize()

        self.updateActions()

        
    def getMapImage(self, scale):
        draw_subsectors = False
        if self.region_type == SUBSECTOR:
            image_width = 800 * scale   # 1668
            image_height = 1050 * scale  # 2106
            filename = 'Subsector.png'
            border_width = 2
        elif self.region_type == SECTOR:
            #image_width = 3336
            #image_height = 4212
            image_width = 3150 * scale
            image_height = 4000 * scale
            filename = 'Sector.png'
            border_width = 2
            draw_subsectors = True

        # Temporarily disable drawing of the boundary polys
        self.map_scene.displaySectorGrid(False)
        self.map_scene.displaySubsectorGrid(False)

        self.source_rect = self.glyph.mapToScene(self.glyph.boundary_glyph.regionRect()).boundingRect()
        self.target_rect = QRectF(0, 0, image_width, image_height)

        # Temporarily set the region glyph to transparent
        self.glyph.itemChange("Snapshot", False)


        self.scaleFactor = self.base_scale
        image = QImage(image_width, image_height, QImage.Format_ARGB32_Premultiplied)
        image.fill(0)
        
        painter = QPainter()
        painter.begin(image)
        #painter.setBackgroundMode(Qt.OpaqueMode)
        #painter.setRenderHint(QPainter.Antialiasing)
        #painter.setBackgroundMode(Qt.TransparentMode)
        self.map_scene.render(painter, self.target_rect, self.source_rect, Qt.AspectRatioMode.KeepAspectRatio)

        painter.setPen(QPen(Qt.black, border_width))
        painter.drawRect(self.target_rect)

        if draw_subsectors:
            sub_width = image_width / 4
            # Why (image_height - 60) ? Possibly due to 5 point border drawn round sector glyphs
            sub_height = (image_height - 60) / 4
            for num in [1, 2, 3]:
                painter.drawLine(sub_width * num, 0, sub_width * num, image_height)
                painter.drawLine(0, sub_height * num, image_width, sub_height * num)

        painter.end()
        
        # Re-Enable drawing of the boundary polys
        self.map_scene.displaySectorGrid(True)
        self.map_scene.displaySubsectorGrid(True)
        # Set the region glyph back to the selection style
        self.glyph.itemChange("Snapshot", True)
        self.glyph.setSelected(True)

        return image


    def createActions(self):
        #self.fitToWindowAct = QAction("&Fit to Window", self,
        #        enabled=False, checkable=True, shortcut="Ctrl+F",
        #        triggered=self.fitToWindow)
        
        self.zoomInAct = QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)
        
        self.normalSizeAct = QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)
        

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowCB.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowCB.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowCB.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        #self.zoomInAct.setEnabled(self.scaleFactor < 1.0)
        #self.zoomOutAct.setEnabled(self.scaleFactor > 0.1)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))


    def saveMapPNG(self):

        name = self.glyph.name
        default_path = os.path.join(self.map_scene.model.project_path,
                                    self.map_scene.model.slugify(name)) + \
                                    '.png'
        filename, filetype = QFileDialog.getSaveFileName(self, 'Save As PNG',
                                               default_path,
                                               'PNG Files (*.png)')

        #print filename
        self.display_image.save(filename, 'PNG', -1)


    def closeDialog(self):
        QDialog.done(self, 0)



###############

    def showName(self, flag):
        pass


# Doesn't work yet
    def printMap(self, image):
        if self.region_type == SUBSECTOR:
            filename = 'Subsector.pdf'
        elif self.region_type == SECTOR:
            filename = 'Sector.pdf'
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A4)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        
        painter = QPainter(printer)
        painter.setBackgroundMode(Qt.OpaqueMode)
        painter.setBrush(Qt.SolidPattern)
        self.scene.render(painter)
        painter.end()
        
        printDialog = QPrintDialog(printer, self)
        printDialog.setWindowTitle('Print Subsector Map')
        if printDialog.exec_() == QDialog.Accepted:
            painter.begin(printer)
            painter.save()
            painter.restore()
            painter.end()







#################
##
##    def redrawMap(self, flag):
##
##        if flag == Qt.Checked:
##
##            self.scene.clear()
##            self.scene.setBackgroundBrush(Qt.white)
##            self.scene.model = self.model
##            self.grid = PreviewGridRoot(self.glyph,
##                                        self.region_type,
##                                        self.model)
##            self.scene.addItem(self.grid)
##            self.grid.setCoordsVisible(True)
##            self.view.setScene(self.scene)
##
##            #self.mapRect = self.scene.sceneRect()
##            #self.mapRect.adjust(-30, -0, -10, 0)
##            #rect = self.mapRect.toRect()
##            #self.view.setGeometry(rect)
##            self.grid.addBorder(self.mapRect)
##
##            if self.region_type == SUBSECTOR:
##                self.view.scale(0.6, 0.6)
##                subX = self.glyph.subsectorCol
##                subY = self.glyph.subsectorRow
##                north = self.model.getSubsectorAt(subX, subY - 1)
##                east = self.model.getSubsectorAt(subX + 1, subY)
##                south = self.model.getSubsectorAt(subX, subY + 1)
##                west = self.model.getSubsectorAt(subX - 1, subY)
##                name = self.glyph.name
##                fontsize = 12
##            elif self.region_type == SECTOR:
##                self.view.scale(0.5, 0.5)
##                secX = self.glyph.sectorCol
##                secY = self.glyph.sectorRow
##                north = self.model.getSectorAt(secX, secY - 1)
##                east = self.model.getSectorAt(secX + 1, secY)
##                south = self.model.getSectorAt(secX, secY + 1)
##                west = self.model.getSectorAt(secX - 1, secY)
##                name = self.glyph.name
##                fontsize = 50
##
##            self.north_text = QGraphicsSimpleTextItem(north)
##            self.scene.addItem(self.north_text)
##            self.north_text.setFont(QFont('Helvetica', fontsize, QFont.Bold))
##            woffset = self.north_text.boundingRect().width()/2
##            hoffset = self.north_text.boundingRect().height()
##            self.north_text.setBrush(Qt.black)
##            self.north_text.setPos((self.mapRect.width() / 2) - woffset - 70,
##                                   -55 - hoffset)
##
##            self.east_text = QGraphicsSimpleTextItem(east)
##            self.scene.addItem(self.east_text)
##            self.east_text.setFont(QFont('Helvetica', fontsize, QFont.Bold))
##            woffset = self.east_text.boundingRect().width()/2
##            hoffset = self.east_text.boundingRect().height()
##            self.east_text.setBrush(Qt.black)
##            self.east_text.setRotation(+90)
##            self.east_text.setPos(self.mapRect.width() - 55 + hoffset,
##                                  (self.mapRect.height() / 2) - woffset - 45)
##
##            self.south_text = QGraphicsSimpleTextItem(south)
##            self.scene.addItem(self.south_text)
##            self.south_text.setFont(QFont('Helvetica', fontsize, QFont.Bold))
##            woffset = self.south_text.boundingRect().width()/2
##            name_offset = self.south_text.boundingRect().height()
##            self.south_text.setBrush(Qt.black)
##            self.south_text.setPos((self.mapRect.width() / 2) - woffset - 70,
##                                   self.mapRect.height() - 45 + 0)
##
##            self.west_text = QGraphicsSimpleTextItem(west)
##            self.scene.addItem(self.west_text)
##            self.west_text.setFont(QFont('Helvetica', fontsize, QFont.Bold))
##            woffset = self.west_text.boundingRect().width()/2
##            hoffset = self.west_text.boundingRect().height()
##            self.west_text.setBrush(Qt.black)
##            self.west_text.setRotation(-90)
##            self.west_text.setPos(-75 - hoffset,
##                                  (self.mapRect.height() / 2) + woffset - 45)
##
##            self.name_text = QGraphicsSimpleTextItem(name)
##            self.scene.addItem(self.name_text)
##            self.name_text.setFont(QFont('Helvetica', fontsize * 2, QFont.Bold))
##            woffset = self.name_text.boundingRect().width()/2
##            self.name_text.setBrush(Qt.black)
##            self.name_text.setPos((self.mapRect.width() / 2) - woffset - 70,
##                                   self.mapRect.height() - 35 + name_offset)
##
##            self.update()
##
##        else:
##            self.scene.clear()
##            self.scene.setBackgroundBrush(Qt.white)
##            self.scene.model = self.model
##            self.grid = PreviewGridRoot(self.glyph,
##                                        self.region_type,
##                                        self.model)
##            self.scene.addItem(self.grid)
##            self.grid.setCoordsVisible(True)
##            #self.view.setScene(self.scene)
##
##            #self.mapRect = self.scene.sceneRect()
##            #self.mapRect.adjust(-30, -0, -10, 0)
##            #rect = self.mapRect.toRect()
##            #self.view.setGeometry(rect)
##            self.grid.addBorder(self.mapRect)
##
##            self.update()
##


