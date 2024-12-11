from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap, QFont, QIcon, QCursor, QImage
from PyQt5.QtWidgets import *
from materialbutton import MaterialButton
import pickle
import os
import copy
from thefuzz import process
import urllib.request
import json
import numpy as np
from collections import defaultdict
from depot import ids
from flowlayout import FlowLayout
from path import resource_path
import pprint

with open(resource_path('save/akChars.pkl'), mode='rb') as f:
    characters = pickle.load(f)

eliteLimits = [None, 0,0,1,2,2,2]
level_limits = [None, [30, 0, 0],[30, 0, 0],[40, 55, 0],[45, 60, 70],[50, 70, 80],[50, 80, 90]]
mod_unlock = [None, None, None, None, 40, 50, 60]
eliteCosts = [None, None, None, [None, 10000], [None, 15000, 60000], [None, 20000, 120000], [None, 30000, 180000] ]
with open(resource_path('json/exp.json')) as f:
    exps = json.load(f)

class OpSubmissionBox(QGroupBox):
    def __init__(self, parent, update=None, **kwargs):
        super(OpSubmissionBox, self).__init__(parent, **kwargs)
        self.preloaded = False
        self.reloadPlanner = update
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setStyleSheet('background-color: rgb(38, 54, 173); color: white; font-size: 14pt; border: 1px solid white')

        nameLayout = QHBoxLayout()
        nameLayout.setAlignment(Qt.AlignVCenter)
        nameLabel = QLabel("Name:", self)
        nameLabel.setFixedWidth(100)
        nameLayout.addWidget(nameLabel)
        self.nameEdit = QLineEdit(self)
        self.nameEdit.textChanged.connect(self.checkCharacter)
        self.nameEdit.setStyleSheet('background-color: white; color: black')
        nameLayout.addWidget(self.nameEdit)
        self.nameEdit.setFixedSize(500, 35)
        self.guessLabel = QLabel(self)
        self.guessLabel.setFixedWidth(600)
        self.guessLabel.setAlignment(Qt.AlignCenter)
        nameLayout.addWidget(self.guessLabel)
        layout.addLayout(nameLayout)

        subBox = QGroupBox(self)
        subBox.setFlat(True)
        subBox.setStyleSheet('border: 1px solid white')
        subLayout = QHBoxLayout()
        subLayout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        subLayout.setContentsMargins(0,0,0,0)
        subLayout.setSpacing(0)
        self.portrait = QLabel()
        self.portrait.setFixedSize(240, 240)
        subLayout.addWidget(self.portrait)

        grid = QGridLayout()
        grid.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        self.job = QLabel()
        self.subjob = QLabel()
        self.submit = QPushButton("Submit")
        self.submit.pressed.connect(lambda: self.submitNeeds())
        self.submit.setStyleSheet('background-color: #505aa3')
        elabel = QLabel("Elite")
        llabel = QLabel("Level")
        slabel = QLabel("Skill Lvl")
        i, a = 0, 0
        for widget in [self.job, self.subjob, self.submit, elabel, llabel, slabel]:
            widget.setFixedSize(120, 120)
            try:
                widget.setAlignment(Qt.AlignCenter)
            except:
                pass
            grid.addWidget(widget, i, a, Qt.AlignCenter)
            a += 1
            if a == 3:
                a = 0
                i += 1
        subLayout.addLayout(grid)

        midLayout = QVBoxLayout()
        midLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        scrollLable = QLabel("Scroll to change values!\nValues are limited by Elite\nie need at least E1 for SK7")
        scrollLable.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        scrollLable.setFixedHeight(120)
        midLayout.addWidget(scrollLable)
        skillLayout = QHBoxLayout()
        skillLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.skills = [QLabel(), QLabel(), QLabel()]
        for skill in self.skills:
            skill.setFixedSize(120, 120)
            skill.setAlignment(Qt.AlignCenter)
            skillLayout.addWidget(skill)
        midLayout.addLayout(skillLayout)
        subLayout.addLayout(midLayout)
        
        modLayout = QGridLayout()
        modLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.mods = [[QLabel(), QLabel()], [QLabel(), QLabel()], [QLabel(), QLabel()]]
        for i in range(len(self.mods)):
            for a in range(len(self.mods[i])):
                self.mods[i][a].setFixedSize(120, 120)
                self.mods[i][a].setAlignment(Qt.AlignCenter)
                modLayout.addWidget(self.mods[i][a], a, i)
        subLayout.addLayout(modLayout)

        subBox.setLayout(subLayout)
        layout.addWidget(subBox)

        self.edits = [[QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self)],
                           [QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self), QSpinBox(self)]]

        for i in range(len(self.edits)):
            for a in range(len(self.edits[i])):
                if a == 1: continue
                self.edits[i][a].lineEdit().setReadOnly(True)
        beforeLayout = QHBoxLayout()
        beforeLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        before = QLabel('Before')
        before.setAlignment(Qt.AlignCenter)
        before.setFixedWidth(240)
        beforeLayout.addWidget(before)
        for widget in self.edits[0]:
            beforeLayout.addWidget(widget)
        layout.addLayout(beforeLayout)

        afterLayout = QHBoxLayout()
        afterLayout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        after = QLabel('After')
        after.setAlignment(Qt.AlignCenter)
        after.setFixedWidth(240)
        afterLayout.addWidget(after)
        for widget in self.edits[1]:
            afterLayout.addWidget(widget)
        layout.addLayout(afterLayout)

        for arr in self.edits:
            for widget in arr:
                widget.setFixedWidth(120)
                widget.setDisabled(True)
                widget.setStyleSheet('background-color: black; color: black')
                widget.setButtonSymbols(QAbstractSpinBox.NoButtons)
                widget.valueChanged.connect(lambda: self.update())

        self.totalScroll = QScrollArea(self)
        self.totalScroll.setAlignment(Qt.AlignTop)
        self.totalScroll.setWidgetResizable(True)
        self.totalBox = QGroupBox(self.totalScroll)
        self.totalBox.setFlat(True)
        self.totals = FlowLayout(None, 0, 0, 0)
        self.totals.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.totals.setContentsMargins(0, 0, 0, 0)
        self.totals.setSpacing(0)
        self.totalBox.setLayout(self.totals)
        self.totalScroll.setWidget(self.totalBox)
        layout.addWidget(self.totalScroll)
        
        self.setLayout(layout)

        self.needs = {}
        self.totalMats = {}
        self.needButtons = {}
        for i in ['1000'] + ids:
            newButton = MaterialButton(self, i, 0, None, None, None, 150, 150, True)
            newButton.hide()
            self.totals.addWidget(newButton)
            self.needButtons[i] = newButton

        self.character = None

    def update(self):
        for arr in self.edits:
            for widget in arr:
                widget.blockSignals(True)
        self.validate()
        for arr in self.edits:
            for widget in arr:
                widget.blockSignals(False)
        self.postTotals(self.adjustNeeds())

    def postTotals(self, changes):
        for k,v in changes.items():
            if v == 0: continue
            if k not in self.totalMats:
                self.totalMats[k] = v
                self.needButtons[k].show()
                self.needButtons[k].setAmount(v)
            else:
                self.totalMats[k] += v
                self.needButtons[k].changeAmount(v)
                if self.totalMats[k] <= 0:
                    self.totalMats.pop(k)
                    self.needButtons[k].hide()

    def submitNeeds(self):
        needs = {}
        for k, v in self.needs.items():
            mats = {}
            for mat in v:
                mats[mat['id']] = int(mat['count'])
            needs[k] = mats
        if len(needs.keys()) == 0:
            dlg = QMessageBox()
            dlg.setStyleSheet('background-color: rgb(38, 54, 173); color: white; font-size: 14pt;')
            dlg.setWindowTitle("No Change")
            dlg.setText("No unit changes found.")
            dlg.exec()
            return
        needs['id'] = self.character.id
        needs = {self.character.name: needs}
        if os.path.isfile(resource_path('save/needs.json')):
            r = open(resource_path('save/needs.json'), 'r')
            allNeeds = json.load(r)
            r.close()
            if self.character.name in allNeeds:
                dlg = QMessageBox()
                dlg.setStyleSheet('background-color: rgb(38, 54, 173); color: white; font-size: 14pt;')
                dlg.setWindowTitle("Character Overwritten")
                dlg.setText("This character already exists on\nthe requirements table.\nOld entries have been overwritten.")
                dlg.exec()
            print(allNeeds.keys())
            allNeeds.update(needs)
            print(allNeeds.keys())
            w = open(resource_path('save/needs.json'), 'w')
            json.dump(allNeeds, w)
            w.close()
        else:
            with open(resource_path('save/needs.json'), 'w') as f:
                json.dump(needs, f)
        self.reloadPlanner()
        self.reset()

    def reset(self):
        self.resetSpins()
        self.needs = {}
        self.totalMats = {}
        for i in ['1000'] + ids:
            self.needButtons[i].hide()
            self.needButtons[i].setAmount(0)

    def validate(self):
        self.edits[1][0].setMinimum(self.edits[0][0].value()) # basic elite minimum
        self.edits[1][2].setMinimum(self.edits[0][2].value()) #skill minimum
        for i in range(2):
            self.edits[i][1].setMaximum(level_limits[self.character.rarity][self.edits[i][0].value()]) #level max
        if self.edits[1][0].value() == self.edits[0][0].value():
            self.edits[1][1].setMinimum(self.edits[0][1].value()) # after level minimum
        else:
            self.edits[1][1].setMinimum(1)
        for i in range(2):
            if self.edits[i][0].value() == 0:
                self.edits[i][2].setMaximum(4)
            else:
                self.edits[i][2].setMaximum(7)
            for a in range(3,9):
                banned = self.edits[i][0].value() != 2 or self.edits[i][2].value() != 7 or self.character.master[a-3][0] == [] if a < 6 \
                         else self.edits[i][0].value() != 2 or self.edits[i][1].value() < mod_unlock[self.character.rarity]\
                         or a - 5 > len(self.character.mods)
                self.edits[i][a].setDisabled(banned)
                if banned: 
                    self.edits[i][a].setValue(0)
                    self.edits[i][a].setStyleSheet('background-color: black; color: black')
                else:
                    self.edits[i][a].setStyleSheet('background-color: rgb(38, 54, 173); color: white')
        for i in range(3,9):
            self.edits[1][i].setMinimum(self.edits[0][i].value())

    def calculateExp(self):
        lstart, lend, estart, eend = self.edits[0][1].value(), self.edits[1][1].value(), self.edits[0][0].value(), self.edits[1][0].value()
        if lstart == lend and estart == eend: return {}
        totals = {}
        while estart < eend:
            needs = np.sum(exps[estart][lstart-1:level_limits[self.character.rarity][estart]],0)
            totals['E{} Lvl{}->{}'.format(estart, lstart, level_limits[self.character.rarity][estart])] = [{
                'id': '1000',
                'count': needs[0]},
                {'id': '4001',
                 'count': needs[1]}
                ]
            estart += 1
            lstart = 1
        if lstart == lend: return totals
        needs = np.sum(exps[eend][lstart-1:lend],0)
        totals['E{} Lvl{}->{}'.format(estart, lstart, lend)] = [{
                'id': '1000',
                'count': needs[0]},
                {'id': '4001',
                 'count': needs[1]}
                ]
        return totals

    def adjustNeeds(self):
        if not hasattr(self, 'prev_start'):
            self.prev_start = [0,1,1,0,0,0,0,0,0]
            self.prev_end =   [0,1,1,0,0,0,0,0,0]
        start = [x.value() for x in self.edits[0]]
        end = [x.value() for x in self.edits[1]]

        #clear/collect exp needs
        totalExp = defaultdict(int)
        keys = list(self.needs.keys())
        for k in keys:
            if k.count('->') > 0:
                need = self.needs.pop(k)
                for req in need:
                    totalExp[req['id']] += req['count']
        newExp = self.calculateExp()
        self.needs.update(newExp)
        totalNewExp = defaultdict(int)
        for v in newExp.values():
            for need in v:
                totalNewExp[need['id']] += need['count']
        expChange = {'4001': totalNewExp['4001'] - totalExp['4001'], '1000': totalNewExp['1000'] - totalExp['1000']}
        

        startDelta = np.subtract(start, self.prev_start)
        endDelta = np.subtract(end, self.prev_end)

        names = ['Elite {}', None, 'Skill Lvl {}', 'S1M{}', 'S2M{}', 'S3M{}', 'Mod{} Stage {}','Mod{} Stage{}','Mod{} Stage{}']
        methods = [lambda x: self.character.getElite(x), None, lambda x: self.character.getSkill(x), lambda x, y: self.character.getSpec(x,y), 
                   lambda x, y: self.character.getSpec(x,y), lambda x,y: self.character.getSpec(x,y), 
                   lambda x,y: self.character.getMod(x,y), lambda x,y: self.character.getMod(x,y), lambda x,y: self.character.getMod(x,y)]
        endChange = []
        startChange = []
        for i in range(9):
            if i == 1: continue
            if endDelta[i] == 1:
                if 2 < i < 6:
                    endChange = (1, copy.deepcopy(methods[i](i-3, end[i])))
                    self.needs[names[i].format(end[i])] = endChange[1]
                elif 6 <= i:
                    endChange = (1, copy.deepcopy(methods[i](i-7, end[i])))
                    subtype = self.character.mods[i-6].type
                    self.needs[names[i].format(subtype, end[i])] = endChange[1]
                else:
                    endChange = (1, copy.deepcopy(methods[i](end[i])))
                    if i == 0: endChange[1].append({'id': '4001', 'count': eliteCosts[self.character.rarity][end[i]]})
                    self.needs[names[i].format(end[i])] = endChange[1]
            elif endDelta[i] == -1:
                if 6 <= i:
                    subtype = self.character.mods[i-6].type
                    endChange = (-1, copy.deepcopy(self.needs.pop(names[i].format(subtype, self.prev_end[i]))))
                else:
                    endChange = (-1, copy.deepcopy(self.needs.pop(names[i].format(self.prev_end[i]))))

            if startDelta[i] == 1:
                if 6 <= i:
                    subtype = self.character.mods[i-6].type
                    startChange = (-1, copy.deepcopy(self.needs.pop(names[i].format(subtype, start[i]))))
                else:
                    startChange = (-1, copy.deepcopy(self.needs.pop(names[i].format(start[i]))))
            elif startDelta[i] == -1:
                if 2 < i < 6:
                    startChange = (1, copy.deepcopy(methods[i](i-3, self.prev_start[i])))
                    self.needs[names[i].format(self.prev_start[i])] = startChange[1]
                elif 6 <= i:
                    startChange = (1, copy.deepcopy(methods[i](i-7, self.prev_start[i])))
                    subtype = self.character.mods[i-6].type
                    self.needs[names[i].format(subtype, self.prev_start[i])] = startChange[1]
                else:
                    startChange = (1, copy.deepcopy(methods[i](self.prev_start[i])))
                    if i == 0: startChange[1].append({'id': '4001', 'count': eliteCosts[self.character.rarity][self.prev_start[i]]})
                    self.needs[names[i].format(self.prev_start[i])] = startChange[1]
        
        for change in [startChange, endChange]:
            if not isinstance(change, tuple): continue
            for need in change[1]:
                need['count'] *= change[0]
        if len(startChange) > 0:
            startChange = startChange[1]
        if len(endChange) > 0:
            endChange = endChange[1]

        totalChange = defaultdict(int)
        for change in [startChange, endChange]:
            if len(change) == 0 or not isinstance(change[0], dict): continue
            for need in change:
                totalChange[need['id']] += need['count']
        totalChange['4001'] += expChange['4001']
        totalChange['1000'] += expChange['1000']

        self.prev_start = start
        self.prev_end = end

        return totalChange

    def resetSpins(self):
        for arr in self.edits:
            for widget in arr:
                widget.blockSignals(True)
        for arr in self.edits:
            for widget in arr:
                widget.setMinimum(0)
                widget.setValue(0)
                widget.setStyleSheet('background-color: black; color: black')

        if self.character is None: return
        rng = range(3) if self.character.rarity < 4 else range(9)
        for i in rng:
            enabled = True
            if 3 >= i >= 5: enabled = i < len(self.character.skillNames)
            elif i >= 6: enabled = i < len(self.character.mods)
            self.edits[0][i].setDisabled(not enabled)
            self.edits[1][i].setDisabled(not enabled)
            if enabled:
                self.edits[0][i].setStyleSheet('background-color: rgb(38, 54, 173); color: white')
                self.edits[1][i].setStyleSheet('background-color: rgb(38, 54, 173); color: white')

        for i in range(2):
            self.edits[i][0].setRange(0, eliteLimits[self.character.rarity])
            self.edits[i][1].setRange(1, level_limits[self.character.rarity][0])
            self.edits[i][2].setRange(1, 7)
            for a in range(3):
                self.edits[i][a+3].setRange(0, 3)
            for a in range(3):
                self.edits[i][a+6].setRange(0, 3)

        for arr in self.edits:
            for widget in arr:
                widget.blockSignals(False)
        
        self.update()

    def checkCharacter(self):
        if self.nameEdit.hasFocus() and len(self.nameEdit.text()) >= 1:
            oldName = self.character.name if self.character is not None else ""
            names = process.extract(self.nameEdit.text(), characters.keys(), limit=5)
            while len(names) > 1:
                if len(names[0][0]) < len(self.nameEdit.text()):
                    names.pop(0)
                else:
                    break
            name = ''
            casefold = self.nameEdit.text().casefold()
            for charname in characters:
                if  casefold == charname.casefold():
                    name = charname
            if name == '':
                if names[0][1] > 50 and names[0][1] > names[1][1]:
                    name = names[0][0]
                else: return
            self.character = characters[name]
            self.guessLabel.setText(characters[name].name)
            self.reset()
            if self.character.name != oldName:
                if not self.preloaded and os.path.isfile(resource_path('save/akImages.pkl')):
                    with open(resource_path('save/akImages.pkl'), mode='rb') as f:
                        self.images = pickle.load(f)
                    self.preloaded = True
                if self.preloaded:
                    self.preloadedCharacter()
                else:
                    self.updateCharacter()

    def updateCharacter(self):
        if self.character is None: return
        keys = [self.character.id, self.character.job, self.character.subjob]
        for name in self.character.skillNames:
            keys.append(name)
        while len(keys) < 6:
            keys.append('')
        for mod in self.character.mods:
            keys.append(mod.icon)
            keys.append(mod.id)
        while len(keys) < 12:
            keys.append('')
        urls = ['https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/avatars/',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/classes/class_',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/ui/subclass/sub_',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/skills/skill_icon_',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/skills/skill_icon_',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/skills/skill_icon_',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/equip/type/',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/equip/icon/',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/equip/type/',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/equip/icon/',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/equip/type/',
                'https://raw.githubusercontent.com/Irvan789/Arknight-Images/refs/heads/main/equip/icon/',]
        widgets = [self.portrait, self.job, self.subjob, self.skills[0], self.skills[1], self.skills[2], self.mods[0][0], self.mods[0][1], self.mods[1][0], self.mods[1][1], self.mods[2][0], self.mods[2][1]]
        sizes = [(240, 240), (120, 120), (80, 80), (120, 120), (120, 120), (120, 120), (80, 80), (120, 120), (80, 80), (120, 120), (80, 80), (120, 120),]
        suffix = ['.png', '.png', '_icon.png', '.png', '.png', '.png', '.png', '.png', '.png', '.png', '.png', '.png',]
        for i in range(len(keys)):
            if keys[i] == '':
                img = QPixmap()
                widgets[i].setPixmap(img)
            else:
                try:
                    data = urllib.request.urlopen(urls[i] + keys[i] + suffix[i]).read()
                    img = QImage()
                    img.loadFromData(data)
                    img = QPixmap(img)
                except:
                    img = QPixmap('img/load_fail.png')
                widgets[i].setPixmap(img.scaled(sizes[i][0], sizes[i][1], transformMode=Qt.SmoothTransformation))
                  
    def preloadedCharacter(self):
        if self.character is None: return
        try:
            imgs = self.images[self.character.name]
        except:
            self.updateCharacter()
            return
        widgets = [self.portrait, self.job, self.subjob, self.skills[0], self.skills[1], self.skills[2], self.mods[0][0], self.mods[0][1], self.mods[1][0], self.mods[1][1]]
        sizes = [(240, 240), (120, 120), (80, 80), (120, 120), (120, 120), (120, 120), (80, 80), (120, 120), (80, 80), (120, 120),]
        for i in range(len(imgs)):
            if imgs[i] is None:
                img = QPixmap()
            elif imgs[i] == 'img/load_fail.png':
                img = QPixmap(resource_path('img/load_fail.png')).scaled(sizes[i][0], sizes[i][1], transformMode=Qt.SmoothTransformation)
            else:
                try:
                    img = QImage()
                    img.loadFromData(imgs[i])
                    img = QPixmap(img)
                except:
                    img = QPixmap(resource_path('img/load_fail.png'))
                img = img.scaled(sizes[i][0], sizes[i][1], transformMode=Qt.SmoothTransformation)
            widgets[i].setPixmap(img)

