import sys
# Copyright 2013 Simon Dominic Hibbs
#import math
from PySide.QtCore import *
from PySide.QtGui import *
from model import Models
from model import InterWorldLinkModel as IWLM

import log


class CheckBoxDelegate(QStyledItemDelegate):
    # Copied from NetworkManager.py
    
    def __init__(self, parent=None):
        super(CheckBoxDelegate, self).__init__(parent)
        log.debug_log("Set up CheckBoxDelegate delegate")

    def createEditor(self, parent, option, index):
        # Prevents an editor being created if the user clicks in this cell.
        return None

    def paint(self, painter, option, index):
        #Paint a checkbox without the label.

        checked = bool(index.model().data(index, Qt.DisplayRole))
        check_box_style_option = QStyleOptionButton()

        if (index.flags() & Qt.ItemIsEditable) > 0:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)
##        if not index.model().hasFlag(index, Qt.ItemIsEditable):
##            check_box_style_option.state |= QStyle.State_ReadOnly

        QApplication.style().drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        #Change the data in the model and the state of the checkbox
        #if the user presses the left mousebutton or presses
        #Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        
        if not (index.flags() & Qt.ItemIsEditable) > 0:
            return False

        # Do not change the checkbox-state
        if event.type() == QEvent.MouseButtonRelease or event.type() == QEvent.MouseButtonDblClick:
            if event.button() != Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QEvent.KeyPress:
            if event.key() != Qt.Key_Space and event.key() != Qt.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData (self, editor, model, index):
        #The user wanted to change the old state in the opposite.

        newValue = not bool(index.model().data(index, Qt.DisplayRole))
        model.setData(index, newValue, Qt.EditRole)

    def getCheckBoxRect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(
            QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QPoint (option.rect.x() +
                             option.rect.width() / 2 -
                             check_box_rect.width() / 2,
                             option.rect.y() +
                             option.rect.height() / 2 -
                             check_box_rect.height() / 2)
        return QRect(check_box_point, check_box_rect.size())


class NetworkLineStyleDelegate(QStyledItemDelegate):
    """
    Draws the colored/styled network line in a QTableView cell
    """
    def __init__(self, parent=None):
        super(NetworkLineStyleDelegate, self).__init__(parent)
        log.debug_log("Set up line style delegate")

##    def createEditor(self, parent, option, index):
##        editor = NetworkLineStyleComboBox(index, parent)
##        return editor
##
##    def setEditorData(self, editor, index):
##        line_style = index.data(Qt.EditRole)
##        editor.setCurrentIndex(line_style)
##
##    def setModelData(self, editor, model, index):
##        model.setData(index, editor.currentIndex(), Qt.EditRole)

    def paint(self, painter, option, index):
        data = index.model().data(index)
        #line_color = index.model().data(index.model().index(index.row(), NWM.NET_COLOR))
        line_color = index.model().getLineColor(index.row())
        #print line_color
        #data = WLM.intToStyle(WLM.LINE_STYLE_LIST[index.model().data(index)])
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


class InterWorldLinkTableView(QTableView):

    def __init__(self, link_model, parent=None):
        super(InterWorldLinkTableView, self).__init__(parent)
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


class InterWorldLinkEditor(QDialog):
    def __init__(self, world_model, pmi_list, cell_list, parent=None):
        super(InterWorldLinkEditor, self).__init__(parent)
        self.setWindowTitle("World Link Editor")
        self.world_model = world_model
        self.network_model = self.world_model.network_model

        world_list = [self.world_model.getWorld(pmi_list[0]),
                      self.world_model.getWorld(pmi_list[1])]

        # Sort the worlds so the left+top most is first
        if world_list[0].col > world_list[1].col:
            world_list[0], world_list[1] = \
                           world_list[1], world_list[0]
            pmi_list[0], pmi_list[1] = \
                         pmi_list[1], pmi_list[0]
        elif world_list[0].col == world_list[1].col and world_list[0].row > world_list[1].row:
            world_list[0], world_list[1] = \
                           world_list[1], world_list[0]
            pmi_list[0], pmi_list[1] = \
                         pmi_list[1], pmi_list[0]

        self.pmi_list = pmi_list
        self.world_list = world_list
        
        self.link_model = IWLM.InterWorldLinkModel(self.network_model,
                                                   world_list[0],
                                                   world_list[1])
        layout = QGridLayout()

        w1_label = QLabel('World 1:')
        w2_label = QLabel('World 2:')
        w1_name = QLabel(self.world_list[0].name)
        w2_name = QLabel(self.world_list[1].name)

        self.linkTable = InterWorldLinkTableView(self.link_model)
        self.linkTable.setItemDelegateForColumn(IWLM.LINK_CHECKED,
                                                CheckBoxDelegate(self))
        self.linkTable.setItemDelegateForColumn(IWLM.LINK_LINE,
                                                NetworkLineStyleDelegate(self))
        self.linkTable.setSelectionMode(QTableView.SingleSelection)
        self.linkTable.setSelectionBehavior(QTableView.SelectRows)
        self.linkTable.resizeColumnsToContents()

        layout.addWidget(w1_label, 0, 0)
        layout.addWidget(w1_name, 0, 1)
        layout.addWidget(w2_label, 1, 0)
        layout.addWidget(w2_name, 1, 1)

        layout.addWidget(self.linkTable, 2, 0, 1, 4)

        self.setLayout(layout)

        self.world_model.rowsAboutToBeRemoved.connect(self.checkWorldRemoved)

        #self.link_model.dataChanged.connect(self.checkStateChanged)
        #self.link_model.dataChanged.connect(self.networkTable.resizeColumnsToContents)
        

    def checkWorldRemoved(self, parent, start, end):
        for pmi in self.pmi_list:
            if pmi.row() in range(start, (end + 1)):
                debug_log('Closing Link Editor: world deleted')
                self.close()
