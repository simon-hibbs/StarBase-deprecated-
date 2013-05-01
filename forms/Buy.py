from PySide.QtCore import *
# Copyright 2013 Simon Dominic Hibbs

from PySide.QtGui import *
import os
from model import Models
from model import Foundation
##from starmap import MapGlyphs
##from starmap import MapGrid
import random
from log import *

def d6(num):
    total = 0
    for i in range(num):
        total += random.randint(1, 6)
    return total

TITLE_FONT = 16
HEADING_FONT = 11
BODY_FONT = 9

PASSAGE_COSTS = {1 : {'High' : 6000,
                      'Middle' : 3000,
                      'Low' : 1000},
                 2 : {'High' : 12000,
                      'Middle' : 6000,
                      'Low' : 1200},
                 3 : {'High' : 20000,
                      'Middle' : 10000,
                      'Low' : 1400},
                 4 : {'High' : 30000,
                      'Middle' : 15000,
                      'Low' : 1600},
                 5 : {'High' : 40000,
                      'Middle' : 20000,
                      'Low' : 1800},
                 6 : {'High' : 50000,
                      'Middle' : 25000,
                      'Low' : 2000}
                 }

AVAILABLE_PASSENGERS = {0 : {'Low' : 0,
                             'Middle' : 0,
                             'High' : 0},
                        1 : {'Low' : d6(2) - 6,
                             'Middle' : d6(1) - 2,
                             'High' : 0},
                        2 : {'Low' : d6(2),
                             'Middle' : d6(1),
                             'High' : d6(1) - d6(1)},
                        3 : {'Low' : d6(2),
                             'Middle' : d6(2) - d6(1),
                             'High' : d6(2)- d6(2)},
                        4 : {'Low' : d6(3) - d6(1),
                             'Middle' : d6(2) - d6(1),
                             'High' : d6(2) - d6(1)},
                        5 : {'Low' : d6(3) - d6(1),
                             'Middle' : d6(3) - d6(2),
                             'High' : d6(2) - d6(1)},
                        6 : {'Low' : d6(3),
                             'Middle' : d6(3) - d6(2),
                             'High' : d6(3) - d6(2)},
                        7 : {'Low' : d6(3),
                             'Middle' : d6(3) - d6(1),
                             'High' : d6(3) - d6(2)},
                        8 : {'Low' : d6(4),
                             'Middle' : d6(3) - d6(1),
                             'High' : d6(3) - d6(1)},
                        9 : {'Low' : d6(4),
                             'Middle' : d6(3),
                             'High' : d6(3) - d6(1)},
                        10 : {'Low' : d6(5),
                             'Middle' : d6(3),
                             'High' : d6(3) - d6(1)},
                        11 : {'Low' : d6(5),
                             'Middle' : d6(4),
                             'High' : d6(3)},
                        12 : {'Low' : d6(6),
                             'Middle' : d6(4),
                             'High' : d6(3)},
                        13 : {'Low' : d6(6),
                             'Middle' : d6(4),
                             'High' : d6(4)},
                        14 : {'Low' : d6(7),
                             'Middle' : d6(5),
                             'High' : d6(4)},
                        15 : {'Low' : d6(8),
                             'Middle' : d6(5),
                             'High' : d6(4)},
                        16 : {'Low' : d6(9),
                             'Middle' : d6(6),
                             'High' : d6(5)}}

