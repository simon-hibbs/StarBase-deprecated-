from PyQt4.QtCore import *
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

        self.report = StatisticsReport(pmi_list, numcells, name)

        editor = QTextEdit()
        editor.setDocument(self.report.document)

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
        self.closeButton.cliecked.connect(self.closeButtonClicked)
        
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)


    def exportToPdf(self):
        #filename = 'World report.pdf'
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPaperSize(QPrinter.A4)
        printer.setOutputFormat(QPrinter.PdfFormat)
        default_path = os.path.join(self.report.model.project_path,
                                    'StatisticsReport')
        filename = QFileDialog.getSaveFileName(self, 'Save as PDF',
                                               default_path,
                                               'PDF Files (*.pdf)')
        printer.setOutputFileName(filename)
        self.report.document.print_(printer)


    def closeButtonClicked(self):
        self.close()


class StatisticsReport(object):
    def __init__(self, pmi_list, numcells, name):
        self.model = pmi_list[0].model()

        world_list = []
        starport_min = 5; starport_avg = 0; starport_max = 0; starport_tot = 0
        size_min = 10; size_avg = 0; size_max = 0; size_tot = 0
        atmo_min = 10; atmo_avg = 0; atmo_max = 0; atmo_tot = 0
        hydro_min = 10; hydro_avg = 0; hydro_max = 0; hydro_tot = 0
        pop_min = 10; pop_avg = 0; pop_max = 0; pop_tot = 0
        gov_min = 10; gov_avg = 0; gov_max = 0; gov_tot = 0
        law_min = 10; law_avg = 0; law_max = 0; law_tot = 0
        tech_min = 15; tech_avg = 0; tech_max = 0; tech_tot = 0
        total_pop = 0

        Ag = 0; As = 0; Ba = 0; De = 0; Fl = 0; Ga = 0; Hi = 0; Ht = 0; IC = 0
        In = 0; Lo = 0; Lt = 0; Na = 0; NI = 0; Po = 0; Ri = 0; Va = 0; Wa = 0
        
        for pmi in pmi_list:
            w = self.model.getWorld(pmi)
            world_list.append(w)
            starport_tot += w.starport.index
            if w.starport.index < starport_min: starport_min = w.starport.index
            if w.starport.index > starport_max: starport_max = w.starport.index
            size_tot += w.size.index
            if w.size.index < size_min: size_min = w.size.index
            if w.size.index > size_max: size_max = w.size.index
            atmo_tot += w.atmosphere.index
            if w.atmosphere.index < atmo_min: atmo_min = w.atmosphere.index
            if w.atmosphere.index > atmo_max: atmo_max = w.atmosphere.index
            hydro_tot += w.hydrographics.index
            if w.hydrographics.index < hydro_min: hydro_min = w.hydrographics.index
            if w.hydrographics.index > hydro_max: hydro_max = w.hydrographics.index
            pop_tot += w.population.index
            total_pop += w.population.inhabitants
            if w.population.index < pop_min: pop_min = w.population.index
            if w.population.index > pop_max: pop_max = w.population.index
            gov_tot += w.government.index
            if w.government.index < gov_min: gov_min = w.government.index
            if w.government.index > gov_max: gov_max = w.government.index
            law_tot += w.lawLevel.index
            if w.lawLevel.index < law_min: law_min = w.lawLevel.index
            if w.lawLevel.index > law_max: law_max = w.lawLevel.index
            tech_tot += w.techLevel.index
            if w.techLevel.index < tech_min: tech_min = w.techLevel.index
            if w.techLevel.index > tech_max: tech_max = w.techLevel.index

            if w.tradeAg: Ag += 1
            if w.tradeAs: As += 1
            if w.tradeBa: Ba += 1
            if w.tradeDe: De += 1
            if w.tradeFl: Fl += 1
            if w.tradeGa: Ga += 1
            if w.tradeHi: Hi += 1
            if w.tradeHt: Ht += 1
            if w.tradeIC: IC += 1
            if w.tradeIn: In += 1
            if w.tradeLo: Lo += 1
            if w.tradeLt: Lt += 1
            if w.tradeNa: Na += 1
            if w.tradeNI: NI += 1
            if w.tradePo: Po += 1
            if w.tradeRi: Ri += 1
            if w.tradeVa: Va += 1
            if w.tradeWa: Wa += 1
            
        world_number = len(world_list)
        starport_avg = int(round(float(starport_tot) / world_number))
        size_avg = int(round(float(size_tot) / world_number))
        atmo_avg = int(round(float(atmo_tot) / world_number))
        hydro_avg = int(round(float(hydro_tot) / world_number))
        pop_avg = int(round(float(pop_tot) / world_number))
        gov_avg = int(round(float(gov_tot) / world_number))
        law_avg = int(round(float(law_tot) / world_number))
        tech_avg = int(round(float(tech_tot) / world_number))
        
        self.document = QTextDocument()
        cursor = QTextCursor(self.document)

        title_text_format = QTextCharFormat()
        title_text_format.setFont(QFont('Helvetica',
                                        TITLE_FONT,
                                        QFont.Bold))
        title_block_format = QTextBlockFormat()
        title_block_format.setTopMargin(TITLE_FONT)

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
##        form_table_format.setColumnWidthConstraints(table_constraints)

        details_table_format = QTextTableFormat()
        details_table_format.setCellSpacing(0)
        details_table_format.setCellPadding(7)
        details_table_format.setBorderBrush(QBrush(Qt.transparent))

        cursor.insertBlock()
        cursor.setBlockFormat(title_block_format)
        cursor.insertText('Summary', title_text_format)

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

        main_table = cursor.insertTable(9, 4, form_table_format)
        cell = main_table.cellAt(0, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Attribute', body_text_format)
        cell = main_table.cellAt(0, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Minumum', body_text_format)
        cell = main_table.cellAt(0, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Average', body_text_format)
        cell = main_table.cellAt(0, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Maximum', body_text_format)

        cell = main_table.cellAt(1, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Starport Type', body_text_format)
        cell = main_table.cellAt(1, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.starport_types[starport_max], body_text_format)
        cell = main_table.cellAt(1, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.starport_types[starport_avg], body_text_format)
        cell = main_table.cellAt(1, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.starport_types[starport_min], body_text_format)

        cell = main_table.cellAt(2, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Size', body_text_format)
        cell = main_table.cellAt(2, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.size_types[size_min], body_text_format)
        cell = main_table.cellAt(2, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.size_types[size_avg], body_text_format)
        cell = main_table.cellAt(2, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.size_types[size_max], body_text_format)

        cell = main_table.cellAt(3, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Atmosphere', body_text_format)
        cell = main_table.cellAt(3, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.atmosphere_types[atmo_min], body_text_format)
        cell = main_table.cellAt(3, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.atmosphere_types[atmo_avg], body_text_format)
        cell = main_table.cellAt(3, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.atmosphere_types[atmo_max], body_text_format)

        cell = main_table.cellAt(4, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Hydrographics', body_text_format)
        cell = main_table.cellAt(4, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.hydrographics_types[hydro_min], body_text_format)
        cell = main_table.cellAt(4, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.hydrographics_types[hydro_avg], body_text_format)
        cell = main_table.cellAt(4, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.hydrographics_types[hydro_max], body_text_format)

        cell = main_table.cellAt(5, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Population', body_text_format)
        cell = main_table.cellAt(5, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.population_types[pop_min], body_text_format)
        cell = main_table.cellAt(5, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.population_types[pop_avg], body_text_format)
        cell = main_table.cellAt(5, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.population_types[pop_max], body_text_format)

        cell = main_table.cellAt(6, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Government', body_text_format)
        cell = main_table.cellAt(6, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.government_types[gov_min], body_text_format)
        cell = main_table.cellAt(6, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.government_types[gov_avg], body_text_format)
        cell = main_table.cellAt(6, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.government_types[gov_max], body_text_format)

        cell = main_table.cellAt(7, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Law Level', body_text_format)
        cell = main_table.cellAt(7, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.law_level_types[law_min], body_text_format)
        cell = main_table.cellAt(7, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.law_level_types[law_avg], body_text_format)
        cell = main_table.cellAt(7, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.law_level_types[law_max], body_text_format)

        cell = main_table.cellAt(8, 0)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText('Tech Level', body_text_format)
        cell = main_table.cellAt(8, 1)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.tech_level_types[tech_min], body_text_format)
        cell = main_table.cellAt(8, 2)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.tech_level_types[tech_avg], body_text_format)
        cell = main_table.cellAt(8, 3)
        cellCursor = cell.firstCursorPosition()
        cellCursor.insertText(Foundation.tech_level_types[tech_max], body_text_format)

        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)

        cursor.insertBlock()
        cursor.setBlockFormat(title_block_format)
        cursor.insertText('Trade Code Frequency', title_text_format)

        print 'About to generate trade code table'

        trade_table = cursor.insertTable(19, 2, form_table_format)
        count = 0
        for row in (('Trade Code', 'Worlds'),
                    ('Agricultural', str(Ag)),
                    ('Asteroid', str(As)),
                    ('Barren', str(Ba)),
                    ('Desert', str(De)),
                    ('Fluid Oceans', str(Fl)),
                    ('Garden', str(Ga)),
                    ('High Population', str(Hi)),
                    ('High Technology', str(Ht)),
                    ('Ice-Capped', str(IC)),
                    ('Industrial', str(In)),
                    ('Low Population', str(Lo)),
                    ('Low Technology', str(Lt)),
                    ('Non-Agricultural', str(Na)),
                    ('Non-Industrial', str(NI)),
                    ('Poor', str(Po)),
                    ('Rich', str(Ri)),
                    ('Vacuum', str(Va)),
                    ('Water World', str(Wa))):
            cell = trade_table.cellAt(count, 0)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[0], body_text_format)
            cell = trade_table.cellAt(count, 1)
            cellCursor = cell.firstCursorPosition()
            cellCursor.insertText(row[1], body_text_format)
            count += 1

        cursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor)
        
        

        

        
