# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

import platform
from PySide.QtCore import *
from PySide.QtGui import *
import os
import sys
import shutil
import tempfile
import csv
from ConfigParser import SafeConfigParser
import random
import math
#import richtextlineedit
import unicodedata
import re
from model import Foundation
from model import NetworkModel as NWM
#from model import Merchant
try:
    import cPickle as pickle
except:
    import pickle

from log import *


debug_log('Hello world')

NAME = 0
COL = 1
ROW = 2
SECTOR_COORDS = 3
OWNING_SECTOR = 4
OWNING_SUBSECTOR = 5
ALLEGIANCE_CODE = 6
ALLEGIANCE_NAME = 7
ATTRIBUTE_BASE = 8

# see lastColumn property

CODE_ROLE = 1001
LABEL_ROLE = 1002
DESCRIPTION_ROLE = 1003

def gridToSlant(gx, gy):
    sx = gx
    sy = gy + math.ceil(float(gx) / 2)
    return int(sx), int(sy)


def gridToHEX(gx, gy):
    # Convert x,y coords to H,E,X three-axis coordinates
    H = int(math.floor( 2.0 * gy))
    E = int(math.floor(math.sqrt(3.0) * gx - gy))
    X = int(math.floor(math.sqrt(3.0) * gx + gy))
    return H, E, X


FIELD_NAMES = ['World Name', 'Column', 'Row', 'Allegiance', 'Attributes']

ACQUIRED = 1



class WorldModel(QAbstractTableModel):

    regionAdded = Signal(str)
    regionDisbanded = Signal(int)

    def __init__(self):
        super(WorldModel, self).__init__()

        self.secsWide = 1
        self.secsHigh = 1

        self.project_path = ''
        self.sectors_file = ''
        self.subsectors_file = ''
        self.worlds_file = ''
        
        self.initialZoomLevel = 3
        self.horizontalScroll = 0
        self.verticalScroll = 0

        self.worldOccurrenceDM = 0
        self.worldOccurrence = 50
        
        self.dirty = False
        
        self.sectors = []
        self.subsectors = []
        self.worlds = []
#        #self.field_names = FIELD_NAMES
        #self.attributeDefinitions = [Foundation.AttributeDefinition(Rules.atmo_data),
        #                             Foundation.AttributeDefinition(Rules.tech_data)]
#        #for attribute_def in self.attributeDefinitions:
#        #    self.field_names.append(attribute_def.name)
        
        self.deleted_worlds= []
        #self.merchant = Merchant.MerchantData()
        #self.fromTradeWorldPmi = None
        #self.toTradeWorldPmi = None
        self.groupNames = ['None']
        self.groupCells = [[]]
        self.selectedGroupIndex = 0
        
        self.hexRegionNames = ['None']
        self.hexRegionCells = [[]]
        self.selectedRegionIndex = 0

        self.codedLabels = True

        self.generateWorld = None     # Placeholder to import generator into

        #The following is a placeholder and is actualy initialised by
        #refreshWorldGeneratorsCombo in the main starbase.py script
        #so that the combo is correctly populated.
        self.currentWorldGeneratorName = 'None'

        # This needs to go into the project config file
        self.auto_name = True
        self.world_name_list = []

        self.network_model = NWM.NetworkModel()

        self._col = -1
        self._row = -1



    # Called by the project manager. Load the project data into the model.
    def loadProjectData(self, project_path):
        self.project_path = project_path

        # Load WorldNames.txt from project if it exists, otherwise use the default
        project_names_file = os.path.join(self.project_path, 'WorldNames.txt')
        if os.path.isfile(project_names_file):
            with open(project_names_file, 'r') as f:
                self.world_name_list = f.readlines()
                debug_log('Using project WorldNames.txt file with ' + str(len(self.world_name_list)) + ' names')
        elif os.path.isfile('WorldNames.txt'):
            with open('WorldNames.txt', 'r') as f:
                self.world_name_list = f.readlines()
                debug_log('Using default WorldNames.txt file with ' + str(len(self.world_name_list)) + ' names')

        # Load Rulse.py from project file if it exists, otherwise load default rules file
        rules_path = os.path.join(self.project_path, 'Rules')
        if os.path.isfile(os.path.join(rules_path,  'Rules.py')):
            debug_log('Using project rules file')
            if  rules_path not in sys.path:
                sys.path.insert(-1, rules_path)
                import Rules
        else:
            from model import StandardRules as Rules

        Rules.project_path = project_path

        self.getWorldStats = Rules.getWorldStats
        self.getWorldDescriptions = Rules.getWorldDescriptions

        self.attributeDefinitions = []
        for definition in Rules.attributeDefinitions:
            self.attributeDefinitions.append(Foundation.AttributeDefinition(definition))

        # Check attribute definitions are consistent
        for definition in self.attributeDefinitions:
            for key in definition._data['Code Data'].iterkeys():
                if key not in definition.codes:
                    debug_log("World Attribute Error: key " + str(key) + "is in Code Data but not codes for " + definition.name)
        debug_log("Attribute Definitions: " + str(self.attributeDefinitions))
        debug_log('Loading project: ' + str(project_path))

        self.config_file = os.path.join(self.project_path ,  'starbase.ini')

        self.config = SafeConfigParser()
        self.config.read(self.config_file)

        self.secsWide = self.config.getint('Map', 'SectorGridWidth')
        self.secsHigh = self.config.getint('Map', 'SectorGridHeight')

        self.sectors_file = os.path.join(self.project_path, 
                                         self.config.get('Files', 'SectorsFile'))
        self.subsectors_file = os.path.join(self.project_path, 
                                            self.config.get('Files', 'SubsectorsFile'))
        self.worlds_file = os.path.join(self.project_path,
                                        self.config.get('Files', 'WorldsFile'))
        
        self.initialZoomLevel = self.config.getfloat('Display', 'ZoomLevel')
        self.horizontalScroll = self.config.getfloat('Display', 'HorizontalScroll')
        self.verticalScroll = self.config.getfloat('Display', 'VerticalScroll')

        try:
            self.codedLabels = self.config.getboolean('Options', 'codedlabels')
        except:
            self.codedLabels = False

        info_log('CodedLabels: ' + str(self.codedLabels))

        #Allegiance defaults defined in Traveller, but maintained in the model.
        #World objects just store the allegiance index into these lists.
        try:
            allegiance_codes = self.config.get('Overrides', 'allegiancecodes')
            allegiance_names = self.config.get('Overrides', 'allegiancenames')
            Foundation.allegiance_codes = allegiance_codes.split(',')
            Foundation.allegiance_names = allegiance_names.split(',')
            debug_log('Allegiance codes overriden.')
        except:
            debug_log('Allegiance codes not overriden, using defaults.')

        try:
            allegiance_colors = self.config.get('Overrides', 'allegiancecolors')
            Foundation.allegiance_colors = allegiance_colors.split(',')
        except:
            debug_log('Allegiance colors not overriden, using defaults.')

        self.worldOccurrenceDM = 0
        self.dirty = False
        
        self.sectors = []
        self.subsectors = []
        self.worlds = []
        self.deleted_worlds= []

        self.loadSectors()
        self.loadSubsectors()
        self.loadWorlds()


    def addFactions(self, pmi):
        row = pmi.row()
        self.worlds[row].addFactions()
        modelIndex1 = self.index(row, GOVERNMENT_TEXT)
        modelIndex2 = self.index(row, GOVERNMENT_TEXT)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                    modelIndex1, modelIndex2)