AVAILABLE_FREIGHT = {0 : {'Incidental' : 0,
                          'Minor' : 0,
                          'Major' : 0},
                     1 : {'Incidental' : 0,
                          'Minor' : d6(1) - 4,
                          'Major' : d6(1) - 4},
                     2 : {'Incidental' : 0,
                          'Minor' : d6(1) - 1,
                          'Major' : d6(1) - 2},
                     3 : {'Incidental' : 0,
                          'Minor' : d6(1),
                          'Major' : d6(1) - 1},
                     4 : {'Incidental' : 0,
                          'Minor' : d6(1) + 1,
                          'Major' : d6(1)},
                     5 : {'Incidental' : 0,
                          'Minor' : d6(1) + 2,
                          'Major' : d6(1) + 1},
                     6 : {'Incidental' : 0,
                          'Minor' : d6(1) + 3,
                          'Major' : d6(1) + 2},
                     7 : {'Incidental' : 0,
                          'Minor' : d6(1) + 4,
                          'Major' : d6(1) + 3},
                     8 : {'Incidental' : 0,
                          'Minor' : d6(1) + 5,
                          'Major' : d6(1) + 4},
                     9 : {'Incidental' : d6(1) - 2,
                          'Minor' : d6(1) + 6,
                          'Major' : d6(1) + 5},
                     10 : {'Incidental' : d6(1),
                          'Minor' : d6(1) + 7,
                          'Major' : d6(1) + 6},
                     11 : {'Incidental' : d6(1) + 1,
                          'Minor' : d6(1) + 8,
                          'Major' : d6(1) + 7},
                     12 : {'Incidental' : d6(1) + 2,
                          'Minor' : d6(1) + 9,
                          'Major' : d6(1) + 8},
                     13 : {'Incidental' : d6(1) + 3,
                          'Minor' : d6(1) + 10,
                          'Major' : d6(1) + 9},
                     14 : {'Incidental' : d6(1) + 4,
                          'Minor' : d6(1) + 12,
                          'Major' : d6(1) + 10},
                     15 : {'Incidental' : d6(1) + 5,
                          'Minor' : d6(1) + 14,
                          'Major' : d6(1) + 11},
                     16 : {'Incidental' : d6(1) + 6,
                          'Minor' : d6(1) + 16,
                          'Major' : d6(1) + 12}}
        
