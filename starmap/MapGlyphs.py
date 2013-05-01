# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PySide import QtCore, QtGui
import math
import binascii
from model import Models
from model import Foundation
#import WorldDialogs
from log import *

CELLSIZE = 100
HEX_DELTA = float(abs(math.tan(math.radians(30))) * 25.0)

userType = QtGui.QGraphicsItem.UserType

SECTOR_ROOT_TYPE = userType
SUBSECTOR_ROOT_TYPE = userType + 1
HEX_ROOT_TYPE = userType +2
GRID_TYPE = userType + 3

SECTOR_RECTANGLE_TYPE = userType + 4
SECTOR_GLYPH_TYPE = userType + 5
SUBSECTOR_RECTANGLE_TYPE = userType + 6
SUBSECTOR_GLYPH_TYPE = userType + 7
GRID_HEX_TYPE = userType + 8
GRID_CELL_TYPE = userType + 9
PLANET_CIRCLE_TYPE = userType + 10
PLANET_GLYPH_TYPE = userType + 11
TZ_CIRCLE_TYPE = userType + 12
GAS_GIANT_TYPE = userType + 13
GAS_GIANT_RING_TYPE = userType + 14
BASE_GLYPH_TYPE = userType + 15

WEB_ROOT_TYPE = userType + 16
NETWORK_ROOT_TYPE = userType + 17
LINK_LINE_TYPE = userType + 18

def gridToPix(gx, gy):
    px = CELLSIZE * gx
    py = CELLSIZE * gy
    if gx%2 != 0:
        py += CELLSIZE / 2.0
    return int(px), int(py)

def gridToHEX(gx, gy):
    # Convert x,y coords to H,E,X three-axis coordinates
    H = int(math.floor( 2.0 * gy))
    E = int(math.floor(math.sqrt(3.0) * gx - gy))
    X = int(math.floor(math.sqrt(3.0) * gx + gy))
    return H, E, X

def targetXY(angle, distance):
    theta = math.radians(angle)
    dx = distance * math.cos(theta)
    dy = distance * math.sin(theta)
    return dx, dy

# deprecated
##def gridToSecRelText(gx, gy):
##    xtext = str((gx % 32) + 1).zfill(2)
##    ytext = str((gy % 40) + 1).zfill(2)
##    return xtext + ytext



class SectorRectangle(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsPolygonItem.__init__(self, parent)
        self._type = SECTOR_RECTANGLE_TYPE
        self.border_width = 5
        pen = QtGui.QPen()
        pen.setWidth(self.border_width)
        #pen.setColor(QtCore.Qt.darkGray)
        self.setPen(pen)
        self.setBrush(QtCore.Qt.transparent)
        # 0,0 is the centre of the top-left hex in the sector
        myPolygon = QtGui.QPolygonF([
                    QtCore.QPointF(-50, -50), QtCore.QPointF(3150, -50),
                    QtCore.QPointF(3150,3950), QtCore.QPointF(-50, 3950),
                    QtCore.QPointF(-50, -50)])
        self.setPolygon(myPolygon)
        self.myPolygon = myPolygon
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)

    @property
    def itemType(self):
        return self._type

    def image(self):
        pixmap = QtGui.QPixmap(250, 250)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)
        return pixmap

    def regionRect(self):
        # Includes the bottom half of the bottom row of hexes
        return QtCore.QRectF(-50, -50, 3200, 4050)

    def boundingRect(self):
        offset = self.border_width / 2
        return QtCore.QRectF(-50 - offset, -50 - offset,
                             3200 + offset, 4000 + offset)


