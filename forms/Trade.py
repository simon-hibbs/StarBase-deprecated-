from PySide.QtCore import *
# Copyright 2013 Simon Dominic Hibbs

from PySide.QtGui import *
import os
from model import Models
from model import Foundation
from starmap import MapGlyphs
from starmap import MapGrid
from forms import Buy
import random
from log import *

# Guide IDs
NO_GUIDE = 0
LOCAL_GUIDE= 1
BLACK_MARKET_GUIDE = 2

# Skill list values
SKILL_VALUES = ('None', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9')


def d6(num):
    total = 0
    for i in range(num):
        total += random.randint(1, 6)
    return total

class StatBox(QSpinBox):
    def __init__(self, parent=None):
        super(StatBox, self).__init__(parent)
        self.setRange(0, 99)

class SkillBox(QComboBox):
    def __init__(self, parent=None):
        super(SkillBox, self).__init__(parent)
        self.addItems(SKILL_VALUES)
        self.setCurrentIndex(0)

    def getSkillLevel(self):
        if self.currentIndex() > 0:
            return self.currentIndex() - 1
        else:
            return None
    def setSkillLevel(self, value):
        if value == None:
            self.setCurrentIndex(0)
        else:
            if 0 <= value <= 9:
                self.setCurrentIndex(value + 1)
            else:
                debug_log('Trade Error: Invalid skill value ' + str(value))
    def delSkillLevel(self):
        pass
    skillLevel = property(getSkillLevel, setSkillLevel, delSkillLevel,
                          'Skill level property')

        
class CostBox(QSpinBox):
    def __init__(self, parent=None):
        super(CostBox, self).__init__(parent)
        self.setRange(0, 9999999)
        self.setPrefix('Cr: ')

class DmBox(QSpinBox):
    def __init__(self, parent=None):
        super(DmBox, self).__init__(parent)
        self.setRange(0, 6)
        self.setPrefix('+')

class MarginBox(QSpinBox):
    def __init__(self, parent=None):
        super(MarginBox, self).__init__(parent)
        self.setRange(0, 99)
        self.setSuffix('%')

class PsgBox(QLineEdit):
    def __init__(self, parent=None):
        super(PsgBox, self).__init__(parent)
        


class MerchantDetailsDialog(QDialog):
    def __init__(self, model, parent=None):
        super(MerchantDetailsDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Trade Tool Setup Screen')
        self.model = model

        self.passengerCheckEffectWidget = StatBox()
        
        self.firstStewardCB = QCheckBox('Chief Steward Skill')
        self.firstStewardWidget = SkillBox()
        self.firstStewardWidget.setDisabled(True)
        self.secondStewardCB = QCheckBox('2nd Steward Skill')
        self.secondStewardWidget = SkillBox()
        self.secondStewardWidget.setDisabled(True)
        self.thirdStewardCB = QCheckBox('3rd Steward Skill')
        self.thirdStewardWidget = SkillBox()
        self.thirdStewardWidget.setDisabled(True)
        self.fourthStewardCB = QCheckBox('4th Steward Skill')
        self.fourthStewardWidget = SkillBox()
        self.fourthStewardWidget.setDisabled(True)

        self.maxHighPsg = PsgBox()
        self.maxHighPsg.setReadOnly(True)
        self.maxHighPsg.setMaximumWidth(80)
        self.maxMidPsg = PsgBox()
        self.maxMidPsg.setReadOnly(True)
        self.maxMidPsg.setMaximumWidth(80)

        self.shipIsArmedCB = QCheckBox()

        self.bestMailRankWidget = StatBox()
        self.bestSocWidget = StatBox()

        self.bestBrokerWidget = SkillBox()
        self.bestIntOrSocWidget = StatBox()

        self.saveMerchantDataButton = QPushButton('Save Merchant Data')
        self.saveMerchantDataButton.setDisabled(True)

        self.guideButtonGroup = QButtonGroup()
        self.noLocalGuideRB = QRadioButton("No Guide")
        self.useGuideSupplierRB = QRadioButton("Local Guide")
        self.useGuideBlackMarketRB = QRadioButton("Black Market Guide")
        self.noLocalGuideRB.setChecked(True)
        self.guideButtonGroup.addButton(self.noLocalGuideRB,
                                        NO_GUIDE)
        self.guideButtonGroup.addButton(self.useGuideSupplierRB,
                                        LOCAL_GUIDE)
        self.guideButtonGroup.addButton(self.useGuideBlackMarketRB,
                                        BLACK_MARKET_GUIDE)
        self.guideCostWidget = CostBox()
        self.guideCostWidget.setDisabled(True)

        self.useLocalBrokerCB = QCheckBox('Local Broker DM:')
        self.localBrokerDmWidget = DmBox()
        self.localBrokerDmWidget.setDisabled(True)
        self.localBrokerMargin = MarginBox()
        self.localBrokerMargin.setDisabled(True)
        
##        self.guideCostBtn = QPushButton('Calc. Guide Cost:')
##        self.guideCostBtn.setDisabled(True)

        self.determineGoodsBtn = QPushButton('Determine Goods')
        self.closeBtn = QPushButton('Close')

        layout = QGridLayout()
        mLabel = QLabel()
        mLabel.setTextFormat(Qt.RichText)
        mLabel.setWordWrap(True)
        intro = '<b>Characters may use Carouse or Streetwise to ' + \
                'help seek out passengers<\b>'
        mLabel.setText(intro)
        layout.addWidget(mLabel,0,0, 1,4)
        layout.addWidget(QLabel('Passenger Search Effect: '),1,0)
        layout.addWidget(self.passengerCheckEffectWidget,1,1)

        layout.addWidget(QLabel(''),2,0)
        
        stewardLabel = QLabel()
        stewardLabel.setTextFormat(Qt.RichText)
        steward_text = '<b>Calculate Steward capability.</b>'
        stewardLabel.setText(steward_text)
        layout.addWidget(stewardLabel,3,0)
        layout.addWidget(self.firstStewardCB,4,0)
        layout.addWidget(self.firstStewardWidget,4,1)

        layout.addWidget(self.secondStewardCB,5,0)
        layout.addWidget(self.secondStewardWidget,5,1)

        layout.addWidget(self.thirdStewardCB,6,0)
        layout.addWidget(self.thirdStewardWidget,6,1)

        layout.addWidget(self.fourthStewardCB,7,0)
        layout.addWidget(self.fourthStewardWidget,7,1)

        layout.addWidget(QLabel('Max. High Passengers:'),4,2)
        layout.addWidget(self.maxHighPsg,4,3)
        layout.addWidget(QLabel('Max. Mid Passengers:'),5,2)
        layout.addWidget(self.maxMidPsg,5,3)

        layout.addWidget(QLabel(''),8,0)
        
        mailLabel = QLabel()
        mailLabel.setTextFormat(Qt.RichText)
        mail_text = '<b>Mail Availability Modifiers.</b>'
        mailLabel.setText(mail_text)
        layout.addWidget(mailLabel,9,0)
        layout.addWidget(QLabel('Best Scout/Navy Rank:'),10,0)
        layout.addWidget(self.bestMailRankWidget,10,1)
        layout.addWidget(QLabel('Best Social Standing:'),11,0)
        layout.addWidget(self.bestSocWidget,11,1)
        layout.addWidget(QLabel('Ship is armed: '),12,0)
        layout.addWidget(self.shipIsArmedCB,12,1)

        #layout.addWidget(self.saveMerchantDataButton,8,4)

        layout.addWidget(QLabel(''),13,0)

        guideLabel = QLabel()
        guideLabel.setTextFormat(Qt.RichText)
        guide_text = '<b>Use a local guide to find a supplier?<\b>'
        guideLabel.setText(guide_text)
        layout.addWidget(guideLabel,14,0, 1,4)
        layout.addWidget(self.noLocalGuideRB,15,0)
        layout.addWidget(self.useGuideSupplierRB,16,0)
        layout.addWidget(self.useGuideBlackMarketRB,17,0)
        layout.addWidget(QLabel('Guide Cost:'),15,2)
        layout.addWidget(self.guideCostWidget,15,3)

        layout.addWidget(QLabel(''),18,0)
        
        brokerLabel = QLabel()
        brokerLabel.setTextFormat(Qt.RichText)
        broker_text = '<b>Price negotiation modifiers.<\b>'
        brokerLabel.setText(broker_text)
        layout.addWidget(brokerLabel,19,0, 1,2)
        layout.addWidget(self.useLocalBrokerCB,20,0)
        layout.addWidget(self.localBrokerDmWidget,20,1)
        layout.addWidget(QLabel('Broker Margin:'),20,2)
        layout.addWidget(self.localBrokerMargin,20,3)
        layout.addWidget(QLabel('Best of Int or Soc: '),21,0)
        layout.addWidget(self.bestIntOrSocWidget,21,1)
        layout.addWidget(QLabel('Best Broker Skill: '),22,0)
        layout.addWidget(self.bestBrokerWidget,22,1)

        layout.addWidget(QLabel(''),23,0)

        layout.addWidget(self.determineGoodsBtn,24,0)
        layout.addWidget(self.closeBtn,24,1)
        
        self.setLayout(layout)

        self.firstStewardCB.stateChanged[int].connect(self.stewardUpdate)
        self.secondStewardCB.stateChanged[int].connect(self.stewardUpdate)
        self.thirdStewardCB.stateChanged[int].connect(self.stewardUpdate)
        self.fourthStewardCB.stateChanged[int].connect(self.stewardUpdate)
        self.firstStewardWidget.currentIndexChanged[int].connect(self.stewardUpdate)
        self.secondStewardWidget.currentIndexChanged[int].connect(self.stewardUpdate)
        self.thirdStewardWidget.currentIndexChanged[int].connect(self.stewardUpdate)
        self.fourthStewardWidget.currentIndexChanged[int].connect(self.stewardUpdate)

        self.guideButtonGroup.buttonClicked[int].connect(self.guideChanged)
        
        self.useLocalBrokerCB.stateChanged[int].connect(self.brokerCbChanged)
        self.localBrokerDmWidget.valueChanged[int].connect(self.brokerDmChanged)

        #self.saveMerchantDataButton.clicked.connect(self.saveMerchantData)
        #.guideCostBtn.clicked.connect(self.calculateGuideCost)
        self.determineGoodsBtn.clicked.connect(self.determineGoods)
        self.closeBtn.clicked.connect(self.closeDialog)


    def stewardUpdate(self, value):
        high = 0
        mid = 0
        
        if self.firstStewardCB.isChecked():
            self.firstStewardWidget.setEnabled(True)
            val = self.firstStewardWidget.skillLevel
            if val is not None:
                high += (val + 1) * 2
                mid += (val + 1) * 5
        else:
            self.firstStewardWidget.setEnabled(False)
            self.firstStewardWidget.skillLevel = None

        if self.secondStewardCB.isChecked():
            self.secondStewardWidget.setEnabled(True)
            val = self.secondStewardWidget.skillLevel
            if val is not None:
                high += (val + 1) * 2
                mid += (val + 1) * 5
        else:
            self.secondStewardWidget.setEnabled(False)
            self.secondStewardWidget.skillLevel = None

        if self.thirdStewardCB.isChecked():
            self.thirdStewardWidget.setEnabled(True)
            val = self.thirdStewardWidget.skillLevel
            if val is not None:
                high += (val + 1) * 2
                mid += (val + 1) * 5
        else:
            self.thirdStewardWidget.setEnabled(False)
            self.thirdStewardWidget.skillLevel = None
        
        if self.fourthStewardCB.isChecked():
            self.fourthStewardWidget.setEnabled(True)
            val = self.fourthStewardWidget.skillLevel
            if val is not None:
                high += (val + 1) * 2
                mid += (val + 1) * 5
        else:
            self.fourthStewardWidget.setEnabled(False)
            self.fourthStewardWidget.skillLevel = None
        
        self.maxHighPsg.setText(str(high))
        self.maxMidPsg.setText(str(mid))


    def guideChanged(self, value):
        if value == NO_GUIDE:
            #self.guideCostBtn.setDisabled(True)
            self.guideCostWidget.setValue(0)
            self.guideCostWidget.setDisabled(True)
            
        elif value == LOCAL_GUIDE:
            #self.guideCostBtn.setDisabled(False)
            self.guideCostWidget.setDisabled(False)
            cost = d6(1) * 100
            self.guideCostWidget.setValue(cost)

        elif value == BLACK_MARKET_GUIDE:
            #self.guideCostBtn.setDisabled(False)
            self.guideCostWidget.setDisabled(False)
            cost = d6(1) * 500
            self.guideCostWidget.setValue(cost)

    def brokerCbChanged(self, value):
        if self.useLocalBrokerCB.isChecked():
            self.localBrokerDmWidget.setDisabled(False)
            self.localBrokerMargin.setDisabled(False)
            self.bestBrokerWidgetskillLevel = None
            self.bestBrokerWidget.setDisabled(True)
        else:
            self.localBrokerDmWidget.setValue(0)
            self.localBrokerDmWidget.setDisabled(True)
            self.localBrokerMargin.setValue(0)
            self.localBrokerMargin.setDisabled(True)
            self.bestBrokerWidget.setDisabled(False)


    def brokerDmChanged(self, value):
        if value == 0:
            self.localBrokerMargin.setValue(0)
        elif value == 1:
            self.localBrokerMargin.setValue(1)
        elif value == 2:
            self.localBrokerMargin.setValue(2)
        elif value == 3:
            self.localBrokerMargin.setValue(5)
        elif value == 4:
            self.localBrokerMargin.setValue(7)
        elif value == 5:
            self.localBrokerMargin.setValue(10)
        elif value >= 6:
            self.localBrokerMargin.setValue(15)
        

    def applyMerchantData(self):
        self.model.merchant.passengerCheckEffect = \
            self.passengerCheckEffectWidget.value()

        self.stewardSkills = []
        for steward in (self.firstStewardWidget,
                        self.secondStewardWidget,
                        self.thirdStewardWidget,
                        self.fourthStewardWidget):
            if steward.skillLevel is not None:
                self.model.merchant.stewardSkills.append(steward.skillLevel)
        try:
            self.model.merchant.highPassengerLimit = int(self.maxHighPsg.text())
        except:
            self.model.merchant.highPassengerLimit = 0
        try:
            self.model.merchant.midPassengerLimit = int(self.maxMidPsg.text())
        except:
            self.model.merchant.midPassengerLimit = 0

        self.model.merchant.bestMailRank = self.bestMailRankWidget.value()
        self.model.merchant.bestSoc = self.bestSocWidget.value()
        self.model.merchant.shipIsArmed = self.shipIsArmedCB.isChecked()

        self.model.merchant.guideOption = self.guideButtonGroup.checkedId()
        try:
            self.model.merchant.guideCost = int(self.guideCostWidget.text())
        except:
            self.model.merchant.guideCost = 0
        
        self.model.merchant.useLocalBroker = self.useLocalBrokerCB.isChecked()
        self.model.merchant.localBrokerDM = self.localBrokerDmWidget.value()
        self.model.merchant.localBrokerMargin = self.localBrokerMargin.value()
        self.model.merchant.bestIntOrSoc = self.bestIntOrSocWidget.value()
        self.model.merchant.bestBroker = self.bestBrokerWidget.skillLevel


    def closeDialog(self):
        self.result = None
        self.close()

    def determineGoods(self):
        self.applyMerchantData()
        self.buyDialog = Buy.BuyDialog(self.model, self)
        self.buyDialog.show()
        self.buyDialog.activateWindow()
        
        


                           
