# Copyright 2013 Simon Dominic Hibbs
from PySide.QtCore import *
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PySide.QtGui import *
import os
from model import Models
from model import Foundation
from starmap import MapGlyphs
from starmap import MapGrid
from log import *

TITLE_FONT = 14
BODY_FONT = 10


class StatisticsDialog(QDialog):
    def __init__(self, pmi_list, numcells, name, parent=None):
        super(StatisticsDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Statistics Report')

        #print "About to generate report."
        self.report = StatisticsReport(pmi_list, numcells, name)

        #print "Adding document to report GUI"
        editor = QTextEdit()
        editor.setDocument(self.report.document)

        #print "Adding GUI buttons"
        self.pdfButton = QPushButton('Save As PDF')
        self.closeButton = QPushButton('Close')

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.pdfButton)
        buttonLayout.addWidget(self.closeButton)
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
        #print "Finished dialog setup"


    def exportToPdf(self):
        #filename = 'World report.pdf'
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A4)
        printer.setOutputFormat(QPrinter.PdfFormat)
        default_path = os.path.join(self.report.model.project_path,
                                    'StatisticsReport')
        filename, discard = QFileDialog.getSaveFileName(self, 'Save as PDF',
                                               default_path,
                                               'PDF Files (*.pdf)')
        print 'print ', str(filename)
        printer.setOutputFileName(str(filename))
        self.report.document.print_(printer)


    def closeButtonClicked(self):
        self.close()


