# Copyright 2013 Simon Dominic Hibbs
from PySide import QtCore
from model import NetworkModel as NM
import log


LINK_CHECKED = 0
LINK_NAME = 1
LINK_LINE = 2

LINK_LAST_COLUMN = 2


class InterWorldLinkModel(QtCore.QAbstractTableModel):
    """
    Model for the links between two specified worlds.
    This is a 'synthetic' model that draws on data from a NetworkModel object
    to present data about links between two specified worlds. InterWorldLinkModel
    objects are created as required by a view and then cleaned up, with the data
    stored in the underlying NetworkModel. Because another model stores the actual
    data, the InterWorldLinkModel requires a view to make sure it's kept up to date
    when the underlying data changes.
    """

    def __init__(self, network_model, world1, world2):
        super(InterWorldLinkModel, self).__init__()
        self.network_model = network_model
        self.world1 = world1
        self.world2 = world2

        self.network_model.linksChanged.connect(self.reset)
        


    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if index.column() == LINK_CHECKED:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)|
                                QtCore.Qt.ItemIsEditable)
        else:
            return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)|
                                QtCore.Qt.NoItemFlags)

    def getLineColor(self, row):
        link_type = self.network_model.linkTypes[row]
        return link_type.color

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.network_model.linkTypes)

    def columnCount(self, index=QtCore.QModelIndex()):
        return LINK_LAST_COLUMN + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return None
        link_type = self.network_model.linkTypes[index.row()]
        column = index.column()
        if role == QtCore.Qt.DisplayRole \
        or role == QtCore.Qt.EditRole:
            if column == LINK_CHECKED:
                xy1 = (self.world1.col, self.world1.row)
                xy2 = (self.world2.col, self.world2.row)
                is_checked = self.network_model.linkExists(xy1,
                                                           xy2,
                                                           link_type.name)
                return is_checked
            if column == LINK_NAME:
                return link_type.name
            if column == LINK_LINE:
                if role == QtCore.Qt.EditRole:
                    # used to return the style index
                    return link_type.line_style
                else:
                    # string repr
                    return link_type.line_style

        elif role == QtCore.Qt.DecorationRole:
            pass
            # Return Qlabel containing pixmap of the color?

        elif role == QtCore.Qt.TextAlignmentRole:
            return int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)

        return None


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Horizontal:
                return int(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            return int(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        if role != QtCore.Qt.DisplayRole:
            return None
        #return "Blah"
        if orientation == QtCore.Qt.Horizontal:
            if section == LINK_CHECKED:
                return "Linked"
            elif section == LINK_NAME:
                return "Network Name"
            elif section == LINK_LINE:
                return "Network Line"

        return int(section) + 1


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.network_model.linkTypes):
            link_type = self.network_model.linkTypes[index.row()]
            column = index.column()
            if column == LINK_CHECKED:
                xy1 = (self.world1.col, self.world1.row)
                xy2 = (self.world2.col, self.world2.row)
                link_type_name = link_type.name
                is_checked = self.network_model.linkExists(xy1,
                                                           xy2,
                                                           link_type.name)
                if is_checked:
                    self.network_model.removeLink(xy1, xy2, link_type_name)
                else:
                    self.network_model.addLink(xy1, xy2, link_type_name)
    
            elif column == LINK_NAME:
                pass

            elif column == LINK_LINE:
                pass

            self.dirty = True
            modelIndex1 = self.index(index.row(), 0)
            modelIndex2 = self.index(index.row(), LINK_LAST_COLUMN)
            self.dataChanged.emit(modelIndex1, modelIndex2)

            #self.network_model.linksChanged.emit()
            return True
        return False