# Hex Regions
    def addNewHexRegion(self, region_name, region_cells=None):
        if region_cells == None:
            region_cells = []
        
        if region_name not in self.hexRegionNames:
            self.hexRegionNames.append(region_name)
            self.hexRegionCells.append(region_cells)
            debug_log('Model: new hex region "' + region_name + '" added.')
            self.regionAdded.emit(region_name)
        else:
            debug_log('Model: Duplicate hex region name: ' + region_name)
            return False
        return True

    def updateHexRegionName(self, region_name, cell_list):
        if region_name not in self.hexRegionNames:
            debug_log('World Model: failed to update region: ' + str(region_name))
        else:
            region_index = self.hexRegionNames.index(region_name)
            self.hexRegionCells[region_index] = cell_list
            debug_log('World Model: Region ' + region_name + ' contains: ' +\
                      str(cell_list))

    def updateHexRegionIndex(self, index, coord_list):
        if (index + 1) <= len(self.hexRegionNames):
            self.hexRegionCells[index] = coord_list

    def disbandRegion(self, index):
        if len(self.hexRegionNames)> index > 0:
            del self.hexRegionNames[index]
            del self.hexRegionCells[index]
            if index <= self.selectedRegionIndex:
                self.selectedRegionIndex -= index
            self.regionDisbanded.emit(index)
        else:
            info_log('Model: Region "' + self.hexRegionNames[index]+ '" not disbanded')

# Hex Groups
    def addNewGroup(self, group_name):
        if group_name not in self.groupNames:
            self.groupNames.append(group_name)
            self.groupCells.append([])
            debug_log('Model: Group "' + group_name + '" added.')
        else:
            debug_log('Model: Duplicate group name: ' + group_name)

    def addCellsToGroup(self, index, coord_list):
        self.groupCells[index] = coord_list