class StatisticsReport(object):
    def __init__(self, pmi_list, numcells, title):
        if len(pmi_list) == 0:
            #print "Generating report"
            self.document = QTextDocument()
            cursor = QTextCursor(self.document)
            body_text_format = QTextCharFormat()
            body_text_format.setFont(QFont('Helvetica',
                                          BODY_FONT,
                                          QFont.Normal))
            body_block_format = QTextBlockFormat()
            body_block_format.setAlignment(Qt.AlignTop)
            body_block_format.setBottomMargin(0)
            body_block_format.setIndent(1)

            cursor.insertBlock()
            cursor.setBlockFormat(body_block_format)
            cursor.insertText('No worlds in selected area', body_text_format)

        else:
            
            self.model = pmi_list[0].model()

            world_list = []

            attribute_table = []
            for attribute in self.model.attributeDefinitions:
                attribute_table.append([0] * len(attribute.codes))
            
            for pmi in pmi_list:
                world = self.model.getWorld(pmi)
                world_list.append(world)
                col_max = 0
                for n, attribute in enumerate(world.attributes):
                    attribute_table[n][self.model.attributeDefinitions[n].index(world.attributes[n])] += 1
                    if len(self.model.attributeDefinitions[n].codes) > col_max:
                        col_max = len(self.model.attributeDefinitions[n].codes)

            total_pop = 0  # Placeholder
            world_number = len(world_list)

            #print "Created summary data table, about to create document."
            self.document = QTextDocument()
            cursor = QTextCursor(self.document)

            title_text_format = QTextCharFormat()
            title_text_format.setFont(QFont('Helvetica',
                                            TITLE_FONT,
                                            QFont.Bold))
            title_block_format = QTextBlockFormat()
            title_block_format.setTopMargin(TITLE_FONT)

            bold_text_format = QTextCharFormat()
            bold_text_format.setFont(QFont('Helvetica',
                                          BODY_FONT,
                                          QFont.Bold))
            body_text_format = QTextCharFormat()
            body_text_format.setFont(QFont('Helvetica',
                                          BODY_FONT,
                                          QFont.Normal))
            body_block_format = QTextBlockFormat()
            body_block_format.setAlignment(Qt.AlignTop)
            body_block_format.setBottomMargin(0)
            body_block_format.setIndent(1)

    ##        table_constraints = [QTextLength(QTextLength.PercentageLength, 25),
    ##                             QTextLength(QTextLength.PercentageLength, 30),
    ##                             QTextLength(QTextLength.PercentageLength, 25),
    ##                             QTextLength(QTextLength.PercentageLength, 20)]
            form_table_format = QTextTableFormat()
            form_table_format.setCellSpacing(0)
            form_table_format.setCellPadding(3)
            form_table_format.setBorderBrush(QBrush(Qt.transparent))

            attrib_table_format = QTextTableFormat()
            attrib_table_format.setCellSpacing(0)
            attrib_table_format.setCellPadding(3)
            attrib_table_format.setBorderBrush(QBrush(Qt.transparent))
    ##        form_table_format.setColumnWidthConstraints(table_constraints)

            details_table_format = QTextTableFormat()
            details_table_format.setCellSpacing(0)
            details_table_format.setCellPadding(7)
            details_table_format.setBorderBrush(QBrush(Qt.transparent))

            #print "Creating report content"
            cursor.insertBlock()
            cursor.setBlockFormat(title_block_format)
            cursor.insertText(title, title_text_format)

            summary_table = cursor.insertTable(4, 2, form_table_format)
            cell = summary_table.cellAt(0, 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText('Number of Hexes: ', body_text_format)
            cell = summary_table.cellAt(0, 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(str(numcells), body_text_format)

            cell = summary_table.cellAt(1, 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText('Number of Worlds: ', body_text_format)
            cell = summary_table.cellAt(1, 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(str(world_number), body_text_format)

            cell = summary_table.cellAt(2, 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText('World Occurrence: ', body_text_format)
            cell = summary_table.cellAt(2, 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(str(int((world_number * 100) / numcells)) + '%', body_text_format)

            def splitThousands(s, sep=','):
                        if len(s) <= 3: return s
                        return splitThousands(s[:-3], sep) + sep + s[-3:]

            cell = summary_table.cellAt(3, 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText('Total Inhabitants: ', body_text_format)
            cell = summary_table.cellAt(3, 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(splitThousands(str(total_pop)), body_text_format)

            cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)


            cursor.insertBlock()
            cursor.setBlockFormat(title_block_format)
            cursor.insertText('World Attributes', title_text_format)

            # define main attribute values table configuration data
            table_constraints = [QTextLength(QTextLength.PercentageLength, 15)]
            colwidth = int(85 / col_max)
            for col in range(col_max):
                table_constraints.append(QTextLength(QTextLength.PercentageLength, colwidth))
            attrib_table_format.setColumnWidthConstraints(table_constraints)

            #print "Construct main attribute values table"
            main_table = cursor.insertTable(len(attribute_table) * 3, col_max + 1, attrib_table_format)

            #print"Populate header row"
            #print "col_max= ", col_max

            for atr_index, atr in enumerate(self.model.attributeDefinitions):
                name_row = atr_index * 3
                cell = main_table.cellAt(name_row, 0)
                cellCursor = cell.firstCursorPosition()
                cellCursor.insertText(atr.name, bold_text_format)
                
                cell = main_table.cellAt(name_row + 1, 0)
                cellCursor = cell.firstCursorPosition()
                cellCursor.insertText("Codes:", body_text_format)

                cell = main_table.cellAt(name_row + 2, 0)
                cellCursor = cell.firstCursorPosition()
                cellCursor.insertText("Total:", body_text_format)

                for code_index, code in enumerate(atr.codes):
                    cell = main_table.cellAt(name_row + 1, code_index + 1)
                    cellCursor = cell.firstCursorPosition()
                    cellCursor.insertText(code, body_text_format)

                    if attribute_table[atr_index][code_index] == 0:
                        total = ''
                    else:
                        total = str(attribute_table[atr_index][code_index])

                    cell = main_table.cellAt(name_row + 2, code_index + 1)
                    cellCursor = cell.firstCursorPosition()
                    cellCursor.insertText(total, body_text_format)

            cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
