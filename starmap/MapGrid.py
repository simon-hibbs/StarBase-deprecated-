# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PySide import QtCore, QtGui

import math
from starmap import MapGlyphs
from model import Models
from log import *

CELLSIZE = 100


def gridToPix(gx, gy):
    px = CELLSIZE * gx
    py = CELLSIZE * gy
    if gx%2 != 0:
        py += CELLSIZE / 2.0
    return px, py

def gridToSlant(gx, gy):
    sx = gx
    sy = gy - (int(gx) / 2)
    return sx, sy

def slantToGrid(sx, sy):
    gx = sx
    gy = sy + (int(sx) / 2)
    return gx, gy

class SectorRoot(QtGui.QGraphicsItem):
    def __init__(self, parent=None, secs_wide=1, secs_high=1):
        QtGui.QGraphicsItem.__init__(self, parent)
        # the co-ordinates of a sector are those of the top-left hex

        self._type = MapGlyphs.SECTOR_ROOT_TYPE

        self.width = secs_wide
        self.height = secs_high
        self.grid = {}
        self.initSectorGrid(secs_wide, secs_high)

    def initSectorGrid(self, width, height):
        self.grid = {}
        for sector_x in range(width):
            for sector_y in range(height):
                sector_glyph = MapGlyphs.SectorGlyph(sector_x, sector_y)
                sector_glyph.setParentItem(self)
                # calculate 'home' hex co-ordinates for the sector
                hx = sector_x * 32
                hy = sector_y * 40
                # calculate pixel co-ordinates
                px, py = gridToPix(hx, hy)
                sector_glyph.setPos(px, py)
                self.grid[(sector_x, sector_y)] = sector_glyph

    @property
    def itemType(self):
        return self._type

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        return QtCore.QRectF()

    def setSectorData(self, name, sector_x, sector_y):
        self.grid[(sector_x, sector_y)].setName(name)

    def showSectorNames(self, flag):
        for sector in self.grid.itervalues():
            sector.showName(flag)


class SubSectorRoot(QtGui.QGraphicsItem):
    def __init__(self, parent=None, subsecs_wide=4, subsecs_high=4):
        QtGui.QGraphicsItem.__init__(self, parent)
        # the co-ordinates of a subsector are those of the top-left hex
        self._type = MapGlyphs.SUBSECTOR_ROOT_TYPE

        self.width = subsecs_wide
        self.height = subsecs_high
        self.grid = []
        self.initSubsectorGrid(subsecs_wide, subsecs_high)

    def initSubsectorGrid(self, width, height):
        self.grid = []
        for ssgrid_x in range(width):
            self.grid.append([])
            for ssgrid_y in range(height):
                subsector_glyph = MapGlyphs.SubSectorGlyph(ssgrid_x, ssgrid_y)
                subsector_glyph.setParentItem(self)
                # calculate 'home' hex co-ordinates for the subsector
                hexgrid_x = ssgrid_x * 8
                hexgrid_y = ssgrid_y * 10
                # calculate pixel co-ordinates
                pixel_x, pixel_y = gridToPix(hexgrid_x, hexgrid_y)
                subsector_glyph.setPos(pixel_x, pixel_y)
                self.grid[ssgrid_x].append(subsector_glyph)

    @property
    def itemType(self):
        return self._type

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        return QtCore.QRectF()

    def setSubsectorData(self, name, subgrid_x, subgrid_y):
        self.grid[subgrid_x][subgrid_y].setName(name)

    def showSubsectorNames(self, flag):
        for row in self.grid:
            for subsector in row:
                subsector.showName(flag)


class HexRoot(QtGui.QGraphicsItem):

    def __init__(self, parent=None, hexes_wide=32, hexes_high=40, hex_color=QtCore.Qt.darkGray):
        QtGui.QGraphicsItem.__init__(self, parent)
        self._type = MapGlyphs.HEX_ROOT_TYPE

        self.hex_color = hex_color
        self.width = hexes_wide
        self.height = hexes_high
        self.grid = []
        self.initGrid(hexes_wide, hexes_high)

    @property
    def itemType(self):
        return self._type

    def initGrid(self, width, height):
        self.grid = []
        for x in range(width):
            self.grid.append([])
            for y in range(height):
                hex_glyph = MapGlyphs.GridCell(x, y, self.hex_color)
                hex_glyph.setParentItem(self)
                #hex_glyph.col = x
                #hex_glyph.row = y
                # calculate pixel co-ordinates
                px, py = gridToPix(x, y)
                hex_glyph.setPos(px, py)
                self.grid[x].append(hex_glyph)

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        return QtCore.QRectF()

    def config(self):
        self.my_scene = self.scene()
        self.my_scene.changeCellsSelectable.connect(self.setCellsSelectable)

    def setCoordsVisible(self, flag):
        for item in self.childItems():
            item.displayGridCoordText(flag)
        
    def setCellsSelectable(self, flag):
        for item in self.childItems():
            item.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, flag)