##        for xy in coord_list:
##            if xy not in self.groupCells[index]:
##                self.groupCells[index].append(xy)

    def disbandGroup(self, index):
        if len(self.groupNames) > index > 0:
            del self.groupNames[index]
            del self.groupCells[index]
            debug_log('Model: Group disbanded.')
            if index <= self.selectedGroupIndex:
                self.selectedGroupIndex -= 1
        else:
            debug_log('Model: Group "' + self.groupNames[index]+ '" not disbanded')

    def getCurrentCell(self):
        return self._col, self._row
    
    def setCurrentCell(self, cell_xy):
        col = cell_xy[0]
        row = cell_xy[1]
        if (self.secsWide * 32) > col >= 0:
            if (self.secsHigh * 40) > row >= 0:
                self._col = col
                self._row = row
            else:
                debug_log('Model.setCurrentCell: Row outside grid ' + \
                          str(col) + ' ' + str(row))
        else:
            debug_log('Model.setCurrentCell: Column outside grid ' + \
                      str(col) + ' ' + str(row))
    def delCurrentCell(self):
        del self._col
        del self._row
    currentCell = property(getCurrentCell, setCurrentCell, delCurrentCell,
             "Current cell coordinates")

    def getSubsectorList(self):
        return self.subsectors

    def getSectorList(self):
        return self.sectors

    def getAllegianceIndex(self, code):
        if code in Foundation.allegiance_codes:
            return Foundation.allegiance_codes.index(code)
        else:
            debug_log('Model: Index for invalid allegiance code requested: ' + str(code))
            return 0

    def getAllegianceInfo(self, pmi):
        world = self.worlds[pmi.row()]
        color = QColor(Foundation.allegiance_colors[world.allegiance.index])
        color.setAlpha(128)
        return world.col, world.row, color

    def setAllegianceCode(self, pmi, code):
        if pmi != None:
            allegiance_index = Foundation.allegiance_codes.index(code)
            codeModelIndex = self.index(pmi.row(), ALLEGIANCE_CODE)
            nameModelIndex = self.index(pmi.row(), ALLEGIANCE_NAME)
            self.setData(codeModelIndex, allegiance_index)
            self.setData(nameModelIndex, allegiance_index)

    def allegianceCodeToName(self, code):
        if code in Foundation.allegiance_codes:
            index = Foundation.allegiance_codes.index(code)
            if 0 <= index < len(Foundation.allegiance_names):
                return Foundation.allegiance_names[index]
            else:
                debug_log('Model: Allegiance names and codes lists do not match.')
                debug_log(str(Foundation.allegiance_codes))
                debug_log(str(Foundation.allegiance_names))
                return 'Non-alligned'
        else:
            debug_log('Model: Allegiance code ' + str(code) + ' not found in list.')
            return 'Non-alligned'         

    def renameSubsector(self, col, row, text):
        #Setting the name in the map needs to be done seperately
        for subsector in self.subsectors:
            if subsector.subsectorCol == col and subsector.subsectorRow == row:
                subsector.name = text

    def renameSector(self, col, row, text):
        #Setting the name in the map needs to be done seperately
        for sector in self.sectors:
            if sector.sectorCol == col and sector.sectorRow == row:
                sector.name = text

    def allegianceDataChanged(self):
        modelIndex1 = self.index(0, ALLEGIANCE_CODE)
        modelIndex2 = self.index((len(self.worlds) - 1), ALLEGIANCE_NAME)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                    modelIndex1, modelIndex2)

    def mergeAllegiance(self, merge_from, merge_to):
        if merge_from in Foundation.allegiance_names and \
           merge_to in Foundation.allegiance_names:
            debug_log('Codes: ' + str(Foundation.allegiance_codes))
            debug_log('Merge From: ' + merge_from)
            debug_log('Merge To: ' + merge_to)
            
            from_index = Foundation.allegiance_names.index(merge_from)
            from_code = Foundation.allegiance_codes[from_index]
            debug_log('From Index: ' + str(from_index))
            debug_log('From Code: ' + from_code)

            to_index = Foundation.allegiance_names.index(merge_to)
            to_code = Foundation.allegiance_codes[to_index]
            debug_log('To Index: ' + str(to_index))
            debug_log('To Code: ' + to_code)

            for world in self.worlds:
                if world.allegiance.code == from_code:
                    world_index = self.worlds.index(world)
                    debug_log('Merging world ' + str(world.name) + ' from ' + \
                              world.allegiance.code)
                    world.allegiance.code = to_code
                    debug_log('To ' + world.allegiance.code)
                    debug_log('Index ' + str(world.allegiance.index))
                    
                    modelIndex1 = self.index(world_index, ALLEGIANCE_CODE)
                    modelIndex2 = self.index(world_index, ALLEGIANCE_NAME)
                    self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                              modelIndex1, modelIndex2)
            
            debug_log('Current codes: ')
            debug_log(str(Foundation.allegiance_codes))
            del Foundation.allegiance_codes[from_index]
            debug_log('New codes: ')
            debug_log(str(Foundation.allegiance_codes))
            del Foundation.allegiance_names[from_index]
            del Foundation.allegiance_colors[from_index]

            for world in self.worlds:
                if world.allegiance.index > from_index:
                    world_index = self.worlds.index(world)
                    world.allegiance.index = world.allegiance.index - 1

                    modelIndex1 = self.index(world_index, ALLEGIANCE_CODE)
                    modelIndex2 = self.index(world_index, ALLEGIANCE_NAME)
                    self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                              modelIndex1, modelIndex2)

        else:
            debug_log('Model: Allegiance merge error')
            debug_log('From: ' + merge_from)
            debug_log('To: ' + merge_to)
            debug_log('Codes: ' + str(Foundation.allegiance_codes))


    # Converts global grid coords to sector relative coords for grid display
    def gridToSector(self, gx, gy):
        sec_x = (gx % 32) + 1
        sec_y = (gy % 40) + 1
        return sec_x, sec_y

    def owningSector(self, gx, gy):
        sec_x = int(math.floor(float(gx) / 32.0))
        sec_y = int(math.floor(float(gy) / 40.0))

        for sector in self.sectors:
            if sec_x == sector.sectorCol \
               and sec_y == sector.sectorRow:
                return sector.name

    def owningSubsector(self, gx, gy):
        sub_x = int(math.floor(float(gx) / 8.0))
        sub_y = int(math.floor(float(gy) / 10.0))

        for sub in self.subsectors:
            if sub_x == sub.subsectorCol \
               and sub_y == sub.subsectorRow:
                return sub.name

    def getSubsectorAt(self, subX, subY):
        for subsector in self.subsectors:
            if subsector.subsectorCol == subX and \
               subsector.subsectorRow == subY:
                return subsector.name
        return None

    def getSectorAt(self, secX, secY):
        for sector in self.sectors:
            if sector.sectorCol == secX and \
               sector.sectorRow == secY:
                return sector.name
        return None

    def slugify(self, name):
        name = unicode(name)
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
        name = unicode(re.sub('[^\w\s-]', '', name).strip().lower())
        return str(re.sub('[-\s]+', '-', name))


    def storeWorldImage(self, world_name, image):
        world_path = os.path.join(self.project_path,
                                  'worlds',
                                  self.slugify(world_name))
        world_path = str(world_path)
        if not os.path.exists(world_path):
            os.makedirs(world_path)
            
        file_name = self.slugify(world_name) + '.png'
        file_path = os.path.join(world_path,  file_name)
        
        with open(file_path, 'w') as f:
            image.save(file_path,  'PNG')
        
        return file_path


    def storeTextData(self, world_name, file_name, text):
        # Store custom text in a file, or delete the file if the text is blank,
        # which reverts description text to the default.
        world_path = os.path.join(self.project_path,
                                  'worlds',
                                  self.slugify(world_name))
        world_path = str(world_path)
        if not os.path.exists(world_path):
            os.makedirs(world_path)
        file_path = os.path.join(world_path,  file_name)
        if text == "" and os.path.exists(file_path):
            os.remove(file_path)
        else:
            with open(file_path, 'w') as f:
                    f.seek(0)
                    f.truncate()
                    f.write(text)

    def retrieveTextData(self, world_name, file_name):
        # Retrieve custom text from file.
        file_path = os.path.join(self.project_path,'worlds',
                            self.slugify(world_name),
                            file_name)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                text = f.read()
                return text
        return False

    def cleanupWorldsDirectory(self, world_name):
        path = os.path.join(self.project_path,
                            'worlds',
                            self.slugify(world_name))
        
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                debug_log('Deleted ' + path)
            except Exception, e:
                debug_log('Failed to delete ' + path)
                debug_log(e)
                return False

        return True

    # storeX methods to persist sesion parameters to config file
    def storeZoomLevel(self, zl):
        self.config.set('Display', 'ZoomLevel', str(zl))

    def storeHorizontalScroll(self, value):
        self.config.set('Display', 'HorizontalScroll', str(value))

    def storeVerticalScroll(self, value):
        self.config.set('Display', 'VerticalScroll', str(value))

    def storeAllegianceInfo(self):
        codes = ','.join(Foundation.allegiance_codes)
        names = ','.join(Foundation.allegiance_names)
        colors = ','.join(Foundation.allegiance_colors)
        
        self.config.set('Overrides', 'allegiancecodes', codes)
        self.config.set('Overrides', 'allegiancenames', names)
        #self.config.set('Overrides', 'allegiancecolors', colors)
        

    # Provides PMI for column 0 of given row. Used later to map back to the row.
    def getPMI(self, row):
        index = self.index(row,  NAME)
        return QPersistentModelIndex(index)

    def getPmiAt(self, grid_col, grid_row):
        for world in self.worlds:
            if world.col == grid_col and world.row == grid_row:
                model_row = self.worlds.index(world)
                index = self.index(model_row,  NAME)
                return QPersistentModelIndex(index)
        else:
            return None

    def getWorld(self, pmi):
        row = pmi.row()
        return self.worlds[row]

    def getWorldAt(self, xy):
        return self.getWorld(self.getPmiAt(xy[0], xy[1]))

    def getDistance(self, fromColRow, toColRow):
        #Parameters are two-tupples of integers
        x1, y1 = gridToSlant(fromColRow[0], fromColRow[1])
        x2, y2 = gridToSlant(toColRow[0], toColRow[1])

        dx = x2 - x1
        dy = y2 - y1
        dd = dx - dy
       
        return int(max([math.fabs(dx), math.fabs(dy), math.fabs(dd)]))


    def rollToPopulate(self):
        roll = random.randint(1, 100)# + self.worldOccurrenceDM
        if roll <= self.worldOccurrence:
            #debug_log('Model: rollToPopulate True = ' + str(roll))
            return True
        else:
            #debug_log('Model: rollToPopulate False = ' + str(roll))
            return False


    def insertRandomWorld(self, row):
        #self.insertRow(row)
        #debug_log('Model: Inserting random world at row ' + str(row))