class SectorGlyph(QtGui.QGraphicsItem):
    def __init__(self, col, row, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        self._type = SECTOR_GLYPH_TYPE
        self.boundary_glyph = SectorRectangle(self)
        self.sectorCol = col
        self.sectorRow = row
        self.cells = []
        
        self.name_text = QtGui.QGraphicsSimpleTextItem(self)
        self.name_text.hide()
        self.name_text.setFont(QtGui.QFont('Helvetica', 250, QtGui.QFont.Bold))
        self.name_text.setBrush(QtCore.Qt.darkGray)
        self.setName('Unknown')

    @property
    def itemType(self):
        return self._type

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        return self.boundary_glyph.boundingRect()

    def setName(self, name):
        self.name = name
        self.name_text.setText(name)
        offset = -1.0 * (self.name_text.boundingRect().width()/2)
        self.name_text.setPos((offset + 1550), 1740.0)

    def showName(self, flag):
        self.name_text.setVisible(flag)

    def itemChange(self, change, value):
        #Temporary feature to test cell selection/display
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged or change == "Snapshot":
            if value == True:
                self.boundary_glyph.setBrush(QtCore.Qt.lightGray)
                self.boundary_glyph.setOpacity(0.7)
            else:
                self.boundary_glyph.setBrush(QtCore.Qt.transparent)
        else:
            #print 'NoSelectionChange'
            return value



class SubSectorRectangle(QtGui.QGraphicsPolygonItem):
    def __init__(self, parent=None):
        QtGui.QGraphicsPolygonItem.__init__(self, parent)
        self._type = SUBSECTOR_RECTANGLE_TYPE
        pen = QtGui.QPen()
        pen.setWidth(2)
        #pen.setColor(QtCore.Qt.darkGray)
        self.setPen(pen)
        self.setBrush(QtCore.Qt.transparent)
        # 0,0 is the centre of the top-left hex in the sector
        left = -50; right = 750
        top = -50; bottom = 950
        myPolygon = QtGui.QPolygonF([
                    QtCore.QPointF(left, top), QtCore.QPointF(right, top),
                    QtCore.QPointF(right,bottom), QtCore.QPointF(left, bottom),
                    QtCore.QPointF(left, top)])
        self.setPolygon(myPolygon)
        self.myPolygon = myPolygon
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)

    @property
    def itemType(self):
        return self._type

    def regionRect(self):
        # Includes the bottom half of the bottom row of hexes
        return QtCore.QRectF(-50, -50, 800, 1050)

    def boundingRect(self):
        return QtCore.QRectF(-50, -50, 800, 1000)

    def hexRect(self):
        base_rect = self.boundingRect()
        


