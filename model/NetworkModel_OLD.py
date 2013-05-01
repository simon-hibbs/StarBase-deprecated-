# Copyright 2013 Simon Dominic Hibbs
import copy
from PySide import QtCore
import networkx as nx
#import log

# Nodes are stored as tupples of the (column, row) coordinates for a world
# in the hex grid.

NET_CHECKED = 0
NET_NAME = 1
NET_COLOR = 2
NET_STYLE = 3

SOLID_LINE = 1
DASH_LINE = 2
DOT_LINE = 3

def intToStyle(val):
    if val == SOLID_LINE: return QtCore.Qt.SolidLine
    elif val == DASH_LINE: return QtCore.Qt.DashLine
    elif val == DOT_LINE: return QtCore.Qt.DotLine
    return 1

def styleToString(val):
    if val == QtCore.Qt.SolidLine: return str(SOLID_LINE)
    elif val == QtCore.Qt.DashLine: return str(DASH_LINE)
    elif val == QtCore.Qt.DotLine: return str(DOT_LINE)
    return 1


LINE_STYLE_LIST = (SOLID_LINE,
                   DASH_LINE,
                   DOT_LINE)

LINE_STYLE_LIST_STRINGS = (str(SOLID_LINE),
                           str(DASH_LINE),
                           str(DOT_LINE))

EDGE_NODE_1=0
EDGE_NODE_2=1
EDGE_NETWORK=2

EMPTY_LINK_TYPE = [False, 'default', '#000000', SOLID_LINE]
DEFAULT_LINK_TYPE = [False, 'Trade Routes', '#225533', SOLID_LINE]

"""
    Seriously consider switching to self.graph = nx.Graph()
    g = nx.Graph()
    g.add_node(1); g.add_node(2); g.add_node(3)
    g.add_edge(1, 2)
    g[1][2] = {'xboat': 0}
    g[1][2] =  {'xboat': 0, 'trade': 1}
    g[1][2]['trade'] = 3
"""



class NetworkModel(QtCore.QAbstractTableModel):
    """
    The NetworkModel object has two 'parts', a Qt model describing the network
    link types, and a networkx graph which contains nodes (worlds) and edges
    (which have a link type associated with them by the link type name).
    """
    linksChanged = QtCore.Signal()

    def __init__(self):
        super(NetworkModel, self).__init__()

        self.graph = nx.MultiGraph()

        self.defaultLinkType = DEFAULT_LINK_TYPE
        self.linkTypes = [self.defaultLinkType]

        self.selectedNetworkPMI = None
        self.combo_proxy_model = ComboProxyModel(self)

    def intToStyle(self, value):
        return intToStyle(value)

    def setLinkTypes(self, link_types):
        checks, names, colors, styles = zip(*link_types)
        error = False
        for edge in self.graph.edges(keys=True):
            if edge[EDGE_NETWORK] not in names:
                log.debug_log('Undefined link type found: ' + str(edge[2]))
                error = True
        if error:
            log.debug_log('Link Types: ' + str(link_types))
        self.linkTypes = link_types
        
        self.linksChanged.emit()

    def setSelectedNetworkRow(self, n):
        if n is not None:
            name_pmi = QtCore.QPersistentModelIndex(self.index(n, NET_NAME))
            self.setData(self.index(n, NET_CHECKED),True)   # make the network visible
            self.selectedNetworkPMI = name_pmi
        else:
            self.selectedNetworkPMI = None

    @property
    def selectedNetworkName(self):
        if self.selectedNetworkPMI is not None:
            name = self.selectedNetworkPMI.data()
            return name
        else:
            return None

##    @property
##    def networkNames(self):
##        return [linktype[NET_NAME] for linktype in self.linkTypes]