##        world = Foundation.World()
##        world.randomize()
        self.insertRow(row)
        #self.regenerateWorld(row)

    def regenerateWorld(self, row):
        #debug_log('Model: Randomizing existing world at row ' + str(row))
        modelIndex1 = self.index(row, 0)
        modelIndex2 = self.index(row, self.lastColumn)

        # self.generateWorld is a reference to Rules.generateWorld
        codes = self.getWorldStats()
        descriptions = self.getWorldDescriptions(codes)
        if len(codes) != len(descriptions):
            debug_log('Critical error in worlds model - description and codes lists from rules are different lengths!')
        self.worlds[row].reconfigure(codes)

        for (index, text) in enumerate(descriptions):
            if text != '' and text != self.attributeDefinitions[index].description(codes[index]):
                debug_log('Setting auto-generated custom text for world ' + str(self.worlds[row].name))
                self.storeTextData(self.worlds[row].name,
                                   self.attributeDefinitions[index].name + '.txt',
                                   text)

        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      modelIndex1, modelIndex2)

    def toggleAutoName(self, flag):
        if flag:
            debug_log('World Model: Enabling auto-name')
            self.auto_name = True
        else:
            debug_log('World Model: Disabling auto-name')
            self.auto_name = False

    def createWorldName(self, salt):
        if len(self.world_name_list) > 0:
            name_number = random.randint(0, (len(self.world_name_list) - 1))
            name = self.world_name_list.pop(name_number).rstrip()

            if salt and len(name) < 8:
                limit = 15 - len(name)
                d20 = random.randint(1, 20)
                if d20 <= 2:
                    name = 'New ' + name
                elif 2 <= d20 <= limit:
                    suffix = random.choice([' Prime', ' Prime', ' Alpha', ' Alpha',
                                            ' Beta', ' Gamma', ' Delta', ' Minor',
                                            ' Majoris', ' II', ' II', ' III', ' III',
                                            ' IV', ' IV', ' V', ' V', ' VI', ' IX'])
                    name = name + suffix

        return name

    def hasWorldAtXY(self, x, y):
        answer = False
        self.world_at_xy = None
        for w in self.worlds:
            if w.col == x and w.row == y:
                answer = True
                self.world_at_xy = w
        return answer

    def hasNamedWorld(self, name):
        for world in self.worlds:
            if world.name == name:
                return True
        return False

##    def sortByName(self):
##        self.worlds = sorted(self.worlds)
##        self.reset()


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)

    @property
    def lastColumn(self):
        return ATTRIBUTE_BASE + (len(self.attributeDefinitions) * 2) - 1


    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < len(self.worlds)):
            return None
        world = self.worlds[index.row()]
        column = index.column()
        if role == Qt.DisplayRole \
           or role == Qt.EditRole \
           or role == DESCRIPTION_ROLE:
            
            if column == NAME:
                return world.name
            
            elif column == COL:
                return world.col
            
            elif column == ROW:
                return world.row

            elif column == SECTOR_COORDS:
                x, y = self.gridToSector(world.col, world.row)
                text = str(x).zfill(2) + str(y).zfill(2)
                return text

            elif column == OWNING_SECTOR:
                return self.owningSector(world.col, world.row)

            elif column == OWNING_SUBSECTOR:
                return self.owningSubsector(world.col, world.row)

            elif column == ALLEGIANCE_CODE:
                if role == Qt.EditRole:
                    return world.allegiance.index
                elif role == Qt.DisplayRole:
                    return world.allegiance.code
                else:
                    return world.allegiance.code

            elif column == ALLEGIANCE_NAME:
                if role == Qt.EditRole:
                    return world.allegiance.index
                elif role == Qt.DisplayRole:
                    return world.allegiance.name
                else:
                    return world.allegiance.name

            # Attributes have two roles:
            #  - EditRole which returns the attribute code index
            #  - DESCRIPTION_ROLE which returns the description text.

            elif column >= ATTRIBUTE_BASE:
                ##print 'model.data: column = ' + str(column)
                attribute_index = column - ATTRIBUTE_BASE
                ##print "attribute_index = ", attribute_index
                try:
                    attribute_code = world.attributes[attribute_index]
                except:
                    ##print "World attribute list too short when retrieving model data."
                    names = ''
                    for definition in self.attributeDefinitions:
                        names += definition.name + ' '
                    ##print names
                    ##print world.attributes
                    attribute_code='0'
                    #world.attributes.append('0')

                attribute_definition = self.attributeDefinitions[attribute_index]

                if role == Qt.EditRole:
                    # return the code index
                    ##print 'Name: ', attribute_definition.name 
                    ##print "Attribute Codes:", attribute_definition.codes
                    ##print "Code for lookup: ", attribute_code, ' type: ', type(attribute_code)
                    ##print 'model.data: Edit Role Attribute Index = ' + \
                    ##          str(attribute_definition.index(attribute_code))
                    return attribute_definition.index(attribute_code)
                
                elif role == CODE_ROLE:
                    return attribute_code
                
                elif role == LABEL_ROLE:
                    return attribute_definition.label(attribute_code)
                
                elif role == DESCRIPTION_ROLE:
                    file_path = os.path.join(self.project_path, 'worlds',
                                             self.slugify(world.name),
                                             attribute_definition.name + '.txt')
                    ##print 'Description Role model.data: ', file_path
                    if os.path.exists(file_path):
                        ##print "Retrieving from file"
                        return self.retrieveTextData(world.name, attribute_definition.name + '.txt')
                    else:
                        #print 'model.data: Attribute Description = ' + \
                        #      attribute_definition.description(attribute_code)
                        ##print "Retrieving default text"
                        return attribute_definition.description(attribute_code)
                else:
                    # For all other roles, return the code
                    ##print 'model.data: Attribute Code = ' + attribute_code
                    return attribute_code

        elif role == Qt.TextAlignmentRole:
            if column == NAME:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