class SubSectorGlyph(QtGui.QGraphicsItemGroup):
    def __init__(self, col, row, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        self._type = SUBSECTOR_GLYPH_TYPE
        self.boundary_glyph = SubSectorRectangle(self)
        self.subsectorCol = col
        self.subsectorRow = row
        self.cells = []
        
        self.name_text = QtGui.QGraphicsSimpleTextItem(self)
        self.name_text.hide()
        self.name_text.setFont(QtGui.QFont('Helvetica', 50, QtGui.QFont.Bold))
        self.name_text.setBrush(QtGui.QColor(85,85,85,170))
        self.setName('Unknown')

    @property
    def itemType(self):
        return self._type

    def setName(self, name):
        self.name = name
        self.name_text.setText(name)
        offset = -1.0 * (self.name_text.boundingRect().width()/2)
        self.name_text.setPos((offset + 350), 410.0)

    def showName(self, flag):
        self.name_text.setVisible(flag)

    def itemChange(self, change, value):
        #Temporary feature to test cell selection/display
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged or change == "Snapshot":
            if value == True:
                self.boundary_glyph.setBrush(QtCore.Qt.lightGray)
                self.boundary_glyph.setOpacity(0.7)
            else:
                self.boundary_glyph.setBrush(QtCore.Qt.transparent)
        else:
            #print 'NoSelectionChange'
            return value


class LinkLine(QtGui.QGraphicsLineItem):
    # links are of the form ((col1, row1), (col2, row2))
    # Links in either direction are considered identical
    def __init__(self, parent=None):
        QtGui.QGraphicsLineItem.__init__(self, parent)
        self._type = LINK_LINE_TYPE
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setWidth(5)
        self.setPen(pen)

    def setColor(self, color):
        #pass
        #print color
        pen = self.pen()
        pen.setColor(QtGui.QColor(color))
        self.setPen(pen)

    def setStyle(self, style):
        pen = self.pen()
        pen.setStyle(style)
        self.setPen(pen)

    def drawLine(self, px1, py1, px2, py2, count):
        line = QtCore.QLineF(px1, py1, px2, py2)
        dx, dy = targetXY(line.angle(), 30)
        nx1 = line.x1() + dx
        ny1 = line.y1() - dy
        nx2 = line.x2()  - dx
        ny2 = line.y2()  + dy
        link_line = QtCore.QLineF(nx1, ny1, nx2, ny2)

        if count > 0:
            offset_line = link_line.normalVector()
            offset_line.setLength(7.0)
            #base_offset = QtCore.QPointF(offset_line.dx(), offset_line.dy())
            if count % 2 == 0:   # if count is even
                count = - (count / 2)
                link_line.translate((offset_line.dx() * count),
                                    (offset_line.dy() * count))
                self.setLine(link_line)
            else:   # count is odd
                count = (count / 2) + 1
                link_line.translate((offset_line.dx() * count),
                                    (offset_line.dy() * count))
                self.setLine(link_line)
        else:
            self.setLine(link_line)
        


class GridHex(QtGui.QGraphicsPolygonItem):

    def __init__(self, parent=None,
                 hex_color=QtCore.Qt.darkGray,
                 hex_brush=QtCore.Qt.transparent):
        QtGui.QGraphicsPolygonItem.__init__(self, parent)
        self._type = GRID_HEX_TYPE
        # path = QtGui.QPainterPath()
        self.pen = QtGui.QPen()
        self.pen.setWidth(0)
        self.pen.setColor(hex_color)
        self.setPen(self.pen)
        self.setBrush(hex_brush)
        topleft = ((HEX_DELTA - 50.0), -50.0)
        topright = ((50.0 - HEX_DELTA), -50.0)
        midright = ((50.0 + HEX_DELTA), 0.0)
        lowright = ((50.0 - HEX_DELTA), 50.0)
        lowleft = ((HEX_DELTA - 50.0), 50.0)
        midleft = ((-50.0 - HEX_DELTA), 0.0)
        myPolygon = QtGui.QPolygonF([
                    QtCore.QPointF(topleft[0], topleft[1]),
                    QtCore.QPointF(topright[0], topright[1]),
                    QtCore.QPointF(midright[0], midright[1]),
                    QtCore.QPointF(lowright[0], lowright[1]),
                    QtCore.QPointF(lowleft[0], lowleft[1]),
                    QtCore.QPointF(midleft[0], midleft[1]),
                    QtCore.QPointF(topleft[0], topleft[1])])
        self.setPolygon(myPolygon)
        self.myPolygon = myPolygon
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)

    @property
    def itemType(self):
        return self._type

    def boundingRect(self):
        pen_width = self.pen.width()
        return QtCore.QRectF((HEX_DELTA - (50.0 + pen_width) ), (-50 - pen_width),
                             (100 + HEX_DELTA + pen_width), (100 + pen_width))

    def shape(self):
        path = QtGui.QPainterPath()
        path.addPolygon(self.myPolygon)
        return path

    def image(self):
        pixmap = QtGui.QPixmap(250, 250)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray, 8))
        painter.translate(125, 125)
        painter.drawPolyline(self.myPolygon)
        return pixmap


