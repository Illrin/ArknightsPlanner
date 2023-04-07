from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5 import uic

import sys
import os
import json
from collections import defaultdict
import threading
from math import floor, ceil
import copy

from akparser import loadCharacters
from path import resource_path
loadCharacters()


from depot import Depot, ids, recipies, names
from materialbutton import *
from materialrow import *
from collapsiblebox import CollapsibleBox
from flowlayout import FlowLayout
from opsubmission import OpSubmissionBox
from planner import PlannerPage
from preload import preload
from farming import FarmBox
from predictions import StageBox

class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi(resource_path('gui/main.ui'), self)
        self.setWindowIcon(QtGui.QIcon(resource_path('img/extra/logo-black.png')))

        self.inventory = Depot()
        self.totals = defaultdict(int)
        self.breakdown = defaultdict(int)

        if os.path.isfile(resource_path('save/settings.json')):
            with open(resource_path('save/settings.json')) as f:
                self.settings = json.load(f)
        self.loadingthread = None

        depot = self.createDepot()
        settings = self.createSettings()
        planner = self.createPlanner()
        sub = self.createSubmissions()
        farming = self.createFarming()
        predicting = self.createPrediction()

        self.stack = QStackedWidget(self)
        self.stack.addWidget(depot)
        self.stack.addWidget(sub)
        self.stack.addWidget(planner)
        self.stack.addWidget(farming)
        self.stack.addWidget(predicting)
        self.stack.addWidget(settings)

        self.setCentralWidget(self.stack)

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        depot_action = QAction("Depot", self)
        depot_action.triggered.connect(lambda: self.changeMenu(0))
        toolbar.addAction(depot_action)
        sub_action = QAction("Operator Submission", self)
        sub_action.triggered.connect(lambda: self.changeMenu(1))
        toolbar.addAction(sub_action)
        plan_action = QAction("Planner", self)
        plan_action.triggered.connect(lambda: self.changeMenu(2))
        toolbar.addAction(plan_action)
        farm_action = QAction("Farming", self)
        farm_action.triggered.connect(lambda: self.changeMenu(3))
        toolbar.addAction(farm_action)
        predict_action = QAction("Stage Predictions", self)
        predict_action.triggered.connect(lambda: self.changeMenu(4))
        toolbar.addAction(predict_action)
        setting_action = QAction("Settings", self)
        setting_action.triggered.connect(lambda: self.changeMenu(5))
        toolbar.addAction(setting_action)

    def createDepot(self):
        self.depotScroll = QScrollArea(self)
        self.depotScroll.setAlignment(Qt.AlignTop)
        self.depotScroll.setWidgetResizable(True)

        depotLayout = QVBoxLayout()
        depotLayout.setContentsMargins(0,0,0,0)
        depotLayout.setSpacing(0)

        self.depotGridGroup = QGroupBox(self.depotScroll)
        self.depotGridGroup.setFlat(True)
        self.depotGridGroup.setStyleSheet('background-color: rgb(38, 54, 173);')
        self.depotGridGroup.setContentsMargins(0,0,0,0)
        gridDepotLayout = FlowLayout(self.depotGridGroup)
        gridDepotLayout.setAlignment(Qt.AlignTop)
        gridDepotLayout.setContentsMargins(0, 0, 0, 0)
        gridDepotLayout.setSpacing(0)

        self.mats = defaultdict(list)
        for id in ids:
            button = MaterialRow(self, id, self.inventory.get_item(id), lambda a=id:self.increment(a), lambda a=id:self.decrement(a), 
                                    lambda x, a=id: self.set(a, x), 150, 150, self.craftItem)
            gridDepotLayout.addWidget(button)
            self.mats[id].append(button)
        self.depotGridGroup.setLayout(gridDepotLayout)

        depotLayout.addWidget(self.depotGridGroup)

        self.depotGroupGroup = QGroupBox(self.depotScroll)
        self.depotGroupGroup.setFlat(True)
        self.depotGroupGroup.setStyleSheet('background-color: rgb(38, 54, 173);')
        self.depotGroupGroup.setContentsMargins(0,0,0,0)

        groupDepotLayout = QHBoxLayout()
        groupDepotLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        groupDepotLayout.setContentsMargins(0,0,0,0)
        groupDepotLayout.setSpacing(0)

        ends = [0, 2, 6, 9, 12, 17, 37, 61, 86]
        titles = ["Currencies", "Battle Records", "Skill Summaries", "Modules",
                  "Tier 5", "T4/T3 Pairs", "T4-T1 Sets", "Chips"]
        groups = [1, 1, 1, 1, 1, 4, 4, 8]

        for i in range(len(ends)-1):
            box = QGroupBox(self)
            box.setFlat(True)
            collapseLayout = QVBoxLayout()
            collapseLayout.setAlignment(Qt.AlignTop)
            label = QLabel(titles[i])
            label.setStyleSheet('color: white; font-size: 18pt')
            collapseLayout.addWidget(label)
            a = ends[i]
            while a < ends[i+1]:
                row = QHBoxLayout()
                row.setAlignment(Qt.AlignTop)
                b = 0
                while b < groups[i]:
                    if a >= ends[i+1]: break
                    id = ids[a]
                    button = MaterialRow(self, id, self.inventory.get_item(id), lambda a=id:self.increment(a), lambda a=id:self.decrement(a), 
                                    lambda x, a=id: self.set(a, x), 150, 150, self.craftItem)
                    row.addWidget(button)
                    self.mats[id].append(button)
                    a += 1
                    b += 1
                    if a == 62:
                        button.setFixedWidth(302)
                        collapseLayout.addLayout(row)
                        row = QHBoxLayout()
                        row.setAlignment(Qt.AlignTop)
                        b -= 1
                collapseLayout.addLayout(row)
            box.setLayout(collapseLayout)
            groupDepotLayout.addWidget(box)

        self.depotGroupGroup.setLayout(groupDepotLayout)

        self.depotGroupGroup.hide()
        depotLayout.addWidget(self.depotGroupGroup)

        depot = QGroupBox(self.depotScroll)
        depot.setLayout(depotLayout)
        depot.setFlat(True)
        self.depotScroll.setWidget(depot)

        self.resetTotals()
        self.resetBreakdown()
        self.refreshInventory()

        return self.depotScroll
        
    def createSubmissions(self):
        self.submissionScroll = QScrollArea(self)
        self.submissionScroll.setAlignment(Qt.AlignTop)
        self.submissionScroll.setWidgetResizable(True)

        submission = OpSubmissionBox(self.submissionScroll,  self.planner.refreshNeeds)
        self.submissionScroll.setWidget(submission)

        return self.submissionScroll

    def createPlanner(self):
        self.plannerScroll = QScrollArea(self)
        self.plannerScroll.setAlignment(Qt.AlignTop)
        self.plannerScroll.setWidgetResizable(True)

        self.planner = PlannerPage(self.plannerScroll, self.submitNeed)
        self.plannerScroll.setWidget(self.planner)
        self.planner.refreshInventory(self.inventory.depot, True)
        return self.plannerScroll

    def createFarming(self):
        self.farmScroll = QScrollArea(self)
        self.farmScroll.setAlignment(Qt.AlignTop)
        self.farmScroll.setWidgetResizable(True)

        self.farm = FarmBox(self.farmScroll, self.increment, self.decrement, self.inventory.get_item)
        self.farmScroll.setWidget(self.farm)
        return self.farmScroll

    def createPrediction(self):
        self.predictScroll = QScrollArea(self)
        self.predictScroll.setAlignment(Qt.AlignTop)
        self.predictScroll.setWidgetResizable(True)

        self.predict = StageBox(self.predictScroll, self.getDepot, self.getTotals)
        self.predictScroll.setWidget(self.predict)
        return self.predictScroll

    def createSettings(self):
        self.settingScroll = QScrollArea(self)
        self.settingScroll.setAlignment(Qt.AlignTop)
        self.settingScroll.setWidgetResizable(True)
        self.settingScroll.setStyleSheet('font-size: 14pt;background-color: rgb(38, 54, 173);color: white')

        settings = QVBoxLayout()
        settings.setAlignment(Qt.AlignTop)
        settings.setContentsMargins(0,0,0,0)

        label = QLabel("Depot Display Style:")

        self.grid = QRadioButton("Grid")
        self.grid.pressed.connect(lambda: self.swapDepot(0))
        self.group = QRadioButton("Group")
        self.group.pressed.connect(lambda: self.swapDepot(1))

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignLeft)
        buttons.addWidget(label)
        buttons.addWidget(self.grid)
        buttons.addWidget(self.group)

        settings.addLayout(buttons)

        self.popup = QCheckBox("Show Crafting Recipe on Hover")
        self.popup.toggled.connect(lambda x=self.popup.isChecked(): self.setPopup(x))
        settings.addWidget(self.popup)

        self.failedCraft = QCheckBox("Create Dialogue on Failed Craft")
        self.failedCraft.toggled.connect(lambda x=self.failedCraft.isChecked(): self.setFail(x))
        settings.addWidget(self.failedCraft)

        self.preload = QPushButton("Download all Character Images")
        self.preload.setFixedWidth(500)
        self.preload.pressed.connect(lambda: self.loadWatcher())
        settings.addWidget(self.preload)

        if hasattr(self, 'settings'):
            self.grid.setChecked(self.settings['grid'])
            self.group.setChecked(self.settings['group'])
            if self.settings['grid']: self.swapDepot(0)
            if self.settings['group']: self.swapDepot(1)
            self.popup.setChecked(self.settings['hover'])
            self.failedCraft.setChecked(self.settings['fail'])
            self.setPopup(self.settings['hover'])
            self.doFail = self.settings['fail']
        else:
            self.grid.setChecked(True)
            self.doHover = True
            self.popup.setChecked(True)
            self.failedCraft.setChecked(True)

        self.settingScroll.setLayout(settings)
        return self.settingScroll
    
    def changeMenu(self, screen):
        self.stack.setCurrentIndex(screen)
        if screen == 0: 
            self.resetTotals()
            self.resetBreakdown()
            self.refreshInventory()
        elif screen == 2: self.planner.refreshInventory(self.inventory.depot)

    def submitNeed(self, need):
        for k, v in need.items():
            self.inventory.reduce_item(k, v)
        self.planner.refreshInventory(self.inventory.depot)

    def setFail(self, fail):
        self.doFail = fail

    def setPopup(self, pop):
        for id in self.mats:
            for button in self.mats[id]:
                button.setDisplay(pop)

    def resetTotals(self):
        self.totals = defaultdict(int)
        if not os.path.isfile('save/needs.json'): return
        with open('save/needs.json') as f:
            needs = json.load(f)
        for op in needs.values():
            for k, v in op.items():
                if k == 'id': continue
                for id, amnt in v.items():
                    self.totals[id] += amnt
        if "1000" in self.totals:
            self.totals["2004"] = floor(self.totals["1000"] / 2000)
            remain = self.totals["1000"] % 2000
            self.totals["2003"] = floor(remain / 1000)
            remain %= 1000
            self.totals["2002"] = floor(remain / 400)
            remain %= 400
            self.totals["2001"] = ceil(remain / 200)

    def getTotals(self):
        self.resetTotals()
        return self.totals
    
    def resetBreakdown(self):
        toBreakdown = copy.deepcopy(self.totals)
        if '1000' in toBreakdown: toBreakdown.pop('1000')
        depot = copy.deepcopy(self.inventory.depot)
        self.breakdown = defaultdict(int)
        while len(toBreakdown.keys()) > 0:
            item, amnt = toBreakdown.popitem()
            if depot[item] >= amnt:
                depot[item] -= amnt
                amnt = 0
            else:
                amnt -= depot[item]
                depot[item] = 0
            if item in recipies:
                for k,v in recipies[item].items():
                    toBreakdown[k] += v * amnt
            self.breakdown[item] += amnt


    def increment(self, id):
        amnt = self.inventory.increment(id)
        if self.stack.currentIndex() == 0:
            self.resetTotals()
            self.resetBreakdown()
            self.setNeeds(id)
        return amnt

    def decrement(self, id):
        amnt = self.inventory.decrement(id)
        if self.stack.currentIndex() == 0:
            self.resetTotals()
            self.resetBreakdown()
            self.setNeeds(id)
        return amnt
    
    def set(self, id, amnt):
        self.inventory.set_item(id, amnt)
        if self.stack.currentIndex() == 0:
            self.resetTotals()
            self.resetBreakdown()
            self.setNeeds(id)

    def getDepot(self):
        return self.inventory.depot

    def setNeeds(self, id):
        buttons = self.mats[id]
        for button in buttons:
            need = max(self.totals[id] - self.inventory.get_item(id),0)
            button.setNeeds(need)
            craft = self.breakdown[id]
            button.setCrafts(craft)
        if id not in recipies: return
        for k in recipies[id]:
            self.setNeeds(k)

    def loadWatcher(self):
        if self.loadingthread is not None and self.loadingthread.is_alive(): 
            dlg = QMessageBox()
            dlg.setWindowTitle("Arknights Planner")
            dlg.setText("Image Download Currently in Progress")
            dlg.exec()
            return
        self.loadingthread = threading.Thread(target=self.loadImages)
        self.loadingthread.daemon = True
        self.loadingthread.start()
        dlg = QMessageBox()
        dlg.setWindowTitle("Arknights Planner")
        dlg.setText("Image Download Started.\nThis will take a few minutes.\nThere will be no notification when finished.")
        dlg.exec()

    def loadImages(self):
        preload()
    
    def swapDepot(self, type:int):
        if type == 0:
            self.depotGroupGroup.hide()
            self.depotGridGroup.show()
        elif type == 1:
            self.depotGroupGroup.show()
            self.depotGridGroup.hide()

    def refreshInventory(self):
        for id in self.mats:
            for button in self.mats[id]:
                button.setAmount(self.inventory.get_item(id))
            self.setNeeds(id)

    def craftItem(self, id):
        craftable = self.inventory.self_craft(id, False, True)
        if isinstance(craftable, bool) and craftable:
            self.inventory.self_craft(id)
            for button in self.mats[id]:
                    button.setAmount(self.inventory.get_item(id))
            for base in recipies[id]:
                for button in self.mats[base]:
                    button.setAmount(self.inventory.get_item(base))
        elif self.doFail:
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Lacking Materials")
            dlg.setStyleSheet('background-color: rgb(38, 54, 173); color: white; font-size: 14pt;')
            msg = ""
            for missing in craftable:
                msg += names[missing[0]] + ": " + str(missing[1]) + "\n"
            dlg.setText("Missing the following materials:\n" + msg[:-1])
            dlg.exec()

    def start(self):
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    window.start()
    app.exec_()
    window.inventory.save()
    settings = {'grid':window.grid.isChecked(),
                'group':window.group.isChecked(),
                'hover':window.popup.isChecked(),
                'fail':window.failedCraft.isChecked(),
                }
    with open(resource_path('save/settings.json'), 'w') as f:
        json.dump(settings, f)
    if window.loadingthread is not None:
        if window.loadingthread.is_alive():
            dlg = QMessageBox()
            dlg.setWindowTitle("Arknights Planner")
            dlg.setText("Canceling download...")
            dlg.exec()
            sys.exit()
        window.loadingthread.join()