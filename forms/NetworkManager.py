# Copyright 2013 Simon Dominic Hibbs
from PySide.QtCore import *
from PySide.QtGui import *
from model import NetworkModel as NWM
import log

NAME = 0
COLOR = 1


class NetworkNameEdit(QLineEdit):
    def __init__(self, parent=None):
        super(NetworkNameEdit, self).__init__(parent)
        self.setMaxLength(30)
        self.setMinimumWidth(160)


# delegate required to draw items in combo box popup
class ComboLineStyleDelegate(QItemDelegate):

    def __init__(self, network_index, parent=None):
        super(ComboLineStyleDelegate, self).__init__(parent)
        log.debug_log("Set up combo style delegate")
        self.network_index = network_index

    def paint(self, painter, option, index):
        data = NWM.intToStyle(int(index.data()))
        line_color = self.network_index.model().createIndex(self.network_index.row(),
                                                            NWM.NET_COLOR).data()
        #line_color = self.network_model.data(index.row(), WLM.NET_COLOR)
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


# Combo box required to paint currently selected item
class NetworkLineStyleComboBox(QComboBox):
    
    def __init__(self, network_index, parent=None):
        super(NetworkLineStyleComboBox, self).__init__(parent)
        log.debug_log("Set up Line Style Combo Box")
        self.network_index = network_index
        # Note self.model is a list model of line styles, and is not the network model
        self.setModel(QStringListModel(NWM.LINE_STYLE_LIST_STRINGS, parent))
        self.setItemDelegate(ComboLineStyleDelegate(self.network_index, self))
        
    def paintEvent(self, e):
        #data = self.itemData(self.currentIndex())
        data = NWM.intToStyle(NWM.LINE_STYLE_LIST[self.currentIndex()])
        line_color = self.network_index.model().createIndex(self.network_index.row(),
                                                            NWM.NET_COLOR).data()
        #line_color = self.network_index.model().data(self.network_index.row(),
        #                                             WLM.NET_COLOR)
        p = QStylePainter(self)
        p.setPen(self.palette().color(QPalette.Text))

        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        p.drawComplexControl(QStyle.CC_ComboBox, opt)

        painter = QPainter(self)
        painter.save()

        rect = p.style().subElementRect(QStyle.SE_ComboBoxFocusRect, opt, self)
        rect.adjust(+5, 0, -5, 0)

        pen = QPen()
        pen.setColor(line_color)
        pen.setWidth(3)
        pen.setStyle(data)
        painter.setPen(pen)

        middle = (rect.bottom() + rect.top()) / 2

        painter.drawLine(rect.left(), middle, rect.right(), middle)
        painter.restore()
    

class NetworkColorDelegate(QStyledItemDelegate):
    """
    Delegate to draw a coloured box in a QTableView cell.
    """
    def __init__(self, parent=None):
        super(NetworkColorDelegate, self).__init__(parent)
        log.debug_log("Set up color delegate")

    def paint(self, painter, option, index):
        if index.column() == NWM.NET_COLOR:
            color_code = index.data()
            color_pixmap = QPixmap(64, 32)
            color_pixmap.fill(QColor(color_code))
            color_icon = QIcon(color_pixmap)

            painter.fillRect(option.rect, QColor(color_code))

        else:
            QStyledItemDelegate.paint(self, painter, option, index)

    def sizeHint(self, option, index):
        if index.column() == NWM.NET_COLOR:
            return QSize(64, 32)
        else:
            log.debug_log("NetworkColorDelegate: Size Hint Error")


    def createEditor(self, parent, option, index):
        if index.column() == NWM.NET_COLOR:
            return None
        else:
            return QStyledItemDelegate.createEditor(self, parent,
                                                       option, index)

## http://stackoverflow.com/questions/516032/how-to-make-qcombobox-painting-item-delegate-for-its-current-item-qt-4
class NetworkLineStyleDelegate(QStyledItemDelegate):
    """
    Draws the colored/styled network line in a QTableView cell
    """
    def __init__(self, parent=None):
        super(NetworkLineStyleDelegate, self).__init__(parent)
        log.debug_log("Set up line style delegate")

    def createEditor(self, parent, option, index):
        editor = NetworkLineStyleComboBox(index, parent)
        return editor

    def setEditorData(self, editor, index):
        line_style = index.data(Qt.EditRole)
        editor.setCurrentIndex(line_style)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentIndex(), Qt.EditRole)

    def paint(self, painter, option, index):
        data = index.model().data(index)
        line_color = index.model().data(index.model().index(index.row(), NWM.NET_COLOR))
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



class CheckBoxDelegate(QStyledItemDelegate):
    # Also copied to InterWorldLinkEditor.py
    
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


