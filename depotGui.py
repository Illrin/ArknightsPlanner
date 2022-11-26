from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import *
from inventory import names, recipes


class SpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class MaterialButton(QLabel):
    def __init__(self, parent, id: str, amount: int, width: int, height: int, **kwargs):
        super(MaterialButton, self).__init__(parent, **kwargs)
        self.id = id
        self.parent = parent
        self.amount = amount
        image = QPixmap("Images/materials/" + id + ".png")
        image = image.scaled(width, height, transformMode=Qt.SmoothTransformation)
        self.setPixmap(image)
        self.setFixedSize(width, height)

    def mousePressEvent(self, QMouseEvent):
        if self.id == "1000": return
        if QMouseEvent.button() == Qt.LeftButton:
            self.amount += 1
        elif QMouseEvent.button() == Qt.RightButton:
            self.amount = max(self.amount-1, 0)
        try:
            self.parentWidget().set_amount(self.amount, self.id)
        except:
            try:
                self.parent.set_amount(self.amount, self.id)
            except:
                pass


class MaterialRow(QGroupBox):
    def __init__(self, parent, id: str, amount: int, width: int, height: int, baseNeed=0, totalNeed=0, **kwargs):
        super(MaterialRow, self).__init__(parent, **kwargs)
        self.baseNeed = baseNeed
        self.totalNeed = totalNeed
        self.wid = width
        self.hei = height
        self.amount = amount
        self.id = id

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.button = MaterialButton(self, self.id, self.amount, self.hei, self.hei)
        layout.addWidget(self.button)

        middle = QGroupBox()
        middle.setFixedSize(int(self.wid / 3), self.hei)
        middleLayout = QVBoxLayout()

        self.label = QLabel(self)
        self.label.setText(names[self.id])
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Sans Serif", 10))
        middleLayout.addWidget(self.label)

        if id in recipes and id not in ["2004", "2003", "2002"]:
            craftButton = QPushButton()
            craftButton.setText("Craft")
            craftButton.clicked.connect(lambda: self.root.craftMaterial(self.id, self))
            middleLayout.addWidget(craftButton)

        middle.setLayout(middleLayout)
        layout.addWidget(middle)

        self.needText = QLabel()
        self.needText.setWordWrap(True)
        self.updateTotals()

        self.text = SpinBox(self)
        self.text.textChanged.connect(self.update_amount)
        self.text.setFixedSize(int(self.wid / 3), self.hei)
        self.text.setMaximum(999999999)
        self.text.setValue(self.amount)
        self.text.setStyleSheet("QSpinBox::up-arrow::pressed{"
                                "background-color : rgb(181, 181, 181);}"
                                "QSpinBox::down-arrow::pressed{"
                                "background-color : rgb(181, 181, 181);}")

        self.text.setFixedSize(int(self.wid / 3), int(self.hei / 2))
        self.needText.setFixedSize(int(self.wid / 3), int(self.hei / 2))
        needLayout = QVBoxLayout()
        needLayout.addWidget(self.text)
        needLayout.addWidget(self.needText)
        layout.addLayout(needLayout)
        self.setLayout(layout)
        self.setFixedSize(self.wid, self.hei)

        self.root = self.parentWidget()
        while not isinstance(self.root, QMainWindow):
            self.root = self.root.parentWidget()

    def set_amount(self, amnt: int, id):
        self.text.setValue(amnt)
        self.amount = amnt
        self.updateTotals()
        try:
            self.root.setMaterialAmount(id, amnt)
        except:
            pass

    def update_amount(self):
        self.button.amount = self.text.value()
        self.amount = self.text.value()
        self.updateTotals()
        try:
            self.root.setMaterialAmount(self.button.id, self.button.amount)
        except:
            pass

    def updateTotals(self, base=None, total=None):
        if base is not None:
            self.baseNeed = base
        if total is not None:
            self.totalNeed = total
        baseRequired = max(int(self.baseNeed - self.amount), 0)
        totalRequired = max(int(self.totalNeed - self.amount), 0)
        self.needText.setText("Needed: " + str(baseRequired) + "\nNeeded Including Crafts: " + str(totalRequired))