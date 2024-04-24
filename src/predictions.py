from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from flowlayout import FlowLayout

from penguin import getPlanner
from depot import ids, names
from materialbutton import MaterialButton

reverse_names = {v:k for k,v in names.items()}

class StageBox(QGroupBox):
    def __init__(self, parent, depot, totals, **kwargs):
        super(StageBox, self).__init__(parent, **kwargs)
        self.depot = depot
        self.totals = totals

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setStyleSheet('background-color: rgb(38, 54, 173); color: white; font-size: 14pt; border: 1px solid white')

        headerLayout = QGridLayout()
        headerLayout.setAlignment(Qt.AlignLeft)
        cnButton = QPushButton(self)
        cnButton.pressed.connect(lambda: self.setPredictions("CN"))
        cnButton.setText("Calculate (CN)")
        enButton = QPushButton(self)
        enButton.setText("Calculate (EN)")
        enButton.pressed.connect(lambda: self.setPredictions("US"))
        headerLayout.addWidget(cnButton, 0, 1)
        headerLayout.addWidget(enButton, 0, 2)
        headerLayout.addWidget(QLabel("Powered by Penguin Statistics"), 1, 0)
        headerLayout.addWidget(QLabel("Uses stages not in EN"))
        headerLayout.addWidget(QLabel("Not up to date with EN side stories"))
        self.mainLayout.addLayout(headerLayout)

        self.bodyLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.bodyLayout)

        self.setLayout(self.mainLayout)

    def setPredictions(self, server):
        owned = self.depot()
        required = self.totals()

        clearLayout(self.bodyLayout)

        owned = {x:owned[x] for x in owned.keys() if x in ids[12:61]}
        required = {x:required[x] for x in required.keys() if x in ids[12:61]}

        needsMoney = '4001' in self.totals()
        needsExp = '2001' in self.totals()
        
        response = getPlanner(owned, required, server, needsMoney, needsExp)
        if 'error' in response:
            errorLabel = QLabel("An Error Occurred. Please try again later.")
            self.bodyLayout.addWidget(errorLabel)
            return
        topLabel = QLabel("Expected Sanity: " + str(response["cost"]) + "\tExpected Costs: " + str(response["gcost"]) +
                        "\tExpected Income: " + str(response['gold']))
        self.bodyLayout.addWidget(topLabel)
        tableLayout = QHBoxLayout()
        nameLabel = QLabel("Stage")
        nameLabel.setFixedWidth(100)
        tableLayout.addWidget(nameLabel)
        countLabel = QLabel("# of Runs")
        countLabel.setFixedWidth(200)
        tableLayout.addWidget(countLabel)
        itemLabel = QLabel("Expected Drops")
        tableLayout.addWidget(itemLabel)
        self.bodyLayout.addLayout(tableLayout)
        for stage in response['stages']:
            stageLayout = QHBoxLayout()
            stageLayout.setAlignment(Qt.AlignLeft)
            codeLabel = QLabel(stage['stage'])
            codeLabel.setFixedWidth(100)
            stageLayout.addWidget(codeLabel)
            countLabel = QLabel(stage['count'])
            countLabel.setFixedWidth(200)
            stageLayout.addWidget(countLabel)

            dropsBox = QGroupBox()
            dropsLayout = FlowLayout(None, 0,0,0)
            i = 0
            for item, count in stage['items'].items():
                if item not in reverse_names: continue
                i += 1
                count = float(count)
                button = MaterialButton(None, reverse_names[item], count, None, None, None, 100, 100, True, True)
                dropsLayout.addWidget(button)
            dropsBox.setFlat(True)
            dropsBox.setLayout(dropsLayout)
            dropsBox.setMinimumWidth(i * 102 + 3)
            stageLayout.addWidget(dropsBox)
            self.bodyLayout.addLayout(stageLayout)


def clearLayout(layout: QLayout):
  while layout.count():
    child = layout.takeAt(0)
    if child.widget():
      child.widget().deleteLater()
    elif child.layout():
       clearLayout(child.layout())