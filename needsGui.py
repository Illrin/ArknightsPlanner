import copy

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from inventory import Depot
from Collapse import CollapsibleBox
from depotGui import MaterialButton
from operatorInfo import name_ids


class NeedsRow(QGroupBox):
    def __init__(self, parent, needs: dict, name: str, width: int, height: int, inv:Depot, person, **kwargs):
        super(NeedsRow, self).__init__(parent, **kwargs)
        self.setFixedSize(width, height)
        self.needs = needs
        self.person = person
        self.inv = inv
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft)

        baseLayout = QVBoxLayout()
        self.name = name
        nameLabel = QLabel()
        nameLabel.setText(name)
        nameLabel.setAlignment(Qt.AlignCenter)
        nameLabel.setWordWrap(True)
        nameLabel.setFixedWidth(100)
        baseLayout.addWidget(nameLabel)
        self.removeButton = QPushButton()
        self.removeButton.setFixedSize(100, 38)
        self.removeButton.setText("Remove")
        self.removeButton.pressed.connect(self.remove)
        baseLayout.addWidget(self.removeButton)

        layout.addLayout(baseLayout)

        availabilty = {-1: "Not Ready", 0: "Craftable", 1: "Ready"}
        self.ready = self.checkReady()

        craftLayout = QVBoxLayout()
        self.craftableLabel = QLabel()
        self.craftableLabel.setFixedWidth(100)
        self.craftableLabel.setText(availabilty[self.ready])
        self.craftableLabel.setAlignment(Qt.AlignCenter)
        craftLayout.addWidget(self.craftableLabel)

        self.craftButton = QPushButton()
        self.craftButton.setFixedSize(100, 38)
        self.craftButton.setText("Submit")
        self.craftButton.pressed.connect(self.submit)
        self.craftButton.setDisabled(self.ready < 0)
        craftLayout.addWidget(self.craftButton)

        layout.addLayout(craftLayout)

        self.needs = needs
        self.buttons = {}
        for id in needs:
            button = MaterialButton(self, id, 0, height-40, height-40, **kwargs)
            label = QLabel()
            label.setText(str(int(needs[id])) + '\n(' + str(int(inv.depot[id]-needs[id])) + ")")
            label.setAlignment(Qt.AlignCenter)
            materialLayout = QVBoxLayout()
            materialLayout.addWidget(button)
            materialLayout.addWidget(label)
            layout.addLayout(materialLayout)
            self.buttons[id] = [button, label]

        self.setLayout(layout)

        self.root = self.parentWidget()
        while not isinstance(self.root, QMainWindow):
            self.root = self.root.parentWidget()

    def reset_amounts(self):
        for id in self.buttons:
            self.buttons[id][0].amount = self.inv.depot[id]
            self.buttons[id][1].setText(str(int(self.needs[id])) + "\n(" + str(int(self.inv.depot[id]-self.needs[id])) + ")")
            if self.inv.depot[id]-self.needs[id] < 0:
                self.buttons[id][1].setStyleSheet("color: red;")
            else:
                self.buttons[id][1].setStyleSheet("color: black;")
        self.setReady()

    def set_amount(self, amnt: int, id):
        self.inv.depot[id] = amnt
        self.root.updateMaterials()
        self.root.resetNeeds()
        self.setReady()

    def setReady(self):
        availabilty = {-1: "Not Ready", 0: "Craftable", 1: "Ready"}
        self.ready = self.checkReady()
        self.craftableLabel.setText(availabilty[self.ready])
        self.craftButton.setDisabled(self.ready < 0)

    def checkReady(self):
        dupe = copy.deepcopy(self.inv.depot)
        needCrafts = False
        for id, amnt in self.needs.items():
            if id == "1000":
                if not self.inv.craft(dupe, id, False, True, amnt):
                    return -1
                return 1
            if dupe[id] >= amnt:
                dupe[id] -= amnt
            else:
                amnt -= dupe[id]
                for i in range(int(amnt)):
                    if not self.inv.craft(dupe, id, True):
                        return -1
                dupe[id] = 0
                needCrafts = True
        if needCrafts: return 0
        return 1

    def submit(self):
        if self.ready == 1:
            for id, amnt in self.needs.items():
                if id == "1000":
                    self.inv.upgrade(amnt)
                    continue
                self.inv.depot[id] -= amnt
        elif self.ready == 0:
            for id, amnt in self.needs.items():
                if id == "1000":
                    self.inv.upgrade(amnt)
                    continue
                if self.inv.depot[id] >= amnt:
                    self.inv.depot[id] -= amnt
                else:
                    for i in range(int(amnt - self.inv.depot[id])):
                        self.inv.craft(self.inv.depot, id, True)
                    self.inv.depot[id] -= amnt
        self.remove()

    def remove(self):
        for i in reversed(range(self.layout().count())):
            wid = self.layout().itemAt(i).widget()
            if wid is not None:
                wid.setParent(None)
                del wid
            else:
                lay = self.layout().itemAt(i).layout()
                lay.setParent(None)
                del lay
        try:
            self.root.removeNeed(self.name, self.person)
        except:
            pass
