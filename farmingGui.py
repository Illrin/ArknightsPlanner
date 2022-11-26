from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from depotGui import MaterialButton
import io, json
from apiInteraction import getStageDrops, updateStages


class FarmingGroup(QGroupBox):
    def __init__(self, parent, width: int, height: int, inv, **kwargs):
        super(FarmingGroup, self).__init__(parent, **kwargs)
        self.setFixedWidth(width)
        self.inv = inv

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        nameBox = QHBoxLayout()
        title = QLabel()
        title.setText("Stage Code:")
        title.setFont(QFont("Sans Serif", 24))
        nameBox.addWidget(title)

        self.stageInput = QLineEdit()
        self.stageInput.setFont(QFont("Sans Serif", 24))
        self.stageInput.setAlignment(Qt.AlignCenter)
        self.stageInput.setStyleSheet("background-color: rgb(200, 200, 200);")
        self.stageInput.textChanged.connect(self.check_name)
        nameBox.addWidget(self.stageInput)
        self.mainLayout.addLayout(nameBox)

        powerLabel = QLabel()
        powerLabel.setText("Powered by Penguin Statistics (https://penguin-stats.io/)")
        self.mainLayout.addWidget(powerLabel)

        self.buttons = QGroupBox()
        self.mats = {}
        self.mainLayout.addWidget(self.buttons)

        self.setLayout(self.mainLayout)

        self.root = self.parentWidget()
        while not isinstance(self.root, QMainWindow):
            self.root = self.root.parentWidget()

        self.update_data()

    def update_data(self):
        updateStages()
        f = io.open("Data/stage_codes.json", encoding='utf-8')
        self.codes = json.load(f)
        f.close()

    def check_name(self):
        stageId = self.codes.get(self.stageInput.text().upper(), None)
        if stageId is not None:
            self.drops = getStageDrops(stageId)
        else:
            return
        self.update_images()

    def update_images(self):
        self.mainLayout.itemAt(2).widget().setParent(None)
        self.buttons = QGroupBox()
        buttons = QVBoxLayout()
        self.mats = {}
        i = 0
        a = 1
        toAdd = QHBoxLayout()
        for id in self.drops:
            box = QSpinBox()
            box.setMaximum(999999999)
            box.setValue(self.inv[id])
            box.setButtonSymbols(QAbstractSpinBox.NoButtons)
            box.setAlignment(Qt.AlignCenter)
            box.setMaximumWidth(79)
            box.valueChanged.connect(lambda: self.set_amount(box.value(), id))
            button = MaterialButton(self, id, self.inv[id], 79, 79)
            self.mats[id] = [button, box]
            mat = QVBoxLayout()
            mat.addWidget(button)
            mat.addWidget(box)
            toAdd.addLayout(mat)
            i += 1
            if i % 10 == 0:
                toAdd.setAlignment(Qt.AlignLeft)
                buttons.addLayout(toAdd)
                toAdd = QHBoxLayout()
                a += 1
        if i % 8 == 0: a -= 1
        toAdd.setAlignment(Qt.AlignLeft)
        buttons.addLayout(toAdd)
        buttons.setSpacing(0)
        buttons.setContentsMargins(0, 0, 0, 0)
        buttons.setAlignment(Qt.AlignTop)
        self.buttons.setMinimumHeight(a*80)
        self.buttons.setLayout(buttons)
        self.mainLayout.addWidget(self.buttons)

    def set_amount(self, amnt, id):
        self.mats[id][1].setValue(amnt)
        self.inv[id] = amnt

    def update_vals(self):
        for id in self.mats:
            self.mats[id][0].amount = self.inv[id]
            self.mats[id][1].setValue(self.inv[id])
