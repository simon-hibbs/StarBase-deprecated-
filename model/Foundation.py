# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PySide.QtCore import *
from PySide.QtGui import *
import random
from log import *



def d6():
    return random.randint(1, 6)

def target(target):
    if (d6() + d6()) >= target:
        return True
    else:
        return False

allegiance_codes = ['Na', 'Im', 'Co', 'Lw', 'Re']
allegiance_names = ['Non-alligned', 'Imperial',
                           'Confederate', 'League of World', 'Republic']
#allegiance_colors = [Qt.darkCyan, Qt.red, Qt.darkGreen, Qt.yellow,
#                     Qt.blue, Qt.darkRed, Qt.green, Qt.darkMagenta,
#                     Qt.darkYellow, Qt.cyan, Qt.lightGray, Qt.darkBlue]
allegiance_colors = ['#FFFF99', '#00FF33', '#FF0099', '#FF6600',
                     '#CCFFCC', '#993399', '#993300', '#663399']


atmosphere_display = {'Breathable' : {'codes' : ['5', '6', '8', 'D', 'E'],
                                      'color' : '#55AAFF'},
                      'Negligible' : {'codes' : ['0', '1'],
                                      'color' : '#3C3C3C'},
                      'Thin' : {'codes' : ['2', '3', '4'],
                                'color' : '#CDCDFA'},
                      'Tainted' : {'codes' : ['7', '9'],
                                   'color' : '#FFAA78'},
                      'Extreme' : {'codes' : ['A', 'B', 'C', 'F'],
                                   'color' : '#A03CFF'}
                      }

# code, ['Label', 'Number', 'Minimum', 'Number Label', 'Description']



class AttributeDefinition(object):
    ATTRIBUTE_TYPES = ['Category', 'Integer', 'Float']

    def __init__(self,
                 _data={}):
        self._data = _data
        self.name = self._data['Name']

    def index(self, code):
        return self._data['Codes'].index(code)

    @property
    def codes(self):
        return self._data['Codes']

    def label(self, code):
        if code in self._data['Codes']:
            try:
                return self._data['Code Data'][code]['Label']
            except:
                debug_log('Attribute ' + self.name + 
                          ' error finding label for code ' + str(code))
                return None
        else:
            print 'error'

    @property
    def labels(self):
        label_list = []
        for code in self._data['Codes']:
            label_list.append(self._data['Code Data'][code]['Label'])
        return label_list

    def numberLabel(self, code):
        if code in self._data['Codes']:
            try:
                return self._data['Code Data'][code]['Number Label']
            except:
                debug_log('Attribute ' + self.name + 
                          ' error finding number label for code ' + str(code))
                return ''

    def description(self, code):
        if code in self._data['Codes']:
            try:
                return self._data['Code Data'][code]['Description']
            except:
                debug_log('Attribute ' + self.name + 
                          ' error finding description for code ' + str(code))
                return ''


class Allegiance(object):
    def __init__(self, code):
        self._index = 0
        if code in allegiance_codes:
            self.code = code

    def getCode(self):
        return allegiance_codes[self._index]
    def setCode(self, value):
        if value in allegiance_codes:
            self._index = allegiance_codes.index(value)
        else:
            debug_log('Invalid Allegiance code ' + str(value))
            debug_log('Allegiances are ' + str(allegiance_codes))

    def delCode(self):
        pass
    code = property(getCode, setCode, delCode, 'Allegiance code property.')

    def getName(self):
        return allegiance_names[self._index]
    def setName(self, value):
        if value in allegiance_names and value != allegiance_names[self._index]:
            #Make sure both index and code are updated
            self.index = allegiance_names.index(value)
        else:
            debug_log('Invalid Allegiance name ' + str(value))
    def delName(self):
        pass
    name = property(getName, setName, delName, 'Allegiance name property')

    def getIndex(self):
        return self._index
    def setIndex(self, value):
        if 0 <= value < len(allegiance_codes):
            self._index = value
        else:
            debug_log('Invalid Allegiance index ' + str(value))
    def delIndex(self):
        del self._index
    index = property(getIndex, setIndex, delIndex, 'Allegiance index property')

    def __repr__(self):
        return self.code


class Sector(object):
    def __init__(self, name='Unknown', x=0, y=0):
        self.name = name
        self.sectorCol = int(x)
        self.sectorRow = int(y)

class Subsector(object):
    def __init__(self, name='Unknown', x=0, y=0):
        self.name = name
        self.subsectorCol = int(x)
        self.subsectorRow = int(y)

class World(object):
    def __init__(self, name='Unknown', x=-1, y=-1,
                 allegiance='Na', attributes=['0']):

        # Indicates if custom user text has changed
        self.dirty = False
        
        self.name = name
        self.col = int(x)
        self.row = int(y)

        self.allegiance = Allegiance(str(allegiance))

        self.attributes = attributes

    def reconfigure(self, attributes):
        self.attributes = attributes


# Tests

if __name__ == "__main__":
    atm = AttributeDefinition()
    print 'Attribute: ', atm.name
    print 'Code', 'Label', 'Min', 'Units', 'Description'
    for code in atm.codes:
        print code, atm.label(code), atm.minimum(code), atm.numberLabel(code), atm.description(code)



##def getWorldStarport():
##    starport_types = ['A', 'B', 'C', 'D', 'E', 'X']
##    starport_labels = ['A - Excellent', 'B - Good', 'C - Routine',
##                       'D - Poor', 'E - Frontier', 'X - No starport']
##    value_list = []
##    bc = 3200
##    for code in starport_types:
##        code_label = starport_labels[starport_types.index(code)]
##        value_list.append(AttributeValueTemplate(attribute_type='Category',
##                                                 code=code,
##                                                 code_label=code_label,
##                                                 minimum=bc,
##                                                 upper_limit=(bc * 2),
##                                                 number_label='Berthing Cost',
##                                                 description=code_label))
##        bc = bc / 2
##
##    starport = AttributeDefinition(name='Starport', values=value_list)
##    return starport
##
##
##
##if __name__ == "__main__":
##    starport_def = getWorldStarport()
##    for value in starport_def.values:
##        print starport_def.name, value.code, value.number_label, value.number
##