TRADE_GOODS = {'Basic Electronics' : {'Codes' : 'All',
                                      'Size' : 10,
                                      'Price' : 10000,
                                      'Purchase DMs' : {'In' : 2,
                                                        'Ht' : 3,
                                                        'Ri' : 1},
                                      'Sale DMs' : {'NI' : 2,
                                                    'Lt' : 1,
                                                    'Po' : 1}},
               'Basic Machine Parts' : {'Codes' : 'All',
                                        'Size' : 10,
                                        'Price' : 10000,
                                        'Purchase DMs' : {'Na' : 2,
                                                          'In' : 5},
                                        'Sale DMs' : {'NI' : 3,
                                                      'Ag' : 2}},
               'Basic Manufactured Goods' : {'Codes' : 'All',
                                             'Size' : 10,
                                             'Price' : 10000,
                                             'Purchase DMs' : {'Na' : 2,
                                                               'In' : 5},
                                             'Sale DMs' : {'NI' : 3,
                                                           'Hi' : 2}},
               'Basic Raw Materials' : {'Codes' : 'All',
                                                  'Size' : 10,
                                                  'Price' : 5000,
                                                  'Purchase DMs' : {'Ag' : 3,
                                                                    'Ga' : 2},
                                                  'Sale DMs' : {'In' : 2,
                                                                'Po' : 2}},
               'Basic Consumables' : {'Codes' : 'All',
                                      'Size' : 10,
                                      'Price' : 2000,
                                      'Purchase DMs' : {'Ag' : 3,
                                                        'Wa' : 2,
                                                        'Ga' : 1,
                                                        'As' : -4},
                                      'Sale DMs' : {'As' : 1,
                                                    'Fl' : 1,
                                                    'IC' : 1,
                                                    'Hi' : 1}},
               'Basic Ore' : {'Codes' : 'All',
                                        'Size' : 10,
                                        'Price' : 1000,
                                        'Purchase DMs' : {'As' : 4,
                                                          'IC' : 0},
                                        'Sale DMs' : {'In' : 3,
                                                      'Ni' : 1}},
               'Advanced Electronics' : {'Codes' : ('In', 'Ht'),
                                                   'Size' : 5,
                                                   'Price' : 100000,
                                                   'Purchase DMs' : {'In' : 2,
                                                                     'Ht' : 3},
                                                   'Sale DMs' : {'NI' : 1,
                                                                 'Ri' : 2,
                                                                 'As' : 2}},
               'Advanced Machine Parts' : {'Codes' : ('In', 'Ht'),
                                                     'Size' : 5,
                                                     'Price' : 75000,
                                                     'Purchase DMs' : {'In' : 2,
                                                                       'Ht' : 1},
                                                     'Sale DMs' : {'As' : 2,
                                                                   'NI' : 1}},
               'Advanced Manufactured Goods' : {'Codes' : ('In', 'Ht'),
                                                          'Size' : 5,
                                                          'Price' : 100000,
                                                          'Purchase DMs' : {'In' : 1,
                                                                            'Ht' : 0},
                                                          'Sale DMs' : {'Hi' : 1,
                                                                        'Ri' : 2}},
               'Advanced Weapons' : {'Codes' : ('In', 'Ht'),
                                     'Size' : 5,
                                     'Price' : 150000,
                                     'Purchase DMs' : {'In' : 0,
                                                       'Ht' : 2},
                                     'Sale DMs' : {'Po' : 1,
                                                   'Az' : 2,
                                                   'Rz' : 4}},
               'Advanced Vehicles' : {'Codes' : ('In', 'Ht'),
                                      'Size' : 5,
                                      'Price' : 180000,
                                      'Purchase DMs' : {'In' : 0,
                                                        'Ht' : 2},
                                      'Sale DMs' : {'As' : 2,
                                                    'Ri' : 2}},
               'Biochemicals' : {'Codes' : ('Ag', 'Wa'),
                                 'Size' : 5,
                                 'Price' : 50000,
                                 'Purchase DMs' : {'Ag' : 1,
                                                   'Wa' : 2},
                                 'Sale DMs' : {'In' : 2}},
               'Crystals and Gems' : {'Codes' : ('As', 'De', 'IC'),
                                      'Size' : 5,
                                      'Price' : 20000,
                                      'Purchase DMs' : {'As' : 2,
                                                        'De' : 1,
                                                        'IC' : 1},
                                      'Sale DMs' : {'In' : 3,
                                                    'Ri' : 2}},
               'Cybernetics' : {'Codes' : ('Ht'),
                                'Size' : 1,
                                'Price' : 250000,
                                'Purchase DMs' : {'Ht' : 0},
                                'Sale DMs' : {'As' : 1,
                                              'IC' : 1,
                                              'Ri' : 2}},
               'Live Animals' : {'Codes' : ('Ag', 'Ga'),
                                 'Size' : 10,
                                 'Price' : 20000,
                                 'Purchase DMs' : {'Ag' : 2,
                                                   'Ga' : 0},
                                 'Sale DMs' : {'Lo' : 3}},
               'Luxury Consumables' : {'Codes' : ('Ag', 'Ga', 'Wa'),
                                       'Size' : 10,
                                       'Price' : 20000,
                                       'Purchase DMs' : {'Ag' : 2,
                                                         'Ga' : 0,
                                                         'Wa' : 1},
                                       'Sale DMs' : {'Ri' : 2,
                                                     'Hi' : 2}},
               'Luxury Goods' : {'Codes' : ('Hi'),
                                 'Size' : 1,
                                 'Price' : 200000,
                                 'Purchase DMs' : {'Hi' : 0},
                                 'Sale DMs' : {'Ri' : 4}},
               'MedicalSupplies' : {'Codes' : ('Ht', 'Hi'),
                                    'Size' : 5,
                                    'Price' : 50000,
                                    'Purchase DMs' : {'Ht' : 2,
                                                      'Hi' : 0},
                                    'Sale DMs' : {'In' : 2,
                                                  'Po' : 1,
                                                  'Ri' : 1}},
               'Petrochemicals' : {'Codes' : ('De', 'Fl', 'IC', 'Wa'),
                                   'Size' : 10,
                                   'Price' : 10000,
                                   'Purchase DMs' : {'De' : 2,
                                                     'Fl' : 0,
                                                     'IC' : 0,
                                                     'Wa' : 0},
                                   'Sale DMs' : {'In' : 2,
                                                 'Ag' : 1,
                                                 'Lt' : 2}},
               'Pharmaceuticals' : {'Codes' : ('As', 'De', 'Hi', 'Wa'),
                                    'Size' : 1,
                                    'Price' : 10000,
                                    'Purchase DMs' : {'As' : 2,
                                                      'De' : 0,
                                                      'Hi' : 1,
                                                      'Wa' : 0},
                                    'Sale DMs' : {'Ri' : 2,
                                                  'Lt' : 1}},
               'Polymers' : {'Codes' : ('In'),
                             'Size' : 10,
                             'Price' : 7000,
                             'Purchase DMs' : {'In' : 0},
                             'Sale DMs' : {'Ri' : 2,
                                           'NI' : 1}},
               'Precious Metals' : {'Codes' : ('As', 'De', 'IC', 'Fl'),
                                    'Size' : 1,
                                    'Price' : 50000,
                                    'Purchase DMs' : {'As' : 3,
                                                      'De' : 1,
                                                      'IC' : 2,
                                                      'Fl' : 0},
                                    'Sale DMs' : {'Ri' : 3,
                                                  'In' : 2,
                                                  'Ht' : 1}},
               'Radioactives' : {'Codes' : ('As', 'De', 'Lo'),
                                 'Size' : 1,
                                 'Price' : 1000000,
                                 'Purchase DMs' : {'As' : 2,
                                                   'De' : 0,
                                                   'Lo' : -4},
                                 'Sale DMs' : {'In' : 3,
                                               'Ht' : 1,
                                               'NI' : -2,
                                               'Ag' : -3}},
               'Robots' : {'Codes' : ('In', 'Ht'),
                           'Size' : 5,
                           'Price' : 4000000,
                           'Purchase DMs' : {'In' : 0},
                           'Sale DMs' : {'Ag' : 2,
                                         'Ht' : 1}},
               }




