from PySide.QtCore import *
from PySide.QtGui import *
from log import *


class AddLabelDialog(QDialog):
    def __init__(self, cell_list, parent=None):
        super(AddLabelDialog, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle('Add Label')
        if len(cell_list) is not 1:
            debug_log('AddLabelDialog: cell_list contains more than one cell.')
            self.close()
        else:
            self.cell = cell_list[0]

        self.okButton = QPushButton("OK")

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.okButton)
        
        self.setLayout(buttonLayout)

        self.okButton.clicked.connect(self.okButtonClicked)

    def okButtonClicked(self):
        self.close()