##  Qt Model/View functionality implemented from here

    @property
    def lastColumn(self):
        return len(self.defaultLinkType) - 1

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)|
                            QtCore.Qt.ItemIsEditable)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.linkTypes)

    def columnCount(self, index=QtCore.QModelIndex()):
        return len(self.defaultLinkType)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < len(self.linkTypes)):
            return None
        network = self.linkTypes[index.row()]
        column = index.column()
        if role == QtCore.Qt.DisplayRole \
        or role == QtCore.Qt.EditRole:
            if column == NET_CHECKED:
                return network[NET_CHECKED]

            elif column == NET_NAME:
                return network[NET_NAME]

            elif column == NET_COLOR:
                return network[NET_COLOR]

            # This needs to return an index to a list of styles
            elif column == NET_STYLE:
                if role == QtCore.Qt.EditRole:
                    # Return the style index
                    return LINE_STYLE_LIST.index(network[NET_STYLE])
                else:
                    #return str(network[NET_STYLE])    # string repr
                    return intToStyle(network[NET_STYLE])

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
            if section == NET_CHECKED:
                return "Selected"
            elif section == NET_NAME:
                return "Network Name"
            elif section == NET_COLOR:
                return "Colour"
            elif section == NET_STYLE:
                return "Line Style"

        return int(section) + 1


    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.linkTypes):
            network = self.linkTypes[index.row()]
            column = index.column()
            if column == NET_CHECKED:
                network[NET_CHECKED] = value
    
            elif column == NET_NAME:
                self.renameLinks(network[NET_NAME], value)
                network[NET_NAME] = str(value)

            elif column == NET_COLOR:
                network[NET_COLOR] = str(value)
            elif column == NET_STYLE:
                network[NET_STYLE] = LINE_STYLE_LIST[value]
            
            self.dirty = True
            modelIndex1 = self.index(index.row(), 0)
            modelIndex2 = self.index(index.row(), self.lastColumn)
            self.dataChanged.emit(modelIndex1, modelIndex2)

            self.linksChanged.emit()
            return True
        return False


    def newLinkTypeName(self, base_name='Network'):
        """Generates a unique default name for new link types."""
        def getSuffix():
            n = 0
            while 1:
                yield '_' + str(n)
                n += 1
        for suffix in getSuffix():
            candidate_name = base_name + suffix
            names = [t[NET_NAME] for t in self.linkTypes]
            if candidate_name not in names:
                return candidate_name  


    def insertRows(self, position=-1, rows=1, index=QtCore.QModelIndex()):
        #log.debug_log('WorldLinkModel: insertRows called - but dummy implementation!!')
        if position == -1:
            position = len(self.linkTypes)
        self.beginInsertRows(QtCore.QModelIndex(), position,
                             position)
        
        new_link_type = copy.copy(EMPTY_LINK_TYPE)
        new_link_type[NET_NAME] = self.newLinkTypeName()
        self.linkTypes.insert(position, new_link_type)

        self.endInsertRows()        
        self.dirty = True
        return True


    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        log.debug_log("WorldLinkTypes:About to remove row(s).")
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        log.debug_log("WorldLinkTypes:Removing row(s).")
        networks_to_delete = self.linkTypes[position:(position + rows)]

        check_boxes, dead_names, colors, styles = zip(*networks_to_delete)
        links_list = self.links
        # links are like [xy1, xy2, network_name]
        for link in links_list:
            if link[EDGE_NETWORK] in dead_names:
                self.removeLink(link[EDGE_NODE_1], link[EDGE_NODE_2], link[EDGE_NETWORK])

        self.linkTypes = self.linkTypes[:position] + \
                         self.linkTypes[position + rows:]

        self.endRemoveRows()
        self.dirty = True
        return True

##  End of Qt Model/View interface

