from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

import json
from thefuzz import process

from flowlayout import FlowLayout
from depot import ids
from materialbutton import MaterialButton
from path import resource_path
from penguin import getStageDrops

with open(resource_path('json/stage_codes.json'), encoding='utf-8') as f:
    codes = json.load(f)

class FarmBox(QGroupBox):
    def __init__(self, parent, inc, drc, get, **kwargs):
        super(FarmBox, self).__init__(parent, **kwargs)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setStyleSheet('background-color: rgb(38, 54, 173); color: white; font-size: 14pt; border: 1px solid white')

        nameLayout = QHBoxLayout()
        nameLayout.setAlignment(Qt.AlignVCenter)
        nameLabel = QLabel("Stage:", self)
        nameLabel.setFixedWidth(100)
        nameLayout.addWidget(nameLabel)

        self.nameEdit = QLineEdit(self)
        self.nameEdit.textChanged.connect(self.checkStage)
        self.nameEdit.setStyleSheet('background-color: white; color: black')
        nameLayout.addWidget(self.nameEdit)
        self.nameEdit.setFixedSize(500, 35)
        self.guessLabel = QLabel(self)
        self.guessLabel.setFixedWidth(600)
        self.guessLabel.setAlignment(Qt.AlignCenter)
        nameLayout.addWidget(self.guessLabel)
        layout.addLayout(nameLayout)

        credit = QLabel("Powered by Penguin Statistics", self)
        credit.setStyleSheet("font-size: 10pt")
        credit.setFixedWidth(1200)
        layout.addWidget(credit)

        self.matScroll = QScrollArea(self)
        self.matScroll.setAlignment(Qt.AlignTop)
        self.matScroll.setWidgetResizable(True)

        self.matBox = QGroupBox(self.matScroll)
        self.matBox.setFlat(True)
        self.matBox.setStyleSheet('border: 1px solid white')
        self.matLayout = FlowLayout(None, 0,0,0)
        self.matLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.matLayout.setContentsMargins(0, 0, 0, 0)
        self.matLayout.setSpacing(0)
        self.matBox.setLayout(self.matLayout)
        self.matScroll.setWidget(self.matBox)
        layout.addWidget(self.matScroll)
        self.setLayout(layout)

        self.buttons = {}
        for i in ids:
            newButton = MaterialButton(self, i, 0 , lambda x=i: inc(x), lambda x=i: drc(x), None, 120, 120, True)
            newButton.hide()
            self.matLayout.addWidget(newButton)
            self.buttons[i] = newButton

        self.stage = None
        self.get = get

    def checkStage(self):
        if self.nameEdit.hasFocus() and len(self.nameEdit.text()) >= 2:
            oldName = self.stage if self.stage is not None else ""
            names = process.extract(self.nameEdit.text(), codes.keys(), limit=5)
            if len(names) == 0: return
            while len(names) > 1:
                if len(names[0][0]) < len(self.nameEdit.text()):
                    names.pop(0)
                else:
                    break
            if names[0][1] > 50 and names[0][1] > names[1][1]:
                if oldName != names[0][0]:
                    self.stage = names[0][0]
                    self.guessLabel.setText(names[0][0])
                    drops = getStageDrops(codes[names[0][0]])
                    for i in ids:
                        self.buttons[i].hide()
                    for i in drops:
                        button = self.buttons[i]
                        button.show()
                        button.setAmount(self.get(i))
                
