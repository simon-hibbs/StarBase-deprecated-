from PySide.QtCore import *
# Copyright 2013 Simon Dominic Hibbs
from PySide.QtGui import *
from model import NetworkModel as NWM
from model import FromWorldLinkModel as FWLM
import log


LINK_LINE = 2

class NetworkLineStyleDelegate(QStyledItemDelegate):
    """
    Draws the colored/styled network line in a QTableView cell
    """
    def __init__(self, parent=None):
        super(NetworkLineStyleDelegate, self).__init__(parent)
        log.debug_log("Set up line style delegate")

    def paint(self, painter, option, index):
        data = index.model().data(index)
        line_color = index.data(FWLM.ColorRole)

        painter.save()

        rect = option.rect
        rect.adjust(+5, 0, -5, 0)

        pen = QPen()
        pen.setColor(line_color)
        pen.setWidth(3)
        pen.setStyle(data)
        painter.setPen(pen)

        middle = (rect.bottom() + rect.top()) / 2

        painter.drawLine(rect.left(), middle, rect.right(), middle)
        painter.restore()


class FromWorldLinkTableView(QTableView):

    def __init__(self, link_model, parent=None):
        super(FromWorldLinkTableView, self).__init__(parent)
        self.setModel(link_model)

        vheader = self.verticalHeader()
        vheader.setVisible(False)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        self.horizontalHeader().geometriesChanged \
             .connect(self.updateGeometryAsync)
        self.horizontalHeader().sectionResized \
             .connect(self.updateGeometryAsync)        
        # ... when a row header label changes and makes the
        # width of the vertical header change too
        self.model().headerDataChanged.connect(self.updateGeometryAsync)

    def updateGeometryAsync(self):      
        QTimer.singleShot(0, self.updateGeometry)


    def sizeHint(self):
        height = QTableWidget.sizeHint(self).height()

        # length() includes the width of all its sections
        width = self.horizontalHeader().length() 

        # you add the actual size of the vertical header and scrollbar
        # (not the sizeHint which would only be the preferred size)                  
        width += self.verticalHeader().width()        
        width += self.verticalScrollBar().width()       

        # and the margins which include the frameWidth and the extra 
        # margins that would be set via a stylesheet or something else
        margins = self.contentsMargins()
        width += margins.left() + margins.right()

        return QSize(width, height)