##        elif role == Qt.TextColorRole and column == STARPORT:
##            return QColor(Qt.darkBlue)
##        elif role == Qt.BackgroundColorRole:
##            if world.starport.code == "A" or world.starport.code == "B":
##                return QColor(250, 230, 250)
##            else:
##                return QColor(210, 230, 230)
        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return int(Qt.AlignLeft|Qt.AlignVCenter)
            return int(Qt.AlignRight|Qt.AlignVCenter)
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if section == NAME:
                return "Name"
            elif section == COL:
                return "Column"
            elif section == ROW:
                return "Row"
            elif section == SECTOR_COORDS:
                return "Sector Hex"
            elif section == OWNING_SECTOR :
                return "Sector"
            elif section == OWNING_SUBSECTOR :
                return "Subsector"
            elif section == ALLEGIANCE_CODE:
                return "Allegiance Code"
            elif section == ALLEGIANCE_NAME:
                return "Allegiance Name"
            elif section >= ATTRIBUTE_BASE:
                attribute_index = ATTRIBUTE_BASE - column
                return self.attributeDefinitions[attribute_index].name
            
        return int(section + 1)


    def rowCount(self, index=QModelIndex()):
        return len(self.worlds)

    def columnCount(self, index=QModelIndex()):
        return (self.lastColumn + 1)

    @logmethod
    def setData(self, index, value, role=Qt.EditRole):
        debug_log('setData: role: ' + str(role))
        debug_log("setData:Row " + str(index.row()) + " Col " + str(index.column()) +
                  " value " + str(value))

        if index.isValid() and 0 <= index.row() < len(self.worlds):
            world = self.worlds[index.row()]
            column = index.column()
            
            if column == NAME:
                new_name = str(value)
                if new_name != world.name:
                    for w in self.worlds:
                        if new_name == w.name:
                            debug_log('Models:setData duplicate world name ' + new_name)
                            return False
                        
                    old_path = os.path.join(self.project_path, 'worlds', 
                                            self.slugify(world.name))
                    new_path = os.path.join(self.project_path, 'worlds', 
                                            self.slugify(new_name))
                    
                    if os.path.exists(new_path):
                        self.cleanupWorldsDirectory(new_name)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        debug_log('Model.setData: Renamed world details directory.')

                    debug_log('Model.setData: Changing' + world.name + ' to ' + new_name)


                    world.name = new_name
                    
                
            elif column == COL:
                newCol = int(value)
                newPos = (newCol, world.row)
                if newPos != (world.col, world.row):
                    collided = False
                    for w in self.worlds:
                        if newPos == (w.col, w.row):
                            debug_log('Worlds Collided at ' + str(w.col) + ' ' + str(w.row))
                            collided = True
                    if not collided:
                        world.col = newCol
                
            elif column == ROW:
                newRow = int(value)
                newPos = (world.col, newRow)
                if newPos != (world.col, world.row):
                    collided = False
                    for w in self.worlds:
                        if newPos == (w.col, w.row):
                            debug_log('Worlds Collided at ' + str(w.col) + ' ' + str(w.row))
                            collided = True
                    if not collided:
                        world.row = newRow

            elif column == SECTOR_COORDS:
                pass
            
            elif column == OWNING_SECTOR:
                pass

            elif column == OWNING_SUBSECTOR:
                pass

            elif column == ALLEGIANCE_CODE:
                new_index = value
                if world.allegiance != int(new_index):
                    world.allegiance.index = int(new_index)

            elif column == ALLEGIANCE_NAME:
                new_index = value
                if world.allegiance.index != int(new_index):
                    world.allegiance.index = int(new_index)

            elif column >= ATTRIBUTE_BASE:
                attribute_index = column - ATTRIBUTE_BASE

                if role == DESCRIPTION_ROLE:
                    if value != self.attributeDefinitions[attribute_index].description(world.attributes[attribute_index]):
                        self.storeTextData(world.name,
                                       self.attributeDefinitions[attribute_index].name + '.txt',
                                       str(value))
                else:
                    debug_log('Attempt to set column ' + str(column) +' value to ' + str(value))
                    new_code_index = value
                    new_code = self.attributeDefinitions[attribute_index].codes[new_code_index]
                    old_code = world.attributes[attribute_index]
                    
                    if new_code != old_code:
                        # Check for custom Description text first
                        attribute_definition = self.attributeDefinitions[attribute_index]
                        old_path = os.path.join(self.project_path, 'worlds',
                                                 self.slugify(world.name),
                                                 attribute_definition.name + '.txt')

                        if os.path.exists(old_path):
                            ret = QMessageBox.question(QWidget(), 'Discard Custom Description',
                                                       'This attribute has a custom description. ' +\
                                                       'If you apply the change we will try to back it up, ' +\
                                                       'but previously backed up descriptions will be lost.',
                                                       QMessageBox.Apply,
                                                       QMessageBox.Cancel)
                            if ret == QMessageBox.Apply:
                                debug_log('World Model:User chose to override custom description and change attribute value.')
                                head, tail = os.path.split(old_path)
                                new_path = os.path.join(head, tail + '.bak')
                                try:
                                    shutil.copyfile(old_path, new_path)
                                except:
                                    debug_log('World Model: Exception thrown while trying to back up custom description ' +\
                                              str(old_path))
                                os.remove(old_path)
                                world.attributes[attribute_index] = new_code
                            elif ret == QMessageBox.Cancel:
                                debug_log('World Model: User cancelled change to atribute to preserve custom description.')
                                return False
                        else:
                            world.attributes[attribute_index] = new_code
                    else:
                        return False
            
            self.dirty = True
            modelIndex1 = self.index(index.row(), 0)
            modelIndex2 = self.index(index.row(), self.lastColumn)
            #self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
            #          modelIndex1, modelIndex2)
            self.dataChanged.emit(modelIndex1, modelIndex2)
            
            return True
        return False

    @logmethod
    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position,
                             position)
        #Code supporting multiple row insert removed. Only one at a time.
        current_xy = self.currentCell
        col = current_xy[0]
        row = current_xy[1]

        #if self.auto_name and len(self.world_name_list) > 0:
        #    name_number = random.randint(0, (len(self.world_name_list) - 1))
        #    name = self.world_name_list.pop(name_number)
        if self.auto_name:
            name = self.createWorldName(True)
        else:
            if len(self.world_name_list) == 0:
                debug_log('Models.insertRows: Run out of world names!')
            name = str(col + 500).zfill(3) + ':' + str(row + 500).zfill(3)
        
        for world in self.worlds:
            if name == world.name:
                debug_log('Models.insertRows: Name Clash creating world ' + name)
                return False

        self.worlds.insert(position, Foundation.World(name, col, row))
        
        self.endInsertRows()
        self.regenerateWorld(position)
        self.network_model.addNode((col, row))
        
        self.dirty = True
        return True

    @logmethod
    def removeRows(self, position, rows=1, index=QModelIndex()):
        debug_log("About to remove row(s).")
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        debug_log("Removing row(s).")
        worlds_to_delete = self.worlds[position:(position + rows)]
        self.deleted_worlds.extend(worlds_to_delete)
        
        self.worlds = self.worlds[:position] + \
                     self.worlds[position + rows:]

        self.endRemoveRows()

        # This should probably be done via a view on the world model
        for world in worlds_to_delete:
            self.network_model.removeNode((world.col, world.row))
        
        self.dirty = True
        return True


    def loadSectors(self):
        debug_log('Loading Sectors')
        exception = None
        f = open(self.sectors_file, "r")
        self.sectors = []
        try:
            reader = csv.reader(f, dialect='excel')
            for line in reader:
                if line[0] != "Sector Name":
                    name, column, row = line[0], int(line[1]), int(line[2])
                    if  0 <= column <= (self.secsWide - 1) and \
                           0 <= row <= (self.secsHigh - 1):
                        self.sectors.append(Foundation.Sector(name, column, row))
                    else:
                        debug_log('Sector outside grid: ' + str(name))
                        debug_log('secsWide = ' + str(self.secsWide) + \
                                  '    secsHigh = ' + str(self.secsHigh))
                        debug_log('')
                                  
        except IOError, e:
            exception = e
            debug_log(e)
        finally:
            f.close()

            def hasSectorAt(x, y):
                for sector in self.sectors:
                    if sector.sectorCol == x and sector.sectorRow == y:
                        return True
                return False

            for x in range(self.secsWide):
                for y in range(self.secsHigh):
                    if not hasSectorAt(x, y):
                        name = 'Sector ' + str(x + 10) + '/' + str(y + 10)
                        self.sectors.append(Foundation.Sector(name, x, y))
                        
            #self.dirty = False
            #self.reset()
        
    def loadSubsectors(self):
        debug_log('Loading Subsectors')
        exception = None
        f = open(self.subsectors_file, "r")
        self.subsectors = []
        try:
            reader = csv.reader(f, dialect='excel')
            for line in reader:
                if line[0] != "Subsector Name":
                    name, column, row = line[0], int(line[1]), int(line[2])
                    if 0 <= column <= ((self.secsWide * 4) - 1) and \
                            0 <= row <= ((self.secsHigh * 4) - 1):
                        self.subsectors.append(Foundation.Subsector(name, column, row))
                    else:
                        debug_log('Subsector outside grid: ' + str(name))
                        debug_log('secsWide = ' + str(self.secsWide) + \
                                  '    secsHigh = ' + str(self.secsHigh))
                        debug_log('Subsector col= ' + str(column) + '    ' + \
                                  'Subsector row= ' + str(row))
        except IOError, e:
            exception = e
            debug_log(e)
        finally:
            f.close()

            def hasSubsectorAt(x, y):
                for sub in self.subsectors:
                    if sub.subsectorCol == x and sub.subsectorRow == y:
                        return True
                return False

            for x in range(self.secsWide * 4):
                for y in range(self.secsHigh * 4):
                    if not hasSubsectorAt(x, y):
                        sx = x; sy = y
                        while sx >= 4:
                            sx = sx - 4
                        while sy >= 4:
                            sy = sy - 4
                        name = str(self.owningSector((x * 8), (y * 10))) + \
                               ': ' + str(sx) + '/' + str(sy)
                        self.subsectors.append(Foundation.Subsector(name, x, y))
            #self.dirty = False
            #self.reset()

    @logmethod
    def loadWorlds(self):
        
        def checkYesNo(text):
            if text == 'Yes': return True
            else: return False
        
        exception = None
        f = open(self.worlds_file, "r")
        self.worlds = []
        try:
            reader = csv.reader(f, dialect='excel')
            reader.next()      # Skip header line
            for line in reader:
                #print line
                world = Foundation.World(
                    name=line[0],
                    x=line[1],
                    y=line[2],
                    allegiance=line[3],
                    attributes=line[4:]
                    )
