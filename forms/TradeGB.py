from PyQt4.QtCore import *
# Copyright 2013 Simon Dominic Hibbs
#import sip
#sip.setapi('QString', 2)
#sip.setapi('QVariant', 2)

from PySide.QtGui import *
import os
from model import Models
from model import Foundation
from starmap import MapGlyphs
from starmap import MapGrid
import random
from log import *


class SkillBox(QSpinBox):
    def __init__(self, parent=None):
        super(SkillBox, self).__init__(parent)
        self.setRange(0, 99)
        
class CostBox(QSpinBox):
    def __init__(self, parent=None):
        super(CostBox, self).__init__(parent)
        self.setRange(0, 9999999)
        self.setPrefix('Cr: ')


class MerchantDetailsDialog(QDialog):
    def __init__(self, model, parent=None):
        super(MerchantDetailsDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Merchant Details Editor')
        self.model = model

        self.bestCarouseWidget = SkillBox()
        self.bestStreetiseWidget = SkillBox()
        self.firstStewardCB = QCheckBox('Chief Steward Skill')
        self.firstStewardWidget = SkillBox()
        self.secondStewardCB = QCheckBox('2nd Steward Skill')
        self.secondStewardWidget = SkillBox()
        self.thirdStewardCB = QCheckBox('3rd Steward Skill')
        self.thirdStewardWidget = SkillBox()
        self.fourthStewardCB = QCheckBox('4th Steward Skill')
        self.fourthStewardWidget = SkillBox()

        self.shipIsArmedCB = QCheckBox()

        self.bestScoutRankWidget = SkillBox()
        self.bestNavyRankWidget = SkillBox()
        self.bestSocWidget = SkillBox()

        self.bestBrokerWidget = SkillBox()
        self.bestIntWidget = SkillBox()

        self.saveMerchantDataButton = QPushButton('Save Merchant Data')

        self.noLocalGuideRB = QRadioButton("No Guide")
        self.useGuideSupplierRB = QRadioButton("Local Guide")
        self.useGuideBlackMarketRB = QRadioButton("Black Market Guide")
        self.guideCostWidget = CostBox()

        self.useLocalBrokerCB = QCheckBox('Use local broker')
        self.localBrokerDmWidget = SkillBox()
        self.brokerCostWidget = CostBox()
        
        self.determineGoodsAvailableBtn = QPushButton('Determine Goods')
        self.closeBtn = QPushButton('Close')

        merchantGroupBox = QGroupBox('Merchant Info.')
        ml = QGridLayout()
        mtext = 'Collected information about the merchant crew skills.'
        ml.addWidget(QLabel(mtext),0,0, 1,4)
        ml.addWidget(QLabel('Best Carouse Skill: '),1,0)
        ml.addWidget(self.bestCarouseWidget,1,1)
        ml.addWidget(QLabel('Best Streetwise Skill: '),2,0)
        ml.addWidget(self.bestStreetiseWidget,2,1)

        ml.addWidget(self.firstStewardCB,3,0)
        ml.addWidget(self.firstStewardWidget,3,1)

        ml.addWidget(self.secondStewardCB,4,0)
        ml.addWidget(self.secondStewardWidget,4,1)

        ml.addWidget(self.thirdStewardCB,5,0)
        ml.addWidget(self.thirdStewardWidget,5,1)

        ml.addWidget(self.fourthStewardCB,6,0)
        ml.addWidget(self.fourthStewardWidget,6,1)
        
        ml.addWidget(QLabel('Best Scout Rank: '),1,2)
        ml.addWidget(self.bestScoutRankWidget,1,3)
        ml.addWidget(QLabel('Best Navy Rank: '),2,2)
        ml.addWidget(self.bestNavyRankWidget,2,3)
        ml.addWidget(QLabel('Best Social Standing: '),3,2)
        ml.addWidget(self.bestSocWidget,3,3)

        ml.addWidget(QLabel('Best Broker Skill: '),4,2)
        ml.addWidget(self.bestBrokerWidget,4,3)
        ml.addWidget(QLabel('Best Intelligence: '),5,2)
        ml.addWidget(self.bestIntWidget,5,3)

        ml.addWidget(QLabel('Ship is armed: '),6,2)
        ml.addWidget(self.shipIsArmedCB,6,3)

        ml.addWidget(self.saveMerchantDataButton,6,4)

        merchantGroupBox.setLayout(ml)

        layout = QGridLayout()
        layout.addWidget(merchantGroupBox,0,0, 1,5)
        layout.addWidget(QLabel('Guide Options'),1,0, 1,2)
        layout.addWidget(self.noLocalGuideRB,2,0)
        layout.addWidget(self.useGuideSupplierRB,3,0)
        layout.addWidget(self.useGuideBlackMarketRB,4,0)
        layout.addWidget(QLabel('Guide Cost:'),5,0)
        layout.addWidget(self.guideCostWidget,5,1)
        
        layout.addWidget(QLabel('Broker Options'),1,2, 1,2)
        layout.addWidget(QLabel('Use Local Broker:'),2,2)
        layout.addWidget(self.useLocalBrokerCB,2,3)
        layout.addWidget(QLabel('Local Broker Skill:'),3,2)
        layout.addWidget(self.localBrokerDmWidget,3,3)
        layout.addWidget(QLabel('Broker Cost:'),5,2)
        layout.addWidget(self.brokerCostWidget,5,3)

        layout.addWidget(self.determineGoodsAvailableBtn,5,4)
        
        self.setLayout(layout)
