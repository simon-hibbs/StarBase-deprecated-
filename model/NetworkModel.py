# Copyright 2013 Simon Dominic Hibbs
import copy
from PySide import QtCore
import networkx as nx
import log
from resources import colour

# Nodes are stored as tupples of the (column, row) coordinates for a world
# in the hex grid.

NET_CHECKED = 0
NET_NAME = 1
NET_COLOR = 2
NET_STYLE = 3

NET_LAST = 3

SOLID_LINE = 1
DASH_LINE = 2
DOT_LINE = 3

CAROUSEL = ('#E02639', '#E026B5', '#3F26E0', '#26A9E0', '#26E0B5', '#26E029',
            '#C1E026', '#E0BE26', '#FA93C7', '#BC93FA', '#93C5FA', '#93FAA8',
            '#FAC893')

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

# Indexes to this list correspond to QComboBox indexes for selecting styles
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

class LinkType(object):

    def __init__(self,
                 visible=True,
                 name='Network Link',
                 color='#000000',
                 line_style=SOLID_LINE):
        
        self.visible = visible
        self.name = name
        self.color = color
        self.line_style_int = line_style

    @property
    def line_style_str(self):
        return styleToString(self.line_style_int)

    @property
    def line_style(self):
        return intToStyle(self.line_style_int)


class Link(object):

    def __init__(self, link_type=LinkType(), order=0):
	self.link_type = link_type
	self.order = order

    @property
    def visible(self):
        return self.link_type.visible

    @property
    def name(self):
        return self.link_type.name

    @property
    def color(self):
        return self.link_type.color

    @property
    def line_style_int(self):
        return self.link_type.line_style_int

    @property
    def line_style_str(self):
        return self.link_type.line_style_str

    @property
    def line_style(self):
        return self.link_type.line_style


class NetworkModel(QtCore.QAbstractTableModel):
    """
    The NetworkModel object has two 'parts', a Qt model describing the network
    link types, and a networkx graph which contains nodes (worlds) and edges
    (which have a link type associated with them by the link type name).
    """
    linksChanged = QtCore.Signal()

    def __init__(self):
        super(NetworkModel, self).__init__()

        self.graph = nx.Graph()

        self.defaultLinkType = DEFAULT_LINK_TYPE
        self.linkTypes = [LinkType()]

        self.selectedNetworkPMI = None

        # Deprecated
        #self.combo_proxy_model = ComboProxyModel(self)

    def intToStyle(self, value):
        return intToStyle(value)

    def setLinkTypes(self, link_types):
        self.graph = nx.Graph()
        self.linkTypes = []
        for lt in link_types:
            self.linkTypes.append(LinkType(visible=lt[0],
                                           name=lt[1],
                                           color=lt[2],
                                           line_style=lt[3]))
        self.linksChanged.emit()

    @property
    def oldLinkTypes(self):
        types_list = []
        for lt in self.linkTypes:
            types_list.append([lt.visible, lt.name, lt.color, lt.line_style_int])
        return types_list

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
        return NET_LAST

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemFlags(QtCore.QAbstractTableModel.flags(self, index)|
                            QtCore.Qt.ItemIsEditable)

    def rowCount(self, index=QtCore.QModelIndex()):
        return len(self.linkTypes)

    def columnCount(self, index=QtCore.QModelIndex()):
        return NET_LAST + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or \
           not (0 <= index.row() < len(self.linkTypes)):
            return None
        link_type = self.linkTypes[index.row()]
        column = index.column()
        if role == QtCore.Qt.DisplayRole \
        or role == QtCore.Qt.EditRole:
            if column == NET_CHECKED:
                return link_type.visible

            elif column == NET_NAME:
                return link_type.name

            elif column == NET_COLOR:
                return link_type.color

            # This needs to return an index to a list of styles
            elif column == NET_STYLE:
                if role == QtCore.Qt.EditRole:
                    # Return the style index
                    return LINE_STYLE_LIST.index(link_type.line_style)
                else:
                    #return str(network[NET_STYLE])    # string repr
                    return intToStyle(link_type.line_style)

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
                return "Active"
            elif section == NET_NAME:
                return "Network Name"
            elif section == NET_COLOR:
                return "Colour"
            elif section == NET_STYLE:
                return "Line Style"

        return int(section) + 1

    def setLinksVisible(self, flag):
        for link_type in self.linkTypes:
            link_type.visible = flag
            
        modelIndex1 = self.index(0, 0)
        modelIndex2 = self.index(self.rowCount() - 1, self.lastColumn)
        self.dataChanged.emit(modelIndex1, modelIndex2)

        self.linksChanged.emit()

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.linkTypes):
            link_type = self.linkTypes[index.row()]
            column = index.column()
            if column == NET_CHECKED:
                link_type.visible = value
    
            elif column == NET_NAME:
                #self.renameLinks(network[NET_NAME], value)
                link_type.name = str(value)

            elif column == NET_COLOR:
                link_type.color = str(value)
                
            elif column == NET_STYLE:
                # Works this way so QComboBox indexes can be used to select styles
                link_type.line_style_int = LINE_STYLE_LIST[value]
                        
            self.dirty = True
            modelIndex1 = self.index(index.row(), 0)
            modelIndex2 = self.index(index.row(), self.lastColumn)
            self.dataChanged.emit(modelIndex1, modelIndex2)

            self.linksChanged.emit()
            return True
        return False


    def newLinkTypeName(self, base_name='LinkType'):
        """Generates a unique default name for new link types."""
        def getSuffix():
            n = 1
            while 1:
                yield '_' + str(n)
                n += 1
        for suffix in getSuffix():
            candidate_name = base_name + suffix
            names = [t.name for t in self.linkTypes]
            if candidate_name not in names:
                return candidate_name  


    def insertRows(self, position=-1, rows=1, index=QtCore.QModelIndex()):
        #log.debug_log('WorldLinkModel: insertRows called - but dummy implementation!!')
        if position == -1:
            position = len(self.linkTypes)
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        
        new_link_type = LinkType()
        new_link_type.name = self.newLinkTypeName()
        new_link_type.color = CAROUSEL[len(self.linkTypes) - 1]
        self.linkTypes.insert(position, new_link_type)

        self.endInsertRows()        
        self.dirty = True
        return True


    def removeRows(self, position, rows=1, index=QtCore.QModelIndex()):
        log.debug_log("WorldLinkTypes:About to remove row(s).")
        self.beginRemoveRows(QtCore.QModelIndex(), position, position + rows - 1)
        log.debug_log("WorldLinkTypes:Removing row(s).")
        dead_link_types = self.linkTypes[position:(position + rows)]

        edge_list = self.links
        # edges are like [xy1, xy2, link]
        for edge in edge_list:
            link = edge[2]
            if link.link_type in dead_link_types:
                self.removeLink(edge[0], edge[1], link.name)

        self.linkTypes = self.linkTypes[:position] + \
                         self.linkTypes[position + rows:]

        self.endRemoveRows()
        self.linksChanged.emit()
        self.dirty = True
        return True