class BuyDialog(QDialog):
    def __init__(self, model, parent=None):
        super(BuyDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Available Cargo')
        self.model = model

        self.salesList = TradeReport(self.model)

        self.editor = QTextEdit()
        self.editor.setDocument(self.salesList.document)

##        self.rerollButton = QPushButton('Reroll Cargo')
        self.pdfButton = QPushButton('Save As PDF')
        self.closeButton = QPushButton('Close')

        buttonLayout = QVBoxLayout()
##        buttonLayout.addWidget(self.rerollButton)
        buttonLayout.addWidget(self.pdfButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.closeButton)

        layout = QHBoxLayout()
        layout.addWidget(self.editor)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

##        self.connect(self.rerollButton, SIGNAL("clicked()"),
##                     self.generateCargo)
        self.connect(self.pdfButton, SIGNAL("clicked()"),
                     self.exportToPdf)
        self.connect(self.closeButton, SIGNAL("clicked()"),
                     self.closeButtonClicked)

    def exportToPdf(self):
        pass

    def closeButtonClicked(self):
        self.result = None
        self.close()

        
class TradeReport(object):
    def __init__(self, model):
        self.model = model

        self.saleData = Goods(model)

        self.document = QTextDocument()
        cursor = QTextCursor(self.document)

        debug_log('TradeReport: Configuring document formats.')

        title_text_format = QTextCharFormat()
        title_text_format.setFont(QFont('Helvetica',
                                        TITLE_FONT,
                                        QFont.Bold))
        title_block_format = QTextBlockFormat()
        title_block_format.setTopMargin(TITLE_FONT)
        title_block_format.setBottomMargin(TITLE_FONT)

        heading_text_format = QTextCharFormat()
        heading_text_format.setFont(QFont('Helvetica',
                                        HEADING_FONT,
                                        QFont.Bold))
        heading_block_format = QTextBlockFormat()
        heading_block_format.setTopMargin(HEADING_FONT)
        heading_block_format.setBottomMargin(HEADING_FONT / 2)

        body_text_format = QTextCharFormat()
        body_text_format.setFont(QFont('Helvetica',
                                      BODY_FONT,
                                      QFont.Normal))
        body_block_format = QTextBlockFormat()
        body_block_format.setAlignment(Qt.AlignTop)
        body_block_format.setBottomMargin(0)
        body_block_format.setIndent(1)

        details_table_format = QTextTableFormat()
        details_table_format.setCellSpacing(0)
        details_table_format.setCellPadding(3)
        #details_table_format.setBorderBrush(QBrush(Qt.transparent))

        # Document Title
        debug_log('TradeReport: Beginning text generation.')
        cursor.setBlockFormat(title_block_format)
        cursor.insertText('Available Goods', title_text_format)

        #Route Info
        cursor.insertBlock()
        cursor.setBlockFormat(heading_block_format)
        cursor.insertText('Route Information',
                          heading_text_format)
        table = cursor.insertTable(3, 2, details_table_format)
        
        cell = table.cellAt(0, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('World of Origin:', body_text_format)
        cell = table.cellAt(0, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(self.saleData.fromWorldName, body_text_format)
        
        cell = table.cellAt(1, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Destination World:', body_text_format)
        cell = table.cellAt(1, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(self.saleData.toWorldName, body_text_format)
        
        cell = table.cellAt(2, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Jump Distance:', body_text_format)
        cell = table.cellAt(2, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(str(self.saleData.distance), body_text_format)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        # Passengers
        cursor.insertBlock()
        cursor.setBlockFormat(heading_block_format)
        cursor.insertText('Passengers bound for ' + \
                          str(self.saleData.toWorldName),
                          heading_text_format)
        
        table = cursor.insertTable(4, 4, details_table_format)

        cell = table.cellAt(0, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Ticket Type', body_text_format)
        cell = table.cellAt(0, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Passengers Available', body_text_format)
        cell = table.cellAt(0, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Passage Cost', body_text_format)
        cell = table.cellAt(0, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Steward Skill Required\n' + \
                              '(Including Level 0)', body_text_format)

        cell = table.cellAt(1, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('High Passage:', body_text_format)
        cell = table.cellAt(1, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(str(self.saleData.highPassengers),
                              body_text_format)
        cell = table.cellAt(1, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Cr: ' + str(self.saleData.highPassageCost),
                              body_text_format)
        cell = table.cellAt(1, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(str(self.saleData.highStewardLevel),
                               body_text_format)
        
        cell = table.cellAt(2, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Middle Passage:', body_text_format)
        cell = table.cellAt(2, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(str(self.saleData.middlePassengers),
                              body_text_format)
        cell = table.cellAt(2, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Cr: ' + str(self.saleData.middlePassageCost),
                              body_text_format)
        cell = table.cellAt(2, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(str(self.saleData.middleStewardLevel),
                               body_text_format)

        cell = table.cellAt(3, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Low Passage:', body_text_format)
        cell = table.cellAt(3, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(str(self.saleData.lowPassengers),
                              body_text_format)
        cell = table.cellAt(3, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Cr: ' + str(self.saleData.lowPassageCost),
                              body_text_format)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        # Mail
        cursor.insertBlock()
        cursor.setBlockFormat(heading_block_format)
        cursor.insertText('Mail Availability', heading_text_format)

        table = cursor.insertTable(1, 2, details_table_format)

        cell = table.cellAt(0, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Mail to ' + \
                          str(self.saleData.toWorldName) + ':',
                              body_text_format)
        if self.saleData.mailAvailable:
            mail_text = 'Yes'
        else:
            mail_text = 'No'
        cell = table.cellAt(0, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(mail_text, body_text_format)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        #Freight
        print self.saleData.freightList
        cursor.insertBlock()
        cursor.setBlockFormat(heading_block_format)
        cursor.insertText('Freight Lots bound for ' + \
                          str(self.saleData.toWorldName),
                          heading_text_format)
        
        table = cursor.insertTable(len(self.saleData.freightList), 3,
                                   details_table_format)

##        cell = table.cellAt(0, 0)
##        cellCursor = cell.firstCursorPosition()
##        cellCursor.insertText('', body_text_format)
##        cell = table.cellAt(0, 1)
##        cellCursor = cell.firstCursorPosition()
##        cellCursor.insertText('Tons', body_text_format)
##        cell = table.cellAt(0, 2)
##        cellCursor = cell.firstCursorPosition()
##        cellCursor.insertText('Fee', body_text_format)

        row = 0
        for lot in self.saleData.freightList:
            cell = table.cellAt(row, 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText('Lot ' + str(row + 1), body_text_format)
            cell = table.cellAt(row, 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(str(lot[0]) + ' tons', body_text_format)
            cell = table.cellAt(row, 2)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText('Cr ' + str(lot[1]), body_text_format)
            row += 1
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)



class Goods(object):
    def __init__(self, model):
        
        fromWorld = model.getWorld(model.fromTradeWorldPmi)
        toWorld = model.getWorld(model.toTradeWorldPmi)

        self.distance = model.getDistance(
            (fromWorld.col, fromWorld.row), (toWorld.col, toWorld.row))
        debug_log('Buy Goods: Trade distance = ' + str(self.distance))

        self.fromWorldName = fromWorld.name
        self.toWorldName = toWorld.name

        passenger_mod = 0
        if fromWorld.tradeAs: passenger_mod += 1
        if fromWorld.tradeBa: passenger_mod -= 5
        if fromWorld.tradeDe: passenger_mod -= 1
        if fromWorld.tradeGa: passenger_mod += 2
        if fromWorld.tradeIC: passenger_mod += 1
        if fromWorld.tradeIn: passenger_mod += 2
        if fromWorld.tradePo: passenger_mod -= 2
        if fromWorld.tradeRi: passenger_mod -= 1
        if fromWorld.travelCode == 'Amber': passenger_mod += 2
        if fromWorld.travelCode == 'Red': passenger_mod += 4
        passenger_mod += fromWorld.population.index
        
        if toWorld.tradeAs: passenger_mod += 1
        if toWorld.tradeBa: passenger_mod += 1
        if toWorld.tradeDe: passenger_mod += 1
        if toWorld.tradeGa: passenger_mod += 1
        if toWorld.tradeHi: passenger_mod += 1
        if toWorld.tradeIC: passenger_mod += 1
        if toWorld.tradeIn: passenger_mod += 1
        if toWorld.tradeLo: passenger_mod += 1
        if toWorld.tradeNI: passenger_mod += 1
        if toWorld.tradePo: passenger_mod += 1
        if toWorld.tradeRi: passenger_mod += 1
        if toWorld.travelCode == 'Amber': passenger_mod -= 2
        if toWorld.travelCode == 'Red': passenger_mod -= 4
        passenger_mod += toWorld.population.index

        # Modifier for Carouse or Streetwise checks?

        if passenger_mod > 16: passenger_mod = 16
        
        self.lowPassengers = AVAILABLE_PASSENGERS[passenger_mod]['Low']
        self.middlePassengers = AVAILABLE_PASSENGERS[passenger_mod]['Middle']
        self.highPassengers = AVAILABLE_PASSENGERS[passenger_mod]['High']

        debug_log('Goods: High/Mid/Low = ' + \
                  str(self.highPassengers) + '/' + \
                  str(self.middlePassengers) + '/' + \
                  str(self.lowPassengers))

        if self.lowPassengers < 0: self.lowPassengers = 0
        if self.middlePassengers < 0 : self.middlePassengers = 0
        if self.highPassengers < 0 : self.highPassengers = 0

        if self.highPassengers > 5:
            self.highStewardLevel = int((self.middlePassengers - 1) / 5)
        else:
            self.highStewardLevel = 0

        if self.middlePassengers > 2:
            self.middleStewardLevel = int((self.middlePassengers - 1) / 2)
        else:
            self.middleStewardLevel = 0

        if self.distance <= 6:
            self.lowPassageCost = PASSAGE_COSTS[self.distance]['Low']
            self.middlePassageCost = PASSAGE_COSTS[self.distance]['Middle']
            self.highPassageCost = PASSAGE_COSTS[self.distance]['High']
        else:
            self.lowPassageCost = 'Special'
            self.middlePassageCost = 'Special'
            self.highPassageCost = 'Special'

        debug_log('Goods: Passage Costs High/Mid/Low = ' + \
                  str(self.highPassageCost) + '/' + \
                  str(self.middlePassageCost) + '/' + \
                  str(self.lowPassageCost))

        freight_mod = 0
        if fromWorld.tradeAg: freight_mod += 2
        if fromWorld.tradeAs: freight_mod -= 3
        if fromWorld.tradeDe: freight_mod -= 3
        if fromWorld.tradeFl: freight_mod -= 3
        if fromWorld.tradeGa: freight_mod += 2
        if fromWorld.tradeHi: freight_mod += 2
        if fromWorld.tradeIC: freight_mod -= 3
        if fromWorld.tradeIn: freight_mod += 3
        if fromWorld.tradeLo: freight_mod -= 5
        if fromWorld.tradeNa: freight_mod -= 3
        if fromWorld.tradeNI: freight_mod -= 3
        if fromWorld.tradePo: freight_mod -= 3
        if fromWorld.tradeRi: freight_mod += 2
        if fromWorld.tradeWa: freight_mod -= 3
        if fromWorld.travelCode == 'Amber': freight_mod += 5
        if fromWorld.travelCode == 'Red': freight_mod -= 5

        if toWorld.tradeAg: freight_mod += 1
        if toWorld.tradeAs: freight_mod += 1
        if toWorld.tradeBa: freight_mod -= 5
        if toWorld.tradeGa: freight_mod += 1
        if toWorld.tradeIn: freight_mod += 2
        if toWorld.tradeNa: freight_mod += 1
        if toWorld.tradeNI: freight_mod += 1
        if toWorld.tradePo: freight_mod -= 3
        if toWorld.tradeRi: freight_mod += 2
        if toWorld.travelCode == 'Amber': freight_mod -= 5

        tech_mod = 0
        if fromWorld.techLevel.index > toWorld.techLevel.index:
            tech_mod = toWorld.techLevel.index - fromWorld.techLevel.index
        else:
            tech_mod = fromWorld.techLevel.index - toWorld.techLevel.index

        if tech_mod > 5: tech_mod = 5
        
        freight_mod = freight_mod - tech_mod
        if freight_mod > 16: freight_mod = 16
        if freight_mod < 0: freight_mod = 0
        if toWorld.travelCode == 'Red': freight_mod = 0

        incidental = AVAILABLE_FREIGHT[freight_mod]['Incidental']
        minor = AVAILABLE_FREIGHT[freight_mod]['Minor']
        major = AVAILABLE_FREIGHT[freight_mod]['Major']

        if incidental < 0: incidental = 0
        if minor < 0: minor = 0
        if major < 0: major = 0

        freight_list = []
        for lot in range(incidental):
            tons = d6(1)
            fee = tons * (1000 + (200 * (self.distance - 1)))
            freight_list.append((tons, fee))

        for lot in range(minor):
            tons = d6(1) * 5
            fee = tons * (1000 + (200 * (self.distance - 1)))
            freight_list.append((tons, fee))

        for lot in range(major):
            tons = d6(1) * 10
            fee = tons * (1000 + (200 * (self.distance - 1)))
            freight_list.append((tons, fee))

        self.freightList = freight_list

        mail_mod = 0
        if freight_mod <= -10 : mail_mod -= 2
        if -5 >= freight_mod >= -9 : mail_mod -= 1
        if 9 >= freight_mod >= 5 : mail_mod += 1
        if freight_mod >= 10 : mail_mod += 2

        # If armed, + 2
        # + naval or Scout rank
        # + Highest Soc

        if fromWorld.techLevel.index <= 5: mail_mod -= 4

        if (d6(2) + mail_mod) >= 12:
            self.mailAvailable = True
        else:
            self.mailAvailable = False

        debug_log('Goods: Calculations complete.')
