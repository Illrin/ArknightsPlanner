from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap, QFont, QIcon, QCursor, QImage
from PyQt5.QtWidgets import *
from materialbutton import MaterialButton
from collapsiblebox import CollapsibleBox
from depot import Depot

import json
import os
import copy

from path import resource_path

availabilty = {-1: "Not Ready", 0: "Craftable", 1: "Ready"}

class NeedRow(QGroupBox):
    def __init__(self, parent, needs: dict, name, charname, delete, sub, **kwargs):
        super(NeedRow, self).__init__(parent, **kwargs)
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setStyleSheet('background-color: rgb(38, 54, 173); font-size: 14pt; border: 1px solid white')
        self.charname = charname
        self.delete = delete
        self.sub = sub

        self.name = name
        baseLayout = QVBoxLayout()
        nameLabel = QLabel(name)
        nameLabel.setFixedWidth(239)
        nameLabel.setAlignment(Qt.AlignCenter)
        nameLabel.setWordWrap(True)
        nameLabel.setStyleSheet('color: white')
        baseLayout.addWidget(nameLabel)
        self.removeButton = QPushButton("Remove")
        self.removeButton.pressed.connect(self.remove)
        self.removeButton.setStyleSheet('color: white')
        baseLayout.addWidget(self.removeButton)

        self.layout.addLayout(baseLayout)

        craftLayout = QVBoxLayout()
        self.craftableLabel = QLabel()
        self.craftableLabel.setFixedWidth(161)
        self.craftableLabel.setAlignment(Qt.AlignCenter)
        self.craftableLabel.setStyleSheet('color: white')
        craftLayout.addWidget(self.craftableLabel)

        self.craftButton = QPushButton("Submit")
        self.craftButton.setStyleSheet('color: white')
        self.craftButton.pressed.connect(self.submit)
        craftLayout.addWidget(self.craftButton)
        self.layout.addLayout(craftLayout)

        self.needs = needs
        self.buttons = {}
        self.amounts = {}
        for k, v in needs.items():
            lay = QVBoxLayout()
            lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            button = MaterialButton(self, k, v, None, None, None, 120, 120, True)
            button.setStyleSheet('color: white')
            label = QLabel()
            label.setAlignment(Qt.AlignCenter)
            lay.addWidget(button)
            lay.addWidget(label)
            self.layout.addLayout(lay)
            self.buttons[k] = button
            self.amounts[k] = label
        self.setLayout(self.layout)

    def remove(self):
        with open(resource_path('save/needs.json')) as f:
            planner = json.load(f)
            planner[self.charname].pop(self.name)
        with open(resource_path('save/needs.json'), 'w') as f:
            json.dump(planner, f)
        self.delete(self.name)
        self.setParent(None)
        self.hide()
        self.deleteLater()

    def submit(self):
        self.sub(self.needs)
        self.remove()

    def deleteLater(self):
        for widget in self.children():
            widget.deleteLater()
        for layout in self.children():
            layout.deleteLater()
        super().deleteLater()

    def refreshInventory(self, inv):
        for k, v in self.amounts.items():
            v.setText(str(inv[k]))
            if inv[k] < self.buttons[k].getAmount():
                v.setStyleSheet('color: #f25252')
            else:
                v.setStyleSheet('color: white')
        self.ready = self.checkReady(inv)
        if self.ready == 0:
            self.craftableLabel.setText('Craftable')
            self.craftButton.setDisabled(True)
            self.craftButton.setStyleSheet('background-color: black; color: black')
        elif self.ready == 1:
            self.craftableLabel.setText('Ready')
            self.craftButton.setDisabled(False)
            self.craftButton.setStyleSheet('background-color: rgb(38, 54, 173); color: white')
        elif self.ready == -1:
            self.craftableLabel.setText('Not Ready')
            self.craftButton.setDisabled(True)
            self.craftButton.setStyleSheet('background-color: black; color: black')

    def checkReady(self, inv):
        depot = Depot()
        dupe = copy.deepcopy(inv)
        needCrafts = False
        for id, amnt in self.needs.items():
            if id == "1000":
                if depot.craft(dupe, id, False, True, amnt) != True:
                    return -1
                return 1
            if dupe[id] >= amnt:
                dupe[id] -= amnt
            else:
                amnt -= dupe[id]
                for i in range(int(amnt)):
                    if depot.craft(dupe, id, True) != True:
                        return -1
                dupe[id] = 0
                needCrafts = True
        if needCrafts: return 0
        return 1

class OperatorNeeds(CollapsibleBox):
    def __init__(self, parent, name: str, width: int, height: int, needs:dict, delete, sub, id:str="", **kwargs):
        super(OperatorNeeds, self).__init__(parent, name, width, height, id, **kwargs)
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.rows = {}
        self.needs = needs
        self.name = name
        self.charId = id
        self.delete = delete
        self.sub = sub
        for k, v in sorted(needs.items(), key=lambda x: x[0]):
            row = NeedRow(self, v, k, name, self.removeRow, sub)
            self.layout.addWidget(row)
            self.rows[k] = row

        self.setContentLayout(self.layout)

    def deleteLater(self):
        for widget in self.layout.children():
            widget.deleteLater()
        super().deleteLater()

    def refreshInventory(self, inv):
        for row in self.rows.values():
            row.refreshInventory(inv)

    def removeRow(self, key):
        self.rows.pop(key)
        if len(self.rows) == 0:
            self.deleteLater()
            self.delete(self.charId)

    

class PlannerPage(QGroupBox):
    def __init__(self, parent, sub, **kwargs):
        super(PlannerPage, self).__init__(parent, **kwargs)
        self.setStyleSheet('background-color: rgb(38, 54, 173); color: white; border: 1px solid white')
        self.ops = {}
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.sub = sub
        self.refreshNeeds()
        self.setLayout(self.layout)

    def refreshNeeds(self):
        for widget in self.ops.values():
            widget.setParent(None)
            widget.deleteLater()
        self.ops = {}
        if not os.path.isfile(resource_path('save/needs.json')): return
        with open(resource_path('save/needs.json')) as f:
            planner = json.load(f)
            for name, needs in planner.items():
                charId = needs.pop('id')
                row = OperatorNeeds(self, name, 240, 240, needs, self.deleteOp, self.sub, charId)
                self.layout.addWidget(row)
                self.ops[charId] = row

    def refreshInventory(self, inv:dict, refreshNeeds=False):
        if refreshNeeds: self.refreshNeeds()
        for row in self.ops.values():
            row.refreshInventory(inv)

    def deleteOp(self, charId):
        self.ops.pop(charId)
        with open(resource_path('save/needs.json')) as f:
            planner = json.load(f)
            toRemove = ''
            for name, needs in planner.items():
                if needs['id'] == charId:
                    toRemove = name
            if toRemove != '': planner.pop(name)
        with open(resource_path('save/needs.json'), 'w') as f:
            json.dump(planner, f)


                