##  End of Qt Model/View interface

##  Graph Functionality from here on

    @property
    def nodes(self):
        return self.graph.nodes()

    @property
    def links(self):
        # Previously returned a list of tupples, of the form (xy1, xy2, 'network_name')
        # Returns a list of lists, of the form [[xy1, xy2, link],]
        edges = self.graph.edges() # [(xy1, xy2),]
        link_data = []
        for edge in edges:
            links = self.graph[edge[0]][edge[1]]['links']
            for link in links:
                link_data.append([edge[0], edge[1], link])
        return link_data


    @property
    def oldLinks(self):
        # Returnes a list of tupples, of the form (xy1, xy2, 'network_name')
        old_links = []
        for edge in self.links:
            old_links.append((edge[0], edge[1], edge[2].name))
        return old_links


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
        for node in (xy1, xy2):
            if node not in self.nodes:
                log.debug_log("Error: node not found in graph: " + str(node))
                return
            
        log.debug_log("addLink: "+ str(xy1) +' '+ str(xy2) +' '+ str(network_name))
        for lt in self.linkTypes:
            if lt.name == network_name:
                if xy1 in self.graph[xy2]:
                    for link in self.graph[xy1][xy2]['links']:
                        if link.name == network_name:
                            log.debug_log("Link already exists: " + \
                                          xy1 + ", " + xy2 + ", " + \
                                          network_name)
                            return
                    # Edge exists, but link doesn't
                    self.graph[xy1][xy2]['links'].append(Link(link_type=lt))
                else:
                    # Edge doesn't exist
                    self.graph.add_edge(xy1, xy2)
                    #print 'graph:', self.graph.edges() #, xy1, xy2 
                    self.graph[xy1][xy2]['links'] = [Link(link_type=lt)]
                self.linksChanged.emit()
                return
        log.debug_log("network does not exist: " + network_name)
        #print self.graph.edges()

    def addLinks(self, link_list):
        for link in link_list:
            self.addLink(link[0], link[1], link[2])
        self.linksChanged.emit()


    def renameLinks(self, old_name, new_name):
        # Possibly not needed anymore as setData does the job
        found = False
        for link_type in self.link_types:
            if link_type.name == old_name:
                found = True
                link_type.name = new_name
                self.linksChanged.emit()
        if not found:
            log.debug_log("Link type not found: " + old_name)


    def removeLink(self, xy1, xy2, network_name):
        links = self.graph[xy1][xy2]['links']
        removed = False
        for link in links:
            if link.name == network_name:
                links.remove(link)
                removed = True
        if removed:
            self.graph[xy1][xy2]['links'] = links
        else:
            log.debug_log("removeLink - Link not found: " + \
                          str(xy1) + " " + str(xy2) + \
                          " " + str(network_name))

        self.linksChanged.emit()


    def linkExists(self, xy1, xy2, network_name):
        try:
            links =  self.graph[xy1][xy2]['links']
        except:
            return False
        
        for link in links:
            if link.name == network_name:
                return True
        return False

    def linksFrom(self, xy):
        # [[xy1, xy2, link],]
        edges = self.graph.edges([xy]) # [(xy1, xy2),]
        link_data = []
        for edge in edges:
            links = self.graph[edge[0]][edge[1]]['links']
            for link in links:
                link_data.append([edge[0], edge[1], link])
        return link_data


##    def getLinksBetween(self, xy1, xy2):
##        # Needs to be implemented
##        return None


## Deprecated
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