class GridCell(QtGui.QGraphicsItemGroup):
    def __init__(self, x, y, hex_color=QtCore.Qt.darkGray, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        self._type = GRID_CELL_TYPE
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

        self.col = x
        self.row = y
        
        self.grid_poly = GridHex(self, hex_color)
        # The selection polly is used as a mask for indicating item selection
        self.selection_poly = GridHex(self, hex_color)
        
        self.grid_text = QtGui.QGraphicsSimpleTextItem(self)
        self.grid_text.setBrush(QtCore.Qt.darkGray)
        self.allegianceColor = QtCore.Qt.transparent

    @property
    def itemType(self):
        return self._type

    def setAllegianceColor(self, color):
        self.allegianceColor = color
        self.grid_poly.setBrush(color)

    def displayGridCoordText(self, flag):
        if flag:
            sectorX, sectorY = self.scene().model.gridToSector(
                                                    self.col, self.row)
            text = str(sectorX).zfill(2) + str(sectorY).zfill(2)
            self.grid_text.setText(text)
            offset = -1.0 * (self.grid_text.boundingRect().width()/2)
            self.grid_text.setPos(offset, -50.0)
            self.grid_text.show()
        else:
            self.grid_text.hide()

    def displayGlobalGridCoordText(self, flag):
        if flag:
            text = str(self.col) + ' ' + str(self.row)
            self.grid_text.setText(text)
            offset = -1.0 * (self.grid_text.boundingRect().width()/2)
            self.grid_text.setPos(offset, -45.0)
            self.grid_text.show()
        else:
            self.grid_text.hide()

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            if value == True:
                self.selection_poly.setBrush(QtCore.Qt.darkGray)
                self.selection_poly.setOpacity(0.7)
                self.scene().model.currentCell = (self.col, self.row)
            else:
                self.grid_poly.setBrush(self.allegianceColor)
                self.selection_poly.setBrush(QtCore.Qt.transparent)
        else:
            return value

    def boundingRect(self):
        # Required for rubber band drag selection
        return self.grid_poly.boundingRect()

    def shape(self):
        return self.grid_poly.shape()


class PlanetCircle(QtGui.QGraphicsItem):

    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        self._type = PLANET_CIRCLE_TYPE
        self.planet_color = QtCore.Qt.darkBlue
        self.sky_color = QtGui.QColor('#55AAFF')

    @property
    def itemType(self):
        return self._type

    def boundingRect(self):
        return QtCore.QRectF(-10.5, -10.5, 22, 22)

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        #painter.setBrush(QtCore.Qt.cyan)
        painter.setBrush(self.sky_color)
        painter.drawEllipse(-12, -12, 24, 24)
        #painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.setBrush(QtGui.QBrush(self.planet_color))
        painter.drawEllipse(-8, -8, 16, 16)

    def setPlanetColor(self, color):
        self.planet_color = color
        self.update()

    def setSkyColor(self, color):
        self.sky_color = color
        self.update()

    def setSelectionColour(self, flag):
        if flag == True:
            self.color = QtCore.Qt.green
        else:
            self.color = QtCore.Qt.blue
        self.update()



class PlanetGlyph(QtGui.QGraphicsItem):
    def __init__(self, pmi, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        self._type = PLANET_GLYPH_TYPE
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.planet_image = PlanetCircle(self)
        self.name_text = QtGui.QGraphicsSimpleTextItem(self)
        self.display_code = QtGui.QGraphicsSimpleTextItem(self)

        self._pmi = pmi
        self.configurePlanetGlyph(False)

    @property
    def itemType(self):
        return self._type

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            if value == True:
                self.planet_image.setSelectionColour(True)
            else:
                self.planet_image.setSelectionColour(False)
        else:
            return value

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        # Required for rubber band drag selection
        return QtCore.QRectF(-25, -25, 50, 50)

    def configurePlanetGlyph(self, show_details):
        if show_details:

            if self._pmi != None:
                world = self.pmi.model().getWorld(self.pmi)
                
                self.name_text.setFont(QtGui.QFont('Helvetica', 12, QtGui.QFont.Bold))
                self.name_text.setText(world.name)
                offset = -1.0 * (self.name_text.boundingRect().width()/2)
                self.name_text.setPos(offset, -35)

##                code_value = world.starport.code
##                self.display_code.setFont(QtGui.QFont('Helvetica', 10, QtGui.QFont.Bold))
##                self.display_code.setText(str(code_value))
##                offset = -1.0 * (self.display_code.boundingRect().width()/2)
##                self.display_code.setPos(offset, -30)

# Not sure what this was here for. Mistake?
#                self.planet_image

                self.name_text.show()
                self.planet_image.show()
##                self.display_code.show()

        else:
            self.planet_image.show()
            self.name_text.hide()
##            self.display_code.hide()
            

    def getPMI(self):
        return self._pmi
    def setPMI(self, pmi):
        self._pmi = pmi
        self.configurePlanetGlyph()
    def delPMI(self):
        del self._pmi
    pmi = property(getPMI, setPMI, delPMI, "The Planet's pmi property")
