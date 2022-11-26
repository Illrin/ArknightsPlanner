from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QSpinBox, QAbstractSpinBox, QGroupBox, QPushButton, \
    QMainWindow
from PyQt5.QtCore import Qt
from operatorInfo import *
from inventory import *


class OperatorTable(QGridLayout):
    def __init__(self, parent, groupBox, total: dict, **kwargs):
        super(OperatorTable, self).__init__()
        self.group = groupBox
        self.total = total
        self.charInfo = None
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.avatar = QLabel(parent)
        self.avatar.setFixedSize(186,186)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.addWidget(self.avatar, 1, 0, 2, 2)

        labels = []
        labels.append(QLabel(parent))
        labels[0].setText("Name")
        self.addWidget(labels[0], 0, 0, 1, 4)

        self.nameInput = QLineEdit(parent)
        self.nameInput.setAlignment(Qt.AlignCenter)
        self.nameInput.setStyleSheet("background-color: rgb(200, 200, 200);")
        self.nameInput.textChanged.connect(self.check_name)
        self.addWidget(self.nameInput, 0, 4, 1, 5)

        self.job = QLabel(parent)
        self.addWidget(self.job, 1, 2, 1, 2)
        self.job.setFixedSize(124, 124)
        self.setRowMinimumHeight(1, 124)
        self.setRowMinimumHeight(2, 62)
        self.job.setAlignment(Qt.AlignCenter)
        self.subjob = QLabel(parent)
        self.subjob.setAlignment(Qt.AlignCenter)
        self.addWidget(self.subjob, 1, 4, 1, 2)
        self.subjob.setFixedSize(124, 124)

        labels.append(QLabel(parent))
        labels[1].setText("Elite")
        self.addWidget(labels[1], 2,2)

        labels.append(QLabel(parent))
        labels[2].setText("Level")
        self.addWidget(labels[2], 2, 3)

        labels.append(QLabel(parent))
        labels[3].setText("Skill Lvl")
        self.addWidget(labels[3], 2, 4)

        self.skLabels = (QLabel(parent),QLabel(parent),QLabel(parent))
        for k in self.skLabels:
            k.setAlignment(Qt.AlignCenter)
            k.setFixedSize(62,62)
        self.addWidget(self.skLabels[0], 2, 5)
        self.addWidget(self.skLabels[1], 2, 6)
        self.addWidget(self.skLabels[2], 2, 7)

        self.modLabels = {}
        self.modLabels["X"] = QLabel(parent)
        self.modLabels["X"].setAlignment(Qt.AlignCenter)
        self.addWidget(self.modLabels["X"], 1, 8, 2, 2)

        self.modLabels["Y"] = QLabel(parent)
        self.modLabels["Y"].setAlignment(Qt.AlignCenter)
        self.addWidget(self.modLabels["Y"], 1, 10, 2, 2)

        button = QPushButton(parent)
        button.pressed.connect(self.submit)
        button.setText("Submit")
        button.setFixedSize(124, 124)
        self.addWidget(button, 1, 6, 1, 2)

        empty = QLabel(parent)
        self.addWidget(empty, 0, 9, 1, 3)

        labels.append(QLabel(parent))
        labels[4].setText("Before")
        self.addWidget(labels[4], 3, 0, 1, 2)

        labels.append(QLabel(parent))
        labels[5].setText("After")
        self.addWidget(labels[5], 4, 0, 1, 2)

        for label in labels:
            label.setAlignment(Qt.AlignCenter)

        self.edits = [[], []]
        for i in range(2):
            for a in range(6):
                self.edits[i].append(QSpinBox(parent))
                self.edits[i][a].setButtonSymbols(QAbstractSpinBox.NoButtons)
                self.addWidget(self.edits[i][a], i+3, a+2)
            self.edits[i].append(QSpinBox(parent))
            self.edits[i][6].setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.addWidget(self.edits[i][6], i + 3, 8, 1, 2)
            self.edits[i].append(QSpinBox(parent))
            self.edits[i][7].setButtonSymbols(QAbstractSpinBox.NoButtons)
            self.addWidget(self.edits[i][7], i + 3, 10, 1, 2)

        for i in range(2):
            self.edits[i][2].setRange(1,7)
            for a in range(3,6):
                self.edits[i][a].setRange(0,3)
                self.edits[i][a].valueChanged.connect(self.check_specs)
            for a in range(6,8):
                self.edits[i][a].setRange(0,3)
                self.edits[i][a].valueChanged.connect(self.check_mods)
            self.edits[i][0].valueChanged.connect(self.check_elites)
            self.edits[i][1].setMinimum(1)
            self.edits[i][1].valueChanged.connect(self.check_levels)
            self.edits[i][2].setMinimum(1)
            self.edits[i][2].valueChanged.connect(self.check_skills)

        self.reset_edits()
        self.needs = {}

        self.needImages = QGroupBox(parent)
        self.needLayout = QGridLayout()
        self.needImages.setLayout(self.needLayout)
        self.needLayout.setContentsMargins(0, 0, 0, 0)
        self.needLayout.setSpacing(0)
        self.needLayout.setAlignment(Qt.AlignLeft)
        self.needLayout.setAlignment(Qt.AlignTop)
        self.addWidget(self.needImages, 6, 0, 12, 12)

        self.root = parent
        while not isinstance(self.root, QMainWindow):
            self.root = self.root.parentWidget()

    def submit(self):
        self.update_needs()
        if len(self.needs) != 0:
            name = self.nameInput.text().lower()
            if name not in self.total:
                self.total[name] = {}
            self.total[name].update(self.needs)
        self.nameInput.setText("")
        self.check_name()
        self.root.rebuildNeeds()

    def update_needs(self):
        self.needs = {}
        if self.charInfo is None: return
        if self.edits[0][0].value() == self.edits[1][0].value() and \
                self.edits[0][1].value() < self.edits[1][1].value():
            elite = self.edits[0][0].value()
            start = self.edits[0][1].value()
            end = self.edits[1][1].value()
            self.needs["Level E" + str(elite) + " " + str(start) + " -> " + str(end)] = get_exp_costs(elite, start, end)
        elif self.edits[0][0].value() != self.edits[1][0].value():
            level_limits = [[30, 0, 0], [30, 0, 0], [40, 55, 0], [45, 60, 70], [50, 70, 80], [50, 80, 90]]
            startElite = self.edits[0][0].value()
            endElite = self.edits[1][0].value()
            initialLevel = self.edits[0][1].value()
            finalLevel = self.edits[1][1].value()
            for i in range(startElite, endElite+1):
                if i == startElite: startLevel = initialLevel
                else: startLevel = 1
                if i == endElite: endLevel = finalLevel
                else:
                    endLevel = level_limits[self.charInfo["rarity"]-1][i]
                if startLevel == endLevel: continue
                self.needs["Level E" + str(i) + " " + str(startLevel) + " -> " + str(endLevel)] = get_exp_costs(i, startLevel, endLevel)
        for i in range(self.edits[0][0].value()+1, self.edits[1][0].value()+1):
            self.needs["Elite " + str(i)] = get_elite_cost(self.charInfo["name"], i)
        for i in range(self.edits[0][2].value()+1, self.edits[1][2].value()+1):
            self.needs["Skill Lvl " + str(i)] = get_skill_cost(self.charInfo["name"], i)
        for a in range(3):
            for i in range(self.edits[0][a+3].value()+1, self.edits[1][a+3].value()+1):
                self.needs["S" + str(a+1) + "M" + str(i)] = get_specs_cost(self.charInfo["name"], i, a+1)
        for a in range(2):
            types = ["X", "Y"]
            for i in range(self.edits[0][a+6].value()+1, self.edits[1][a+6].value()+1):
                self.needs["Mod" + types[a] + " Lvl " + str(i)] = get_mod_cost(self.charInfo["name"], i, types[a])
        self.update_materials()

    def update_materials(self):
        for i in reversed(range(self.needLayout.count())):
            wid = self.needLayout.itemAt(i).widget()
            wid.setParent(None)
            del wid
        sumNeeds = {}
        r = 0
        c = 0
        for needs in self.needs.values():
            for k, v in needs.items():
                if k not in sumNeeds:
                    sumNeeds[k] = v
                else: sumNeeds[k] += v
        extras = copy.deepcopy(ids)
        extras.insert(0, "1000")
        for k, v in sorted(sumNeeds.items(), key=lambda x: extras.index(x[0])):
            mat = QLabel()
            image = QPixmap("Images/materials/" + k + ".png")
            image = image.scaled(79, 79, transformMode=Qt.SmoothTransformation)
            mat.setPixmap(image)
            mat.setFixedSize(79,79)
            self.needLayout.addWidget(mat, r, c)
            name = QLabel()
            name.setFixedSize(79, 20)
            name.setText(str(int(v)))
            self.needLayout.addWidget(name, r+1, c)
            c += 1
            if c == 10:
                r += 2
                c = 0
        self.needImages.setLayout(self.needLayout)
        if len(sumNeeds) > 0:
            self.group.setMinimumHeight(260 + (99 * ((r/2) + 1)))

    def check_elites(self):
        level_limits = [[30, 0, 0],[30, 0, 0],[40, 55, 0],[45, 60, 70],[50, 70, 80],[50, 80, 90]]

        self.edits[1][0].setMinimum(self.edits[0][0].value())
        if self.charInfo is not None:
            self.edits[0][1].setMaximum(level_limits[self.charInfo["rarity"] - 1][self.edits[0][0].value()])
            self.edits[1][1].setMaximum(level_limits[self.charInfo["rarity"] - 1][self.edits[1][0].value()])
        if self.edits[1][0].value() == self.edits[0][0].value():
            self.edits[1][1].setMinimum(self.edits[0][1].value())
        for i in range(2):
            if self.edits[i][0].value() == 0:
                self.edits[i][2].setMaximum(4)
            else:
                self.edits[i][2].setMaximum(7)
            for a in range(3,6):
                banned = self.edits[i][0].value() != 2
                self.edits[i][a].setDisabled(banned)
                if banned: self.edits[i][a].setValue(0)
        self.check_skills()
        self.update_needs()

    def check_levels(self):
        if self.edits[1][0].value() == self.edits[0][0].value():
            self.edits[1][1].setMinimum(self.edits[0][1].value())
        self.update_needs()

    def check_skills(self):
        self.edits[1][2].setMinimum(self.edits[0][2].value())
        for i in range(2):
            cantSpec = self.edits[i][2].value() != 7
            if self.charInfo is None:
                for a in range(3):
                    self.edits[i][a+3].setDisabled(True)
                continue
            for a in range(3):
                if self.charInfo["skills"][a] is not None:
                    self.edits[i][a+3].setDisabled(cantSpec)
                else:
                    self.edits[i][a+3].setDisabled(True)
        self.update_needs()

    def check_specs(self):
        for i in range(3,6):
            self.edits[1][i].setMinimum(self.edits[0][i].value())
        self.update_needs()

    def check_mods(self):
        for i in range(6, 8):
            self.edits[1][i].setMinimum(self.edits[0][i].value())
        self.update_needs()

    def check_name(self):
        name = self.nameInput.text()
        self.charInfo = get_operator(name)
        if self.charInfo is not None:
            self.full_change(False)
            self.update_images()
            self.reset_edits()
            self.check_elites()
        else:
            self.needs = {}
            self.reset_images()
            self.reset_edits()
            self.update_materials()

    def full_change(self, disable):
        for i in range(2):
            for a in range(8):
                self.edits[i][a].setDisabled(disable)

    def reset_edits(self):
        for i in range(2):
            for a in range(8):
                self.edits[i][a].setValue(0)

        if self.charInfo is None:
            self.full_change(True)
            return

        blackout = False
        for i in range(len(self.charInfo["skills"])):
            if self.charInfo["skills"][i] is None: blackout = True
            for a in range(2):
                self.edits[a][i+3].setDisabled(blackout)

        for a in range(2):
            self.edits[a][6].setDisabled(self.charInfo["modules"]["X"] is None)
            self.edits[a][7].setDisabled(self.charInfo["modules"]["Y"] is None)
            eliteLimit = {1: 0, 2: 0, 3: 1, 4: 2, 5: 2, 6: 2}
            self.edits[a][0].setRange(0, eliteLimit[self.charInfo["rarity"]])

    def reset_images(self):
        self.avatar.setPixmap(QPixmap())
        self.job.setPixmap(QPixmap())
        self.subjob.setPixmap(QPixmap())
        for i in self.skLabels:
            i.setPixmap(QPixmap())
        for i in self.modLabels.values():
            i.setPixmap(QPixmap())


    def update_images(self):
        self.avatar.setPixmap(QPixmap("Images/avatars/" + self.charInfo["id"] + ".png"))

        jobIcon = QPixmap("Images/classes/class_" + self.charInfo["class"] + ".png")
        jobIcon = jobIcon.scaled(120, 120, transformMode=Qt.SmoothTransformation)
        self.job.setPixmap(jobIcon)

        jobIcon = QPixmap("Images/subclass/sub_" + self.charInfo["subclass"] + "_icon.png")
        self.subjob.setPixmap(jobIcon)

        for i in range(len(self.charInfo["skills"])):
            if self.charInfo["skills"][i] is None:
                jobIcon = QPixmap()
            else:
                jobIcon = QPixmap("Images/skills/skill_icon_" + self.charInfo["skills"][i] + ".png")
            jobIcon = jobIcon.scaled(62, 62, transformMode=Qt.SmoothTransformation)
            self.skLabels[i].setPixmap(jobIcon)

        for i in self.charInfo["modules"]:
            if self.charInfo["modules"][i] is None:
                jobIcon = QPixmap()
            else:
                jobIcon = QPixmap("Images/equip/" + self.charInfo["modules"][i] + ".png")
            jobIcon = jobIcon.scaled(112,112, transformMode=Qt.SmoothTransformation)
            self.modLabels[i].setPixmap(jobIcon)

