from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from apiInteraction import getPlanner
from inventory import ids, names
from depotGui import MaterialButton

reverse_ids = {v:k for k,v in names.items()}

class StageGroup(QGroupBox):
    def __init__(self, parent, width: int, has, needs, **kwargs):
        super(StageGroup, self).__init__(parent, **kwargs)
        self.setFixedWidth(width)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.owned = has
        self.required = needs

        headerLayout = QGridLayout()
        headerLayout.setAlignment(Qt.AlignLeft)
        cnButton = QPushButton(self)
        cnButton.pressed.connect(lambda: self.setPredictions("CN"))
        cnButton.setText("Calculate (CN)")
        cnButton.setFont(QFont("Sans Serif", 12))
        enButton = QPushButton(self)
        enButton.setText("Calculate (EN)")
        enButton.setFont(QFont("Sans Serif", 12))
        enButton.pressed.connect(lambda: self.setPredictions("US"))
        headerLayout.addWidget(cnButton, 0, 1)
        headerLayout.addWidget(enButton, 0, 2)
        headerLayout.addWidget(QLabel("Powered by Penguin Statistics (https://penguin-stats.io/)"), 1, 0)
        headerLayout.addWidget(QLabel("Considers stages not in EN"))
        headerLayout.addWidget(QLabel("Not up to date with EN side story availability"))
        self.mainLayout.addLayout(headerLayout)

        self.setLayout(self.mainLayout)

    def setPredictions(self, server):
        for i in reversed(range(1, self.mainLayout.count())):
            wid = self.mainLayout.itemAt(i).widget()
            if wid is None:
                wid = self.mainLayout.itemAt(i).layout()
            if wid is not None:
                wid.setParent(None)
                del wid
        owned = {names[x]:self.owned[x] for x in self.owned.keys() if x in ids[12:61] and
                 x not in ["30155", "31064", "31063"]}
        required = {names[x]:self.required[x] for x in self.required.keys() if x in ids[12:61] and
                 x not in ["30155", "31064", "31063"]}
        response = getPlanner(owned, required, server)
        if 'error' in response:
            errorLabel = QLabel("An Error Occurred. Please try again later.")
            errorLabel.setFont(QFont("Sans Serif", 14))
            self.mainLayout.addWidget(errorLabel)
        topLabel = QLabel("Expected Sanity: " + str(response["cost"]) + "\tExpected Costs: " + str(response["gcost"]) +
                          "\tExpected Income: " + str(response['gold']))
        self.mainLayout.addWidget(topLabel)
        tableLayout = QHBoxLayout(self)
        nameLabel = QLabel("Stage")
        nameLabel.setFixedSize(100, 30)
        nameLabel.setFont(QFont("Sans Serif", 12))
        tableLayout.addWidget(nameLabel)
        countLabel = QLabel("# of Runs")
        countLabel.setFixedSize(100, 30)
        countLabel.setFont(QFont("Sans Serif", 12))
        tableLayout.addWidget(countLabel)
        itemLabel = QLabel("Expected Drops")
        itemLabel.setFixedSize(600, 30)
        itemLabel.setFont(QFont("Sans Serif", 12))
        tableLayout.addWidget(itemLabel)
        self.mainLayout.addLayout(tableLayout)
        for stage in response['stages']:
            stageLayout = QHBoxLayout(self)
            stageLayout.setAlignment(Qt.AlignLeft)
            codeLabel = QLabel(stage['stage'])
            codeLabel.setFont(QFont("Sans Serif", 12))
            codeLabel.setFixedSize(100, 80)
            stageLayout.addWidget(codeLabel)
            countLabel = QLabel(stage['count'])
            countLabel.setFixedSize(100, 80)
            stageLayout.addWidget(countLabel)

            i = 0
            dropsLayout = QGridLayout(self)
            for item, count in stage['items'].items():
                if item not in reverse_ids: continue
                count = float(count)
                button = MaterialButton(self, reverse_ids[item], 0, 59, 59)
                label = QLabel(str(count))
                label.setFixedWidth(59)
                matLayout = QVBoxLayout()
                matLayout.addWidget(button)
                matLayout.addWidget(label)
                dropsLayout.addLayout(matLayout, int(i/10), i%10)
                i += 1
            stageLayout.addLayout(dropsLayout)
            self.mainLayout.addLayout(stageLayout)