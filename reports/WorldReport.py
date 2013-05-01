# Copyright 2013 Simon Dominic Hibbs
from PySide.QtCore import *

from PySide.QtGui import *
import os
from model import Models, FromWorldLinkModel
from model import Foundation
from starmap import MapGlyphs
from starmap import MapGrid
from log import *


TITLE_FONT = 16
UPP_FONT = 10
HEADING_FONT = 11
BODY_FONT = 9


class WorldReportDialog(QDialog):
    def __init__(self, pmi, parent=None):
        super(WorldReportDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('World Report')

        self.worldReport = WorldReport(pmi)
        
        editor = QTextEdit()
        editor.setDocument(self.worldReport.document)

        #saveButton = QPushButton('Save')
        self.pdfButton = QPushButton('Save As PDF')
        self.closeButton = QPushButton('Close')

        buttonLayout = QVBoxLayout()
        #buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(self.pdfButton)
        buttonLayout.addWidget(self.closeButton)
##        buttonLayout.addWidget(self.view)
        buttonLayout.addStretch()

        layout = QHBoxLayout()
        layout.addWidget(editor)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        #self.connect(pdfButton, SIGNAL("clicked()"),
        #             self.exportToPdf)
        self.pdfButton.clicked.connect(self.exportToPdf)
        #self.connect(closeButton, SIGNAL("clicked()"),
        #             self.closeButtonClicked)
        self.closeButton.clicked.connect(self.closeButtonClicked)
        
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        


    def exportToPdf(self):
        #filename = 'World report.pdf'
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A4)
        printer.setOutputFormat(QPrinter.PdfFormat)
        default_path = os.path.join(self.worldReport.model.project_path,
                                    self.worldReport.model.slugify(self.worldReport.world.name))
        filename, selected_filter = QFileDialog.getSaveFileName(self, 'Save as PDF',
                                                                default_path,
                                                                'PDF Files (*.pdf)')
        printer.setOutputFileName(filename)
        
        self.worldReport.document.print_(printer)


    def closeButtonClicked(self):
        self.close()



class BoundaryRectangle(QGraphicsPolygonItem):
    def __init__(self, rectF=QRectF(), parent=None):
        QGraphicsPolygonItem.__init__(self, parent)
        self.rectF = rectF
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.transparent)
        self.setPen(pen)
        self.setBrush(Qt.transparent)
        myPolygon = QPolygonF(rectF)
        self.setPolygon(myPolygon)
        self.myPolygon = myPolygon
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def boundingRect(self):
        return self.rectF

                  
class MicroGridRoot(QGraphicsItem):
    def __init__(self, pmi, parent=None):
        QGraphicsItem.__init__(self, parent)

        self.hex_root = MapGrid.HexRoot(self,
                                        hexes_wide=1,
                                        hexes_high=1,
                                        hex_color=Qt.black)
        self.hex_root.setCellsSelectable(False)
        self.hex_root.setParentItem(self)
        self.model = pmi.model()

        model_row = pmi.row()
        world = pmi.model().getWorld(pmi)
        glyph = MapGlyphs.PlanetGlyph(pmi)
        glyph.configurePlanetGlyph(True)
        glyph.setParentItem(self)
        px, py = 0, 0
        MapGrid.gridToPix((world.col), (world.row))
        glyph.setPos(px, py)
        glyph.setFlag(QGraphicsItem.ItemIsSelectable, False)

        self.world_glyph = glyph


    def addBorder(self, rectF):
        self.boundary = BoundaryRectangle(rectF, self)

    def setCoordsVisible(self, flag):
        self.hex_root.setCoordsVisible(flag)

    def paint(self, painter=None, option=None, widget=None):
        pass

    def boundingRect(self):
        return QRectF()




class WorldReport(object):
    def __init__(self, pmi):

        self.pmi = pmi
        self.model = pmi.model()
        self.from_world_link_model = FromWorldLinkModel.FromWorldLinkModel(self.pmi)
        self.world = self.model.getWorld(pmi)

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.white)
        self.scene.model = self.model

        self.grid = MicroGridRoot(pmi)
        self.scene.addItem(self.grid)
        self.grid.setCoordsVisible(True)

        self.mapRect = self.scene.sceneRect()
        self.mapRect.adjust(-30, -0, -13, 0)
        #rect = self.mapRect.toRect()
        self.grid.addBorder(self.mapRect)

        image = QImage(262, 200, QImage.Format_ARGB32_Premultiplied)
        image.fill(0)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        self.scene.render(painter)
        painter.end()
        self.image_file = self.model.storeWorldImage(self.world.name, image)

##        self.view = QGraphicsView(self.scene)
##        self.view.setRenderHints(QPainter.Antialiasing)
##        self.view.setViewportUpdateMode(self.view.FullViewportUpdate)

        self.document = self.createDocument()


    def getDocFormats(self):
        class Formats(object):
            pass

        fmt = Formats()

        fmt.title_text = QTextCharFormat()
        fmt.title_text.setFont(QFont('Helvetica',
                                     TITLE_FONT,
                                     QFont.Bold))
        fmt.title_block = QTextBlockFormat()
        fmt.title_block.setTopMargin(TITLE_FONT)

        fmt.region_text = QTextCharFormat()
        fmt.region_text.setFont(QFont('Helvetica',
                                      HEADING_FONT,
                                      QFont.Bold))
        
        fmt.upp_text = QTextCharFormat()
        font = QFont('Courier New', UPP_FONT, QFont.Bold)
        fmt.upp_text.setFont(font)
        
        fmt.upp_block = QTextBlockFormat()
        fmt.upp_block.setTopMargin(0)
        fmt.upp_block.setBottomMargin(0)

        fmt.heading_text = QTextCharFormat()
        fmt.heading_text.setFont(QFont('Helvetica',
                                       HEADING_FONT,
                                       QFont.Bold))
        
        fmt.heading_block = QTextBlockFormat()
        fmt.heading_block.setTopMargin(HEADING_FONT)
        fmt.heading_block.setBottomMargin(HEADING_FONT)
        fmt.heading_block.setIndent(0)

        fmt.body_text = QTextCharFormat()
        fmt.body_text.setFont(QFont('Helvetica',
                                      BODY_FONT,
                                      QFont.Normal))
        fmt.body_text_bold = QTextCharFormat()
        fmt.body_text_bold.setFont(QFont('Helvetica',
                                      BODY_FONT,
                                      QFont.Bold))

        fmt.body_block = QTextBlockFormat()
        fmt.body_block.setAlignment(Qt.AlignTop)
        fmt.body_block.setBottomMargin(0)
        fmt.body_block.setIndent(0)

        fmt.body_block_padded = QTextBlockFormat()
        fmt.body_block_padded.setAlignment(Qt.AlignTop)
        fmt.body_block_padded.setBottomMargin(BODY_FONT)
        fmt.body_block_padded.setIndent(0)

        fmt.body_block_centre = QTextBlockFormat()
        fmt.body_block_centre.setAlignment(Qt.AlignHCenter)
        fmt.body_block_centre.setBottomMargin(0)
        fmt.body_block_centre.setIndent(0)

        table_constraints = [QTextLength(QTextLength.PercentageLength, 25),
                             QTextLength(QTextLength.PercentageLength, 5),
                             QTextLength(QTextLength.PercentageLength, 15)]
        fmt.attrib_table = QTextTableFormat()
        fmt.attrib_table.setCellSpacing(0)
        fmt.attrib_table.setCellPadding(3)
        fmt.attrib_table.setBorderBrush(QBrush(Qt.transparent))
        fmt.attrib_table.setColumnWidthConstraints(table_constraints)

        table_constraints = [QTextLength(QTextLength.PercentageLength, 25),
                             QTextLength(QTextLength.PercentageLength, 25)]
        fmt.links_table = QTextTableFormat()
        fmt.links_table.setCellSpacing(0)
        fmt.links_table.setCellPadding(3)
        fmt.links_table.setBorderBrush(QBrush(Qt.transparent))
        fmt.links_table.setColumnWidthConstraints(table_constraints)

        return fmt
        


    def createDocument(self):
        
        worldReport = QTextDocument()
        cursor = QTextCursor(worldReport)
        fmt = self.getDocFormats()

        def block(curs, bform, text, tform):
            curs.insertBlock()
            curs.setBlockFormat(bform)
            curs.insertText(text, tform)

        block(cursor, fmt.title_block, self.world.name, fmt.title_text)

        block(cursor, fmt.heading_block, 'Map Symbol', fmt.heading_text)

        image_format = QTextImageFormat()
        image_format.setHeight(100)
        image_format.setWidth(131)
        image_format.setName(self.image_file)

        cursor.insertBlock()
        cursor.insertImage(image_format)

        block(cursor, fmt.heading_block, 'System Information', fmt.heading_text)

        block(cursor, fmt.body_block, "Allegiance:\t" + str(self.world.allegiance), fmt.body_text)
        block(cursor, fmt.body_block, "Grid Column:\t" + str(self.world.col), fmt.body_text)
        block(cursor, fmt.body_block, "Grid Row:\t" + str(self.world.row), fmt.body_text)

        block(cursor, fmt.heading_block, 'World Attributes', fmt.heading_text)

        attribute_definitions = self.pmi.model().attributeDefinitions
        table = cursor.insertTable(len(attribute_definitions) + 1, 3, fmt.attrib_table)

        cell = table.cellAt(0, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Attribute Name', fmt.body_text_bold)

        cell = table.cellAt(0, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.setBlockFormat(fmt.body_block_centre)
        cellCursor.insertText('Code', fmt.body_text_bold)
        
        cell = table.cellAt(0, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Label', fmt.body_text_bold)

        for (count, attribute) in enumerate(attribute_definitions):
            base_column = count + Models.ATTRIBUTE_BASE
            cell = table.cellAt((count + 1), 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(attribute.name, fmt.body_text)

            code = self.world.attributes[count]
            cell = table.cellAt((count + 1), 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.setBlockFormat(fmt.body_block_centre)
            cellCursor.insertText(code, fmt.body_text)
            
            cell = table.cellAt((count + 1), 2)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(attribute.label(code), fmt.body_text)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        block(cursor, fmt.heading_block, 'Transport Links', fmt.heading_text)
        link_count = self.from_world_link_model.rowCount()
        table = cursor.insertTable(link_count + 1, 2, fmt.links_table)

        cell = table.cellAt(0, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Linked World', fmt.body_text_bold)

        cell = table.cellAt(0, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Link Type', fmt.body_text_bold)

        for row in range(link_count):
            world_index = self.from_world_link_model.createIndex(row,
                              FromWorldLinkModel.LINKED_WORLD_NAME)
            world_name = world_index.data()
            link_index = self.from_world_link_model.createIndex(row,
                            FromWorldLinkModel.LINK_TYPE_NAME)
            link_name = link_index.data()

            cell = table.cellAt((row + 1), 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(world_name, fmt.body_text)

            cell = table.cellAt((row + 1), 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(link_name, fmt.body_text)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        block(cursor, fmt.heading_block, 'Description', fmt.heading_text)
        for (offset, attribute) in enumerate(attribute_definitions):
            index = self.model.createIndex(self.pmi.row(),
                                           Models.ATTRIBUTE_BASE + offset)
            block(cursor,
                  fmt.body_block,
                  attribute.name,
                  fmt.body_text_bold)
            block(cursor,
                  fmt.body_block_padded,
                  index.data(Models.DESCRIPTION_ROLE),
                  fmt.body_text)

        return worldReport


    def oldCreateDocument(self):
        #Table of Details
        cursor.insertBlock()
        cursor.setBlockFormat(fmt.heading_block)
        cursor.insertText('System Information', fmt.heading_text)

        info = self.getSystemInfo()
        table = cursor.insertTable(len(info), 4, fmt.form_table)
        for row in info:
            cell = table.cellAt(info.index(row), 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[0], fmt.body)

            cell = table.cellAt(info.index(row), 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[1], fmt.body_text)

            cell = table.cellAt(info.index(row), 2)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[2], fmt.body_text)

            cell = table.cellAt(info.index(row), 3)
            cellCursor = cell.firstCursorPosition()
            if row[3] != '':
                cellCursor.insertText(row[3], fmt.body_text)
        table.mergeCells(1, 3, 2, 1)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)


        cursor.insertBlock()
        cursor.setBlockFormat(fmt.heading_block)
        cursor.insertText('Starport Facilities', fmt.heading_text)

        info = self.getStarportInfo()
        table = cursor.insertTable(len(info), 4, fmt.form_table)
        for row in info:
            cell = table.cellAt(info.index(row), 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[0], fmt.body_text)

            cell = table.cellAt(info.index(row), 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[1], fmt.body_text)

            cell = table.cellAt(info.index(row), 2)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[2], fmt.body_text)

            cell = table.cellAt(info.index(row), 3)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[3], fmt.body_text)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        debug_log('Finished starport info table')


        cursor.insertBlock()
        cursor.setBlockFormat(fmt.heading_block)
        cursor.insertText('Mainworld Attributes', fmt.heading_text)

        info = self.getMainworldInfo()
        table = cursor.insertTable(len(info), 4, fmt.form_table)
        for row in info:
            cell = table.cellAt(info.index(row), 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[0], fmt.body_text)

            cell = table.cellAt(info.index(row), 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[1], fmt.body_text)

            cell = table.cellAt(info.index(row), 2)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[2], fmt.body_text)

            cell = table.cellAt(info.index(row), 3)
            cellCursor = cell.firstCursorPosition()
            if row[3] != '':
                cellCursor.insertText(row[3], fmt.body_text)
        table.mergeCells(4, 3, 5, 1)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)


        cursor.insertBlock()
        cursor.setBlockFormat(fmt.heading_block)
        cursor.insertText('Mainworld Description', fmt.heading_text)

        info = self.getMainworldDescription()
        table = cursor.insertTable(len(info), 2, fmt.details_table)
        for row in info:
            cell = table.cellAt(info.index(row), 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[0], fmt.body_text)

            cell = table.cellAt(info.index(row), 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[1], fmt.body_text)
        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        return worldReport