class NetworkTableView(QTableView):
    
    def __init__(self, network_model, parent=None):
        super(NetworkTableView, self).__init__(parent)
        self.doubleClicked.connect(self.checkShowColorDialog)
        self.setModel(network_model)
        vheader = self.verticalHeader()
        vheader.setVisible(False)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        # To force the width to use sizeHint().width()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # To readjust the size automatically...
        # ... when columns are added or resized
        self.horizontalHeader().geometriesChanged \
             .connect(self.updateGeometryAsync)
        self.horizontalHeader().sectionResized \
             .connect(self.updateGeometryAsync)        
        # ... when a row header label changes and makes the
        # width of the vertical header change too
        self.model().headerDataChanged.connect(self.updateGeometryAsync)


    def checkShowColorDialog(self, index):
        if index.column() == NWM.NET_COLOR:
            color = QColorDialog.getColor(QColor(index.data()), self)
            if color.isValid():
                index.model().setData(index, str(color.name()), Qt.EditRole)

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

    
class NetworkManager(QDialog):
    def __init__(self, network_model, scene, parent=None):
        super(NetworkManager, self).__init__(parent)
        log.debug_log('Started Network Manager init.')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("Network Manager")
        self.network_model = network_model
        self.scene = scene

        log.debug_log('Setting up Network Editor controlls')
        #self.networkTable = QTableView()
        self.networkTable = NetworkTableView(self.network_model)
        #self.networkTable.setModel(self.network_model)
        #self.networkTable.setItemDelegate(NetworkDelegate(self))
        self.networkTable.setItemDelegateForColumn(NWM.NET_CHECKED,
                                                   CheckBoxDelegate(self))
        self.networkTable.setItemDelegateForColumn(NWM.NET_COLOR,
                                                   NetworkColorDelegate(self))
        self.networkTable.setItemDelegateForColumn(NWM.NET_STYLE,
                                                   NetworkLineStyleDelegate(self))
        self.networkTable.setSelectionMode(QTableView.SingleSelection)
        self.networkTable.setSelectionBehavior(QTableView.SelectRows)
        self.networkTable.resizeColumnsToContents()

        self.addButton = QPushButton('Add')
        self.mergeButton = QPushButton('Merge')
        self.colorButton = QPushButton('Change Colour')
        self.deleteButton = QPushButton('Delete')
        self.okButton = QPushButton('OK')

        buttonLayout =  QVBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.mergeButton)
        buttonLayout.addWidget(self.colorButton)
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addStretch(10)
        buttonLayout.addWidget(self.okButton)

        hLayout = QHBoxLayout()
        hLayout.addWidget(self.networkTable, 1)
        hLayout.addLayout(buttonLayout)
        self.setLayout(hLayout)

        self.addButton.clicked.connect(self.addButtonClicked)
        self.deleteButton.clicked.connect(self.deleteButtonClicked)
        self.colorButton.clicked.connect(self.colorButtonClicked)
        self.okButton.clicked.connect(self.okButtonClicked)

        self.network_model.dataChanged.connect(self.checkStateChanged)
        self.network_model.dataChanged.connect(
            self.networkTable.resizeColumnsToContents)
        #self.resetCheckStates()
        self.checkStateChanged()


    def addButtonClicked(self):
        self.network_model.insertRows()

    def mergeButtonClicked(self):
        log_debug_log('NetworkManager:merge|Not yet implemented')
        pass

    def colorButtonClicked(self):
        for row in range(self.network_model.rowCount()):
            if self.network_model.data(
                self.network_model.index(row, NWM.NET_CHECKED)):
                index = self.network_model.index(row, NWM.NET_COLOR)
                color = QColorDialog.getColor(QColor(index.data()), self)
                index.model().setData(index, str(color.name()), Qt.EditRole)

    def deleteButtonClicked(self):
        delete_list = []
        for row in range(self.network_model.rowCount()):
            if self.network_model.data(
                self.network_model.index(row, NWM.NET_CHECKED)):
                delete_list.append(row)
        msgBox = QMessageBox(self)
        msgBox.setText("The following networks will be deleted:")
        informative_text = ""
        for row in delete_list:
            net_name = self.network_model.index(row, NWM.NET_NAME).data()
            informative_text += "        " + str(net_name) + "\n"
        msgBox.setInformativeText(informative_text)
        msgBox.setStandardButtons(QMessageBox.Ok |
                                  QMessageBox.Cancel)
        msgBox.setDefaultButton(QMessageBox.Cancel)
        ret = msgBox.exec_()
        if ret == QMessageBox.Ok:
            delete_list.sort(reverse=True)
            for row in delete_list:
                self.network_model.removeRows(row)

    def okButtonClicked(self):
        #self.resetCheckStates()
        self.close()
        
    def checkStateChanged(self):
        # Looks at the checkbox states and sets the user's options
        # (enables and disables buttons) as apropriate.
        checked_count = 0
        for row in range(self.network_model.rowCount()):
            if self.network_model.data(
                self.network_model.index(row, NWM.NET_CHECKED)):
                checked_count += 1
        if checked_count == 0:
            self.mergeButton.setDisabled(True)
            self.colorButton.setDisabled(True)
            self.deleteButton.setDisabled(True)
        elif checked_count == 1:
            self.mergeButton.setDisabled(True)
            self.colorButton.setDisabled(False)
            self.deleteButton.setDisabled(False)
        else:
            self.mergeButton.setDisabled(False)
            self.colorButton.setDisabled(True)
            self.deleteButton.setDisabled(False)

    def resetCheckStates(self):
        for row in range(self.network_model.rowCount()):
            self.network_model.setData(
                self.network_model.index(row, NWM.NET_CHECKED), False)
                
