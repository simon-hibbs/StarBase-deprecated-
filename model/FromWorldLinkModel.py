# Copyright 2013 Simon Dominic Hibbs
from PySide import QtCore
from PySide import QtGui
from model import NetworkModel as NM
import log

ColorRole = 32

LINKED_WORLD_NAME = 0
LINK_TYPE_NAME = 1
LINK_LINE = 2

LAST_COLUMN = 2

# For use in the World Editor, displays links from a given world. Read-Only.
# A new model will need to be created as required.

class FromWorldLinkModel(QtCore.QAbstractTableModel):

    def __init__(self, world_pmi):
        super(FromWorldLinkModel, self).__init__()
        self.world_model = world_pmi.model()
        self.network_model = self.world_model.network_model
        self.world_pmi = world_pmi
        self.world = self.world_pmi.model().getWorld(self.world_pmi)
        self.xy = (self.world.col, self.world.row)

        self.network_model.linksChanged.connect(self.reset)
        self.world_model.dataChanged.connect(self.reset)

    def flags(self, index):
        #if not index.isValid():
        #    return QtCore.Qt.ItemIsEnabled
        #return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)|
        #                        QtCore.Qt.NoItemFlags)
        return QtCore.Qt.ItemIsEnabled

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.network_model.linksFrom(self.xy))

    def columnCount(self, index=QtCore.QModelIndex()):
        return LAST_COLUMN + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < self.rowCount()):
            return None
        link_list = sorted(self.network_model.linksFrom(self.xy))
        #log.debug_log("FWLM data: " + str(link_list))
        link_data = link_list[index.row()]
        link = link_data[2]
        if link_data[0] == self.xy:
            linked_world_xy = link_data[1]
        elif link[1] == self.xy:
            linked_world_xy = link_data[0]
        else:
            log.debug_log("Link does not contain orriginating hex: " + \
                          self.xy + " " + link_data)
        column = index.column()

        if role == QtCore.Qt.DisplayRole \
        or role == QtCore.Qt.EditRole \
        or role == ColorRole:
            
            if column == LINKED_WORLD_NAME:
                return self.world_model.getWorldAt(linked_world_xy).name

            if column == LINK_TYPE_NAME:
                return link.name

            if column == LINK_LINE:
                if role == ColorRole:
                    return link.color
                else:
                    return link.line_style

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
            if section == LINKED_WORLD_NAME:
                return "Connected World"

            if section == LINK_TYPE_NAME:
                return "Connection Type"

            if section == LINK_LINE:
                return "Map Line"

        return int(section) + 1