##                world = Foundation.World(
##                    name=line['World Name'],
##                    x=int(line['Column']),
##                    y=int(line['Row']),
##                    allegiance=line['Allegiance'],
##                    attributes=list(line['Attributes'])
##                    )
                #Check there are enough attributes      #####
                if len(world.attributes) < len(self.attributeDefinitions):
                    debug_log("World " + world.name + "has too few attributes")
                    debug_log("Undefined attributes will default to code '0'")
                    names = ''
                    for definition in self.attributeDefinitions:
                        names += definition.name + ' '

                #world.recalculateTradeCodes()
                self.worlds.append(world)
                #debug_log(self.getUWP(len(self.worlds) - 1))

        except IOError, e:
            exception = e
        finally:
            f.close()
            self.dirty = False
            self.reset()
            
        debug_log('Loading custom user text.')
        # Load custom user text
        for world in self.worlds:
            world_path = os.path.join(self.project_path, 'worlds',  self.slugify(world.name))
            if os.path.exists(world_path):
                pass
##                filepath = os.path.join(world_path,'Starport.txt')
##                if os.path.exists(filepath):
##                    world.starport.userText = self.retrieveTextData(world.name, 'Starport.txt')

        debug_log('Loading world link data')
        # Load World Link data
        link_filename = os.path.join(self.project_path, 'NetworkData.dat')
        if os.path.exists(link_filename):
            with open(link_filename, "r") as link_file:
                link_types = pickle.load(link_file)
                self.network_model.setLinkTypes(link_types)
                
                node_list = pickle.load(link_file)
                self.network_model.addNodes(node_list)
                
                link_data = pickle.load(link_file)
                self.network_model.addLinks(link_data)
                debug_log("WorldModel: Links Added")
                #self.network_model.graph.add_edges_from(pickle.load(link_file))

        # Check World Link Nodes
