# importing libraries
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtGui import *
from depotGui import *
from inventory import *
from needsGui import *
import sys
from operatorGui import OperatorTable
from farmingGui import FarmingGroup
from stagesGui import StageGroup
from math import floor, ceil

reverse_ids = {v.lower(): k for k,v in names.items()}


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        # setting title
        self.setWindowTitle("Arknights Planner")

        self.width = 960
        self.height = 480
        # setting geometry
        self.setFixedSize(self.width, self.height)
        self.setWindowIcon(QIcon("Images/logo-black.ico"))

        self.rows = {}
        self.inventory = Depot()
        self.needs = {}
        try:
            f = io.open("Data/requirements.json")
            self.needs = json.load(f)
        except OSError:
            pass
        self.totals = {}
        self.breakdown = {}
        self.isFiltered = False

        self.StageComponents()
        self.DepotComponents()
        self.updateTotals()
        self.OperatorComponents()
        self.RequirementsComponents()
        self.FarmingComponents()

        self.Sounds()

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)
        depot_action = QAction("Depot", self)
        depot_action.triggered.connect(lambda: self.showScreen(0))
        toolbar.addAction(depot_action)
        operator_action = QAction("Operator Submissions", self)
        operator_action.triggered.connect(lambda: self.showScreen(1))
        toolbar.addAction(operator_action)
        requirements_action = QAction("Planner", self)
        requirements_action.triggered.connect(lambda: self.showScreen(2))
        toolbar.addAction(requirements_action)
        farming_action = QAction("Stage Farming", self)
        farming_action.triggered.connect(lambda: self.showScreen(3))
        toolbar.addAction(farming_action)
        stage_action = QAction("Farming Predictions", self)
        stage_action.triggered.connect(lambda: self.showScreen(4))
        toolbar.addAction(stage_action)
        export_action = QAction("Penguin Stats Export", self)
        export_action.triggered.connect(self.buildExport)
        toolbar.addAction(export_action)

        toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

        self.setStyleSheet("""
        QScrollBar:vertical {
            border: none;
            background: rgb(45, 45, 68);
            width: 22px;
            margin: 15px 0 15px 0;
            border-radius: 0px;
         }
        
        /*  HANDLE BAR VERTICAL */
        QScrollBar::handle:vertical {	
            background-color: rgb(80, 80, 122);
            min-height: 30px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical:hover{	
            background-color: rgb(255, 0, 147);
        }
        QScrollBar::handle:vertical:pressed {	
            background-color: rgb(185, 0, 112);
        }
        
        /* BTN TOP - SCROLLBAR */
        QScrollBar::sub-line:vertical {
            border: none;
            background-color: rgb(59, 59, 120);
            height: 15px;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar::sub-line:vertical:hover {	
            background-color: rgb(255, 0, 147);
        }
        QScrollBar::sub-line:vertical:pressed {	
            background-color: rgb(185, 0, 112);
        }
        
        /* BTN BOTTOM - SCROLLBAR */
        QScrollBar::add-line:vertical {
            border: none;
            background-color: rgb(59, 59, 90);
            height: 15px;
            border-bottom-left-radius: 7px;
            border-bottom-right-radius: 7px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        QScrollBar::add-line:vertical:hover {	
            background-color: rgb(255, 0, 127);
        }
        QScrollBar::add-line:vertical:pressed {	
            background-color: rgb(185, 0, 92);
        }
        
        /* RESET ARROW */
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background-color: rgb(59, 59, 90);
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background-color: rgb(59, 59, 90);
        }
        """)

        self.show()

    # method for components
    def DepotComponents(self):
        self.depotGroup = QGroupBox(self)
        self.depotGroup.setGeometry(0, 25, self.width, self.height)
        self.depotGroup.setFixedSize(self.width, self.height - 25)
        depotLayout = QVBoxLayout()
        depotLayout.setContentsMargins(0, 0, 0, 0)
        depotLayout.setSpacing(0)
        self.filterLayout = QHBoxLayout()
        filterLabel = QLabel("Filter Material/Craft")
        breakdownBox = QCheckBox()
        breakdownLabel = QLabel("Show Full Craft Tree Mats")
        breakdownLabel.setAlignment(Qt.AlignRight)
        filterLabel.setFixedSize(200, 20)
        filterEdit = QLineEdit()
        filterEdit.textChanged.connect(lambda: self.filterDepot(filterEdit.text(), breakdownBox.isChecked()))
        breakdownBox.stateChanged.connect(lambda: self.filterDepot(filterEdit.text(), breakdownBox.isChecked()))
        filterEdit.setStyleSheet("background-color: rgb(200, 200, 200);")
        filterEdit.setFixedSize(200, 20)

        self.filterLayout.addWidget(filterLabel)
        self.filterLayout.addWidget(filterEdit)
        self.filterLayout.addWidget(breakdownLabel)
        self.filterLayout.addWidget(breakdownBox)
        depotLayout.addLayout(self.filterLayout)

        self.depot = QScrollArea(self)
        self.depot.setAlignment(Qt.AlignTop)
        self.depot.setWidgetResizable(True)
        self.depot.setGeometry(0, 55, self.width, self.height)
        self.depot.setFixedWidth(self.width)#, self.height-55)
        self.depot.horizontalScrollBar().setEnabled(False)
        self.depot.setStyleSheet("""background-image: url(Images/backgrounds/bg_bridge.png) 0 0 0 0 stretch stretch;
                           background-attachment: fixed;
                           background-repeat: none;
                           """)
        depotLayout.addWidget(self.depot)
        self.depotGroup.setLayout(depotLayout)

        self.buildDepot()

    def buildDepot(self, filter=None):
        depot = QGroupBox(self.depot)
        depot.setMinimumSize(800, self.height)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        ends = [0, 2, 6, 9, 12, 17, 37, 61, 87]
        titles = ["Currencies", "Battle Records", "Skill Summaries", "Modules",
                  "Tier 5", "T4/T3 Pairs", "T4-T1 Sets", "Chips"]
        images = ["1001", "2004", "3303", "4003", "30135", "30074", "30064", "3000"]
        self.boxes = []
        for a in range(5):
            box = CollapsibleBox(self, "", 0, 800, 100)
            box.toggle_button.setText(titles[a])
            image = QPixmap("Images/materials/" + images[a] + ".png")
            image = image.scaled(100, 100, transformMode=QtCore.Qt.SmoothTransformation)
            box.avatarLabel.setPixmap(image)
            box.setStyleSheet("background-color: rgb(74, 158, 181);")
            collapseLayout = QVBoxLayout()
            collapseLayout.setAlignment(Qt.AlignTop)
            i = 0
            for id in ids[ends[a]:ends[a + 1]]:
                row = MaterialRow(depot, id, self.inventory.depot[id], 400, 100, self.totals.get(id, 0),
                                  self.breakdown.get(id, 0))
                row.setStyleSheet("background-color: rgb(74, 158, 181);")
                self.rows[id] = row
                if filter is not None and id not in filter:
                    row.hide()
                    continue
                collapseLayout.addWidget(row)
                collapseLayout.addStretch()
                i += 1
            if i > 0:
                box.setContentLayout(collapseLayout)
                self.boxes.append(box)
                layout.addWidget(box)

        for a in range(5, 8):
            box = CollapsibleBox(self, "", 0, 800, 100)
            box.toggle_button.setText(titles[a])
            image = QPixmap("Images/materials/" + images[a] + ".png")
            image = image.scaled(100, 100, transformMode=QtCore.Qt.SmoothTransformation)
            box.avatarLabel.setPixmap(image)
            box.setStyleSheet("background-color: rgb(74, 158, 181);")
            collapseLayout = QGridLayout()
            collapseLayout.setAlignment(Qt.AlignTop)
            i = 0
            for id in ids[ends[a]:ends[a + 1]]:
                row = MaterialRow(depot, id, self.inventory.depot[id], 400, 100, self.totals.get(id, 0),
                                  self.breakdown.get(id, 0))
                row.setStyleSheet("background-color: rgb(74, 158, 181);")
                self.rows[id] = row
                if filter is not None and id not in filter:
                    row.hide()
                    continue
                if id == "3000":
                    collapseLayout.addWidget(row, 0, 0, 1, 2)
                    i += 1
                else:
                    collapseLayout.addWidget(row, int(i / 2), i % 2)
                i += 1
            if i > 0:
                box.setContentLayout(collapseLayout)
                layout.addWidget(box)
                self.boxes.append(box)

        depot.setLayout(layout)
        depot.setStyleSheet("background: transparent")
        self.depot.setWidget(depot)

    def OperatorComponents(self):
        self.operator = QScrollArea(self)
        self.operator.setGeometry(0, 25, self.width, self.height)
        self.operator.setFixedSize(self.width, self.height - 25)
        self.operator.horizontalScrollBar().setEnabled(False)
        self.operator.setStyleSheet("""background-image: url(Images/backgrounds/bg_bridge.png) 0 0 0 0 stretch stretch;
                                   background-attachment: fixed;
                                   background-repeat: none;
                                   """)
        opTable = QGroupBox(self.operator)
        opTable.setMinimumSize(self.width-160, 260)
        opTable.setStyleSheet("background: transparent;"
                              "background-color: rgb(74, 158, 181);"
                              "border: 1px solid black")
        ops = OperatorTable(self, opTable, self.needs)
        opTable.setLayout(ops)
        self.operator.setWidget(opTable)

        self.operator.hide()

    def RequirementsComponents(self):
        self.requirements = QScrollArea(self)
        self.requirements.setGeometry(0, 25, self.width, self.height-25)
        self.requirements.setWidgetResizable(True)
        self.requirements.horizontalScrollBar().setEnabled(False)
        self.requirements.setStyleSheet("""background-image: url(Images/backgrounds/bg_bridge.png) 0 0 0 0 stretch stretch;
                                           background-attachment: fixed;
                                           background-repeat: none;
                                           """)
        self.rebuildNeeds()
        self.requirements.hide()

    def FarmingComponents(self):
        self.farming = QScrollArea(self)
        self.farming.setGeometry(0, 25, self.width, self.height - 25)
        self.farming.setWidgetResizable(True)
        self.farming.horizontalScrollBar().setEnabled(False)
        self.farming.setStyleSheet("""background-image: url(Images/backgrounds/bg_bridge.png) 0 0 0 0 stretch stretch;
                                                   background-attachment: fixed;
                                                   background-repeat: none;
                                                   """)
        self.farm = FarmingGroup(self, 800, self.height, self.inventory.depot)
        self.farm.setStyleSheet("background: transparent;"
                              "background-color: rgb(74, 158, 181);"
                              "border: 1px solid black")
        self.farming.setWidget(self.farm)
        self.farming.hide()

    def StageComponents(self):
        self.stages = QScrollArea(self)
        self.stages.setGeometry(0, 25, self.width, self.height - 25)
        self.stages.setWidgetResizable(True)
        self.stages.horizontalScrollBar().setEnabled(False)
        self.stages.setStyleSheet("""background-image: url(Images/backgrounds/bg_bridge.png) 0 0 0 0 stretch stretch;
                                                           background-attachment: fixed;
                                                           background-repeat: none;
                                                           """)
        self.stage = StageGroup(self, 800, self.inventory.depot, self.totals)
        self.stage.setStyleSheet("background: transparent;"
                                "background-color: rgb(74, 158, 181);"
                                "border: 1px solid black")
        self.stages.setWidget(self.stage)
        self.stages.hide()

    def showScreen(self, screen):
        self.depotGroup.hide()
        self.operator.hide()
        self.requirements.hide()
        self.farming.hide()
        self.stages.hide()

        if screen == 0: self.updateMaterials()
        self.updateTotals()
        if screen == 2: self.resetNeeds()
        if screen == 3: self.farm.update_vals()
        [self.depotGroup, self.operator, self.requirements, self.farming, self.stages][screen].show()

    def resetNeeds(self):
        for names in self.needRows:
            for need in self.needRows[names].values():
                if isinstance(need, NeedsRow):
                    need.reset_amounts()

    def rebuildNeeds(self):
        requirements = QGroupBox(self.depot)
        requirements.setMinimumSize(800, self.height)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        self.needRows = {}
        for name in self.needs:
            row = CollapsibleBox(self, name, 0, 800, 100)
            row.setStyleSheet("background-color: rgb(74, 158, 181);")
            self.needRows[name] = {"header":row}
            rowLayout = QVBoxLayout()
            for title, mats in self.needs[name].items():
                matRow = NeedsRow(self, mats, title, 800, 100, self.inventory, name)
                matRow.setStyleSheet("background-color: rgb(74, 158, 181);"
                                     "border: 1px solid black")
                rowLayout.addWidget(matRow)
                self.needRows[name][title] = matRow
            row.setContentLayout(rowLayout)
            layout.addWidget(row)

        requirements.setLayout(layout)
        requirements.setStyleSheet("background: transparent")
        self.requirements.setWidget(requirements)

    def Sounds(self):
        fail = QSoundEffect()
        fail.setSource(QUrl.fromLocalFile("Sounds/alarm.wav"))
        self.effects = {
            'fail': fail
        }
        for e in self.effects:
            self.effects[e].setVolume(.5)

    def updateTotals(self):
        self.totals = {}
        for need in self.needs.values():
            for mats in need.values():
                for k, v in mats.items():
                    if k in self.totals:
                        self.totals[k] += v
                    else:
                        self.totals[k] = v
        self.stage.required = self.totals
        self.stage.owned = self.inventory.depot
        if "1000" in self.totals:
            self.totals["2004"] = floor(self.totals["1000"] / 2000)
            remain = self.totals["1000"] % 2000
            self.totals["2003"] = floor(remain / 1000)
            remain %= 1000
            self.totals["2002"] = floor(remain / 400)
            remain %= 400
            self.totals["2001"] = ceil(remain / 200)
        self.breakdown = {}
        toBreakdown = copy.deepcopy(self.totals)
        for i in self.inventory.depot:
            if i not in toBreakdown:
                toBreakdown[i] = -self.inventory.depot[i]
            else:
                toBreakdown[i] -= self.inventory.depot[i]
        while len(toBreakdown.keys()) > 0:
            item, amnt = toBreakdown.popitem()
            if item in recipes:
                for k,v in recipes[item].items():
                    if k in toBreakdown:
                        toBreakdown[k] += v * amnt
                    else:
                        toBreakdown[k] = v * amnt
            if item in self.breakdown:
                self.breakdown[item] += amnt
            else:
                self.breakdown[item] = amnt
        self.refreshNeeds()

    def buildExport(self):
        msg = '{"@type":"@penguin-statistics/planner/config","items":['
        for i in ids[12:62]:
            msg += '{"id":"' + i + '","have":' + str(self.inventory.depot[i]) + ',"need":' + str(self.totals.get(i, 0)) + '},'
        msg = msg[:-1]
        msg += '],"options":{"byProduct":true,"requireExp":false,"requireLmb":false},"excludes":[]}'
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(msg, mode=cb.Clipboard)
        msgBox = QMessageBox()
        msgBox.setText("Export Copied to Clipboard.")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Arknights Planner")
        msgBox.setWindowIcon(QIcon("Images/logo-black.ico"))
        a = msgBox.exec()

    def setMaterialAmount(self, id, amnt):
        self.inventory.depot[id] = amnt
        self.updateTotals()

    def craftMaterial(self, id, source):
        if self.inventory.craft(self.inventory.depot, id, False, True):
            self.inventory.craft(self.inventory.depot, id)
            source.set_amount(self.inventory.depot[id], id)
            for base in recipes[id]:
                self.rows[base].set_amount(self.inventory.depot[base], base)
            self.updateTotals()
        else:
            self.effects['fail'].play()

    def updateMaterials(self):
        tickets = {"2004": 2000, "2003": 1000, "2002": 400, "2001": 200}
        self.inventory.depot["1000"] = 0
        for id in ids:
            self.rows[id].set_amount(self.inventory.depot[id], id)
            if id in tickets.keys():
                self.inventory.depot["1000"] += tickets[id] * self.inventory.depot[id]

    def removeNeed(self, title, name):
        v = self.requirements.verticalScrollBar().value()
        self.needs[name].pop(title)
        if len(self.needs[name]) == 0:
            self.needs.pop(name)
        self.rebuildNeeds()
        self.needRows[name]["header"].on_pressed()

    def refreshNeeds(self, ids = None):
        if ids is None: ids = self.rows
        for row in ids:
            self.rows[row].updateTotals(self.totals.get(row,0), self.breakdown.get(row,0))

    def filterDepot(self, name: str, breakdown = False):
        id = reverse_ids.get(name.lower(), None)
        if id is None:
            if self.isFiltered:
                self.isFiltered = False
                self.buildDepot()
            return
        self.isFiltered = True
        toAdd = set()
        toAdd.add(id)
        added = set()
        while len(toAdd) > 0:
            id = toAdd.pop()
            for i in recipes.get(id, []):
                if breakdown: toAdd.add(i)
                added.add(i)
            added.add(id)
        self.buildDepot(added)


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
App.exec()
window.inventory.save_depot()
f = io.open("Data/requirements.json", 'w')
json.dump(window.needs, f)
f.close()
sys.exit()