class NetworkRoot(QtGui.QGraphicsItem):
    # The networks belong to the WebRoot
    
    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        self._type = MapGlyphs.NETWORK_ROOT_TYPE

        self.links = []
        self.cell_pairs = []

    @property
    def itemType(self):
        return self._type

    def redrawLinks(self):
        for glyph in self.links:
            scene = glyph.scene()
            scene.removeItem(glyph)
            del glyph
        self.links = []
        self.cell_pairs = []

        # obtains links in the form: [[xy1, xy2, link],]
        for cell1, cell2, link in self.scene().model.network_model.links:
            if link.visible:
                line_glyph = MapGlyphs.LinkLine()
                line_glyph.setParentItem(self)
                
                px1, py1 = gridToPix(cell1[0], cell1[1])
                px2, py2 = gridToPix(cell2[0], cell2[1])
                line_glyph.setColor(link.color)
                line_glyph.setStyle(link.line_style)

                # Count the number of links so far, in either direction
                count = self.cell_pairs.count((cell1, cell2))
                count += self.cell_pairs.count((cell2, cell1))
                
                line_glyph.drawLine(px1, py1, px2, py2, count)

                self.links.append(line_glyph)
                self.cell_pairs.append((cell1, cell2))

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        return QtCore.QRectF()
        
        
class Grid(QtGui.QGraphicsItem):
    
    def __init__(self, secs_wide=1, secs_high=1, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        # Parent item for all items with grid coordinates
        # Scene position should be (0,0) for simplicity
        self._type = MapGlyphs.GRID_TYPE

        subsecs_wide = secs_wide * 4
        subsecs_high = secs_high * 4
        hexes_wide = secs_wide * 32
        hexes_high = secs_high * 40

        #self.hex_root.setVisible(False)
        self.hex_root = HexRoot(self, hexes_wide, hexes_high, hex_color=QtCore.Qt.darkGray)
        self.sector_root = SectorRoot(self, secs_wide, secs_high)
        self.subsector_root = SubSectorRoot(self, subsecs_wide, subsecs_high)
        self.network_root = NetworkRoot(self)

        for col in self.hex_root.grid:
            for cell in col:
                sec_x = int(math.floor(cell.col / 32))
                sec_y = int(math.floor(cell.row / 40))
                self.sector_root.grid[(sec_x, sec_y)].cells.append(cell)

                subsec_x = int(math.floor(cell.col / 8))
                subsec_y = int(math.floor(cell.row / 10))
                self.subsector_root.grid[subsec_x][subsec_y].cells.append(cell)

        self.worlds_coords = []
        self.worlds_data = []
        self.worlds_glyphs = []
        self.worlds_pmi = []
        self.show_details = True
        self.displayAllegiances = False


    @property
    def itemType(self):
        return self._type

    def paint(self, painter=None, option=None, widget=None):
        pass

    def setHexGridVisible(self, flag):
        self.hex_root.setVisible(flag)

    def setCoordsVisible(self, flag):
        self.hex_root.setCoordsVisible(flag)

    def showWorldDetails(self, flag):
        self.show_details = flag
        for world_glyph in self.worlds_glyphs:
            world_glyph.configurePlanetGlyph(flag)

    def showSubsectorNames(self, flag):
        self.subsector_root.showSubsectorNames(flag)

    def showSectorNames(self, flag):
        self.sector_root.showSectorNames(flag)

    def linksChanged(self):
        self.network_root.redrawLinks()
        #print "     Grid: Links changed"

    def selectCells(self, cell_list):
        if len(cell_list) > 0:
            for coords in cell_list:
                self.hex_root.grid[coords[0]][coords[1]].setSelected(True)


    def toggleAllegianceDisplay(self, checked):
        self.displayAllegiances = checked
        if checked:
            count = 0
            for pmi in self.worlds_pmi:
                hex_col, hex_row, color = pmi.model().getAllegianceInfo(pmi)
                self.hex_root.grid[hex_col][hex_row].setAllegianceColor(color)
        else:
            for col in self.hex_root.grid:
                for cell in col:
                    cell.setAllegianceColor(QtCore.Qt.transparent)

    def setSectorData(self, name, sector_x, sector_y):
        self.sector_root.setSectorData(name, sector_x, sector_y)

    def setSubsectorData(self, name, subgrid_x, subgrid_y):
        self.subsector_root.setSubsectorData(name, subgrid_x, subgrid_y)

    def worldPmiAt(self, x, y):
        try:
            index = self.worlds_coords.index((x, y))
            return self.worlds_pmi[index]
        except:
            return None

    def config(self):
        self.hex_root.config()

    def worldChanged(self, row):
        pmi = self.worlds_pmi[row]
        world = pmi.model().getWorld(pmi)
        self.worlds_coords[row] = (world.col, world.row)
        self.world_data = world
        self.worlds_glyphs[row].world = world
        px, py = gridToPix(world.col, world.row)
        self.worlds_glyphs[row].configurePlanetGlyph(self.show_details)
        self.worlds_glyphs[row].setPos(px, py)

        if self.displayAllegiances == True:
            hex_col, hex_row, color = pmi.model().getAllegianceInfo(pmi)
            self.hex_root.grid[hex_col][hex_row].setAllegianceColor(color)

    def insertWorld(self, pmi, selectable):
        # use the PMI to map to the row and retrieve world data.
        model_row = pmi.row()
        world = pmi.model().getWorld(pmi)
        glyph = MapGlyphs.PlanetGlyph(pmi)
        glyph.configurePlanetGlyph(self.show_details)
        glyph.setParentItem(self)
        px, py = gridToPix(world.col, world.row)
        glyph.setPos(px, py)
        glyph.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, selectable)
        #
        self.worlds_coords.insert(model_row, (world.col, world.row))
        self.worlds_data.insert(model_row, world)
        self.worlds_pmi.insert(model_row, pmi)
        self.worlds_glyphs.insert(model_row, glyph)
        #

    def removeWorld(self, row):
        glyph = self.worlds_glyphs[row]
        del self.worlds_coords[row]
        del self.worlds_data[row]
        del self.worlds_pmi[row]
        del self.worlds_glyphs[row]
        scene = glyph.scene()
        scene.removeItem(glyph)
        del glyph

    @logmethod
    def clearWorlds(self):
        self.worlds_coords = []
        self.worlds_data = []
        self.worlds_glyphs = []
        self.worlds_pmi = []

    def boundingRect(self):
        return QtCore.QRectF()