##        count = 0
##        for world in self.worlds:
##            if (world.col, world.row) not in self.network_model.nodes:
##                debug_log('World not in Links database: ' +\
##                          world.name +\
##                          str((world.col, world.row)))
##                self.network_model.addNode((world.col, world.row))
##                count += 1
##        if count > 0:
##            debug_log('Added ' + str(count) + ' missing worlds to Links database.')

        # Load Cell Region data
        debug_log('Loading Cell Region data')
        region_filename = os.path.join(self.project_path, 'HexRegionData.dat')
        if os.path.exists(region_filename):
            with open(region_filename, "rb") as region_file:
                self.hexRegionNames = pickle.load(region_file)
                self.hexRegionCells = pickle.load(region_file)

        # Prune existing world names from the world names list
        for world in self.worlds:
            if world.name in self.world_name_list:
                self.world_name_list.remove(world.name)
        debug_log('WorldModel: Pruned existing world names from world_names_list: ' + str(len(self.world_name_list)) + ' names remaining.')


    @logmethod
    def save(self):
        # Save world data
        
        def setYesNo(value):
            if value: return 'Yes'
            else: return 'No'

        # Clean up custom directories for deleted worlds
        for world in self.deleted_worlds:
            self.cleanupWorldsDirectory(world.name)

        # Save worlds csv file
        exception = None
        f = open(self.worlds_file, "wb")
        try:
            writer = csv.writer(f,
                                dialect='excel')
            writer.writerow(FIELD_NAMES)
            for world in self.worlds:
                writer.writerow( [world.name,
                                  world.col,
                                  world.row,
                                  world.allegiance,
                                  ] + world.attributes)
        except IOError,  e:
            exception = e
        finally:
            f.close()

        # Save custom user text
        for world in self.worlds:
            if world.dirty:
                world.dirty = False
##                if world.starport.userTextChanged:
##                    world.starport.userTextChanged = False
##                    self.storeTextData(world.name,
##                                       'Starport.txt',
##                                       world.starport.userText)


        # Save Sector Data
        exception = None
        f = open(self.sectors_file, "wb")
        try:
            writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow( ('Sector Name',  'Column',  'Row') )
            for sector in self.sectors:
                writer.writerow( (sector.name,
                                  sector.sectorCol,
                                  sector.sectorRow) )
        except IOError,  e:
            exception = e
        finally:
            f.close()

        # Save Subsector Data
        exception = None
        f = open(self.subsectors_file, "wb")
        try:
            writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow( ('Subsector Name',  'Column',  'Row') )
            for subsector in self.subsectors:
                writer.writerow( (subsector.name,
                                  subsector.subsectorCol,
                                  subsector.subsectorRow) )
        except IOError,  e:
            exception = e
        finally:
            f.close()

        # Save World Link data
        link_filename = os.path.join(self.project_path, 'NetworkData.dat')
        with open(link_filename, "wb") as link_file:
            pickle.dump(self.network_model.oldLinkTypes, link_file, 0)
            pickle.dump(self.network_model.nodes, link_file, 0)
            pickle.dump(self.network_model.oldLinks, link_file, 0)
        debug_log('Nodes and Links saved')

        # Save Region data
        region_filename = os.path.join(self.project_path, 'HexRegionData.dat')
        with open(region_filename, "wb") as region_file:
            pickle.dump(self.hexRegionNames, region_file, 2)
            pickle.dump(self.hexRegionCells, region_file, 2)
        debug_log('Cell Regions saved')

        # Save Config Data
        self.config.set('Overrides', 'allegiancecodes',
                        ','.join(Foundation.allegiance_codes))
        self.config.set('Overrides', 'allegiancenames',
                        ','.join(Foundation.allegiance_names))
        self.config.set('Overrides', 'allegiancecolors',
                        ','.join(Foundation.allegiance_colors))
        self.config.set('Overrides', 'worldgeneratorname', self.currentWorldGeneratorName)
        self.config.write(open(self.config_file, "w"))



    def createNewProject(self, width=2, height=2, project_path=None):
        sectors = 'Sector Name,Column,Row\n'
        subsectors = 'Subsector Name,Column,Row\n'
        worlds = ''
        for field in FIELD_NAMES:
            worlds = worlds + field + ','
        #worlds = worlds + 'Attributes' + ',' + '\n'
        secs_wide = width
        secs_high = height

        for sec_row in range(secs_high):
            for sec_column in range(secs_wide):
                sec_name = 'Sec' + str((sec_column + 1) + (sec_row * secs_wide))
                sectors += sec_name + ',' + str(sec_column) + ',' +  str(sec_row) + '\n'

                for sub_row in range(4):
                    for sub_col in range(4):
                        sub_name = sec_name + 'Sub' + str((sub_col + 1) + (sub_row * 4))
                        subsectors += sub_name + ',' + str(sub_col) + ',' + str(sub_row) + '\n'

        with open(os.path.join(project_path, 'worlds.csv'), 'w') as world_file:
            world_file.write(worlds)

        with open(os.path.join(project_path, 'sectors.csv'), 'w') as sectors_file:
            sectors_file.write(sectors)

        with open(os.path.join(project_path, 'subsectors.csv'), 'w') as subsectors_file:
            subsectors_file.write(subsectors)

        sbconf = SafeConfigParser()
        sbconf.add_section('Files')
        sbconf.set('Files', 'worldsfile', 'worlds.csv')
        sbconf.set('Files', 'sectorsfile', 'sectors.csv')
        sbconf.set('Files', 'subsectorsfile', 'subsectors.csv')

        sbconf.add_section('Map')
        sbconf.set('Map', 'sectorgridheight', str(height))
        sbconf.set('Map', 'sectorgridwidth', str(width))

        sbconf.add_section('Overrides')

        sbconf.add_section('Display')
        sbconf.set('Display', 'zoomlevel', '2')
        sbconf.set('Display', 'horizontalscroll', '100')
        sbconf.set('Display', 'verticalscroll', '100')

        sbconf.add_section('Options')
        sbconf.set('Options', 'codedlabels', str(self.codedLabels))

        with open(os.path.join(project_path, 'starbase.ini'), 'w') as starbase_file:
            sbconf.write(starbase_file)

        project_name = os.path.split(project_path)[-1]
        return project_name


