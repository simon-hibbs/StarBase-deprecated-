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

TITLE_FONT = 16
HEADING_FONT = 12
UPP_FONT = 10
BODY_FONT = 9

class SubsectorReportDialog(QDialog):
    def __init__(self, subsector_glyph, pmi_list, model, parent=None):
        super(SubsectorReportDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Subsector Report')

        self.model = model
        self.glyph = subsector_glyph
        self.report = SubsectorReport(subsector_glyph, pmi_list, model)
        
        editor = QTextEdit()
        editor.setDocument(self.report.document)
        
        saveButton = QPushButton('Save')
        self.pdfButton = QPushButton('Save As PDF')
        self.closeButton = QPushButton('Close')

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(saveButton)
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
        default_path = os.path.join(self.model.project_path,
                                    self.model.slugify(self.glyph.name)) + \
                                    '.pdf'
        filename = QFileDialog.getSaveFileName(self, 'Save as PDF',
                                               default_path,
                                               'PDF Files (*.pdf)')
        printer.setOutputFileName(filename)
        
        self.report.document.print_(printer)


    def closeButtonClicked(self):
        self.close()



class SubsectorReport(object):
    def __init__(self, subsector_glyph, pmi_list, model):

        self.glyph = subsector_glyph
        self.subectorName = subsector_glyph.name
        self.pmi_list = pmi_list
        self.model = model

        self.document = QTextDocument()
        cursor = QTextCursor(self.document)

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
        heading_block_format.setBottomMargin(HEADING_FONT)

        upp_text_format = QTextCharFormat()
        font = QFont('Courier New', UPP_FONT, QFont.Normal)
        font.setStyleHint(QFont.TypeWriter)
        upp_text_format.setFont(font)
        upp_block_format = QTextBlockFormat()
        upp_block_format.setTopMargin(0)
        upp_block_format.setBottomMargin(0)

        body_text_format = QTextCharFormat()
        body_text_format.setFont(QFont('Helvetica',
                                      BODY_FONT,
                                      QFont.Normal))
        body_block_format = QTextBlockFormat()
        body_block_format.setAlignment(Qt.AlignTop)
        body_block_format.setBottomMargin(0)
        body_block_format.setIndent(1)

        # Add Title
        cursor.insertBlock()
        cursor.setBlockFormat(title_block_format)
        cursor.insertText(self.subectorName + ' Subsector', title_text_format)

        cursor.insertBlock()
        cursor.setBlockFormat(body_block_format)
        cursor.insertText('Subsector description text', body_text_format)
        cursor.insertBlock()
        cursor.setBlockFormat(body_block_format)

        cursor.insertBlock()
        cursor.setBlockFormat(heading_block_format)
        cursor.insertText('World UWPs', heading_text_format)
##        cursor.insertBlock()
##        cursor.setBlockFormat(upp_block_format)

        cursor.insertBlock()
        cursor.setBlockFormat(upp_block_format)
        headers = self.model.getUWP(None)
        cursor.insertText(headers, upp_text_format)
        
        for pmi in self.pmi_list:
            upp_text =  self.model.getUWP(pmi.row())
            cursor.insertBlock()
            cursor.setBlockFormat(upp_block_format)
            cursor.insertText(upp_text, upp_text_format)

        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        
        

        