##  Graph Functionality from here on

    @property
    def nodes(self):
        return self.graph.nodes()

    @property
    def links(self):
        # Returns a list of tupples, of the form (xy1, xy2, 'network_name')
        return self.graph.edges(keys=True)


    @property
    def fullLinkData(self):
        # links are of the form [ (node1, node2, network_name),) ]
        # returns full_links in the form: [ (node1, node2, checked, name, color), ]
        links = self.graph.edges(keys=True)
        full_links = []
        for link in links:
            # filter self.linkTypes to extract the first one with a name matching that of the current link
            link_type = filter(lambda x: x[NET_NAME] == link[EDGE_NETWORK], self.linkTypes)[0]
            (checked, name, color, style) = link_type
            # Does NOT return full link data yet!!!!!!
            full_links.append((link[EDGE_NODE_1], link[EDGE_NODE_2], checked, name, color, style))
        return full_links


    @property
    def linksWithColors(self):
        links = self.graph.edges(keys=True)
        colored_links = []
        for link in links:
            color = [t[NET_COLOR] for t in self.linkTypes if t[NET_NAME] == link[EDGE_NETWORK]][0]
            colored_links.append((link[EDGE_NODE_1], link[EDGE_NODE_2], color))
        return colored_links


    def addNode(self, xy):
        if xy not in self.nodes:
            self.graph.add_node(xy)
            #print self.graph.nodes()

    def addNodes(self, node_list):
        self.graph.add_nodes_from(node_list)

    def removeNode(self, xy):
        if xy in self.nodes:
            try:
                self.graph.remove_node(xy)
            except:
                self.graph.delete_node(xy)
        self.linksChanged.emit()
            #print self.graph.nodes()

    def nodeChanged(self, xy):
        # Placeholder in case moving worlds is ever implemented
        pass

    def testLinkChanged(self):
        self.linksChanged.emit()

    def addLink(self, xy1, xy2, network_name):
        for link_type in self.linkTypes:
            if link_type[NET_NAME] == network_name:
                self.graph.add_edge(xy1, xy2, key=network_name)
                self.linksChanged.emit()
                return
        print "network name does not exist: ", network_name
        #print self.graph.edges()

    def addLinks(self, link_list):
        for link in link_list:
            self.graph.add_edge(link[EDGE_NODE_1], link[EDGE_NODE_2], key=link[EDGE_NETWORK])
        self.linksChanged.emit()


    def renameLinks(self, old_name, new_name):
        new_graph = nx.MultiGraph()
        new_graph.add_nodes_from(self.graph.nodes())
        
        old_edges = self.graph.edges(keys=True)
        for edge in old_edges:
            if edge[EDGE_NETWORK] == old_name:
                new_graph.add_edge(edge[EDGE_NODE_1],
                                   edge[EDGE_NODE_2],
                                   key=new_name)
            else:
                new_graph.add_edge(edge[EDGE_NODE_1],
                                   edge[EDGE_NODE_2],
                                   key=edge[EDGE_NETWORK])
        self.graph = new_graph
        # The following causes problems becaus the model uses this function to rename links,
        # but before actualy changing the underlying network data. Therefore link updates
        # need to be invoked by the caller, i.e. the model setData method, not here.
        #self.linksChanged.emit()

    def removeLink(self, xy1, xy2, network_name):
        try:
            self.graph.remove_edge(xy1, xy2, key=network_name)
        except:
            self.graph.delete_edge(xy1, xy2)
        self.linksChanged.emit()
        #print self.graph.edges()
        
    def linkExists(self, xy1, xy2, network_name):
        candidate_edges =  self.graph.edges((xy1, xy2), keys=True)
        if (xy1, xy2, network_name) in candidate_edges or \
           (xy2, xy1, network_name) in candidate_edges:
            return True
        else:
            return False

    def linksFrom(self, xy1):
        edges = self.graph.edges((xy1,), keys=True)
        return edges


##    def getLinksBetween(self, xy1, xy2):
##        # Needs to be implemented
##        return None


class ComboProxyModel(QtCore.QAbstractListModel):
    """
    Proxy model used for combo box displaying list of network types.
    """
    def __init__(self, base_model):
        super(ComboProxyModel, self).__init__()
        self.base_model = base_model

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)|
                            QtCore.Qt.ItemIsEditable)

    def rowCount(self, index=QtCore.QModelIndex()):
        return self.base_model.rowCount(index) + 1

    def columnCount(self, index=QtCore.QModelIndex()):
        return 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < (len(self.base_model.linkTypes) + 1)):
            return None
        row = index.row()
        column = index.column()
        if row == 0:
            if role == QtCore.Qt.DisplayRole \
            or role == QtCore.Qt.EditRole:
                return "None"
        else:
            return self.base_model.data(
                self.base_model.createIndex(row - 1, NET_NAME),
                role)
        return None