# Still under development

    def importSEC(self, import_file, sec_col, sec_row):
        #Assumes the sector has been blanked already

        base_col = sec_col * 32
        base_row = sec_row * 40

        sub_map = {'A' : (0, 0),
                   'B' : (1, 0),
                   'C' : (2, 0),
                   'D' : (3, 0),
                   'E' : (0, 1),
                   'F' : (1, 1),
                   'G' : (2, 1),
                   'H' : (3, 1),
                   'I' : (0, 2),
                   'J' : (1, 2),
                   'K' : (2, 2),
                   'L' : (3, 2),
                   'M' : (0, 3),
                   'N' : (1, 3),
                   'O' : (2, 3),
                   'P' : (3, 3)}

        # 0:Navy, 1:Scout
        base_codes = {'A' : (True, True),
                      'N' : (True, False),
                      'S' : (False, True)}

        travel_zone_lookup = {'A' : 'Amber',
                              'R' : 'Red',
                              ' ' : 'Green'}
        
        with open(import_file, "r") as secfile:
            all_lines = secfile.readlines()
            
            #Discard first two lines of the file
            for line in all_lines[2:]:
                debug_log(line)
                if len(line) < 3:
                    debug_log('Short line')
                
                elif line[0] == '#' and line[2] == ':':
                    #Set subsector name
                    if line[1] in sub_map:
                        col_offset, row_offset = sub_map[line[1]]
                        sub_name = line[4:]
                        sub_col = (sec_col * 4) + col_offset
                        sub_row = (sec_row * 4) + row_offset
                        debug_log('Setting subsector name: ' + sub_name)
                        debug_log(' subsector column: ' + str(sub_col))
                        debug_log(' subsector row:    ' + str(sub_row))
                        self.subsectors.append(Foundation.Subsector(
                            sub_name, sub_col, sub_row))
                    else:
                        debug_log('Sector import error, bad subsector: ' + line)

                elif line[0] == '+' and line[3] == ' ':
                    #Add allegiance config, if not already present
                    new_code = line[1:3]
                    new_name = line[4:]
                    if new_code not in Foundation.allegiance_codes:
                        debug_log('New allegiance: '
                                  + new_code + ' '
                                  + new_name)
                        Foundation.allegiance_codes.append(new_code)
                        Foundation.allegiance_names.append(new_name)
                        Foundation.allegiance_colors.append('#CCCCCC')

                elif line[0] not in ('#', '+'):
                    debug_log('Parsing world data line:')
                    debug_log(line)
                    
                    world_name = line[0:18].rstrip()
                    column = base_col + int(line[19:21]) - 1
                    row = base_row + int(line[21:23]) - 1
                    trade_list = (line[36:38], line[39:41], line[42:44],
                                  line[45:47], line[48:50])
                    hasNavy, hasScout = False, False
                    if line[34] in base_codes:
                        hasNavy, hasScout = base_codes[line[34]]
                    hasResearch = 'Rs' in trade_list
                    travel_zone = travel_zone_lookup[line[52]]
                    pop_multiplier = int(line[54])
                    num_belts = int(line[55])
                    num_gas_giants = int(line[56])
                    if num_gas_giants > 0:
                        hasGasGiant = True
                    else:
                        hasGasGiant = False
                    allegiance_code = line[58:60]

                    world = Foundation.World(
                        name=world_name,
                        x=column,
                        y=row,
                        port=line[24],
                        size=line[25],
                        atmosphere=line[26],
                        hydrographics=line[27],
                        population=line[28],
                        government=line[29],
                        law_level=line[30],
                        tech_level=line[32],
                        gas=hasGasGiant,
                        travel_code=travel_zone,
                        navy=hasNavy,
                        scout=hasScout,
                        research=hasResearch,
                        tas=False,
                        consulate=False,
                        pirate=False,
                        allegiance=allegiance_code,
                        port_txt='',
                        size_txt='',
                        atmo_txt='',
                        hydro_txt='',
                        pop_txt='',
                        gov_txt='',
                        law_txt='',
                        tech_txt='',
                        hydro_pc=None,
                        Ag='Ag' in trade_list,
                        As='As' in trade_list,
                        Ba='Ba' in trade_list,
                        De='De' in trade_list,
                        Fl='Fl' in trade_list,
                        Ga='Ga' in trade_list,
                        Hi='Hi' in trade_list,
                        Ht='Ht' in trade_list,
                        IC='IC' in trade_list,
                        In='In' in trade_list,
                        Lo='Lo' in trade_list,
                        Lt='Lt' in trade_list,
                        Na='Na' in trade_list,
                        NI='NI' in trade_list,
                        Po='Po' in trade_list,
                        Ri='Ri' in trade_list,
                        Va='Va' in trade_list,
                        Wa='Wa' in trade_list)

                    new_row = len(self.worlds)
                    self.beginInsertRows(QModelIndex(), new_row, new_row)
                    self.worlds.append(world)
                    self.endInsertRows()
                    debug_log(self.getUWP(len(self.worlds) - 1))
        self.dirty = True
