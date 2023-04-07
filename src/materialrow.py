from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap, QFont, QIcon, QCursor
from PyQt5.QtWidgets import *
from depot import recipies, names
from materialbutton import MaterialButton
from typing import Callable

from path import resource_path

displayPopup = [True]

class MaterialRow(QGroupBox):
    def __init__(self, parent, itemId: str, amount:int, left: Callable, right: Callable, setter: Callable, width: int, height: int, crafting: Callable=None, **kwargs):
        super(MaterialRow, self).__init__(parent, **kwargs)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("color: #FFFFFF; ")
        self.setTitle(names[itemId])
        self.id = itemId
        self.crafted = 0
        self.needed = 0
        if width >= height:
            buttonHeight = height
            buttonWidth = height
            self.lay = QHBoxLayout()
            self.infolay = QVBoxLayout()
        elif height > width:
            buttonHeight = width
            buttonWidth = width
            self.lay = QVBoxLayout()
            self.infolay = QHBoxLayout()
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        self.button = MaterialButton(self, itemId, amount, left, right, setter, buttonWidth, buttonHeight, **kwargs)
        self.lay.addWidget(self.button)

        self.needs = QLabel("0", self)
        self.needs.setFixedWidth(width)
        self.needs.setStyleSheet("color: rgb(242, 92, 110); font-size: 16pt")
        self.breakdown = QLabel("0", self)
        self.breakdown.setFixedWidth(width)
        self.breakdown.setStyleSheet("color: rgb(196, 151, 59); font-size: 16pt;")

        self.infolay.setAlignment(Qt.AlignHCenter)

        self.lay.addLayout(self.infolay)
        self.infolay.addWidget(self.needs)
        self.infolay.addWidget(self.breakdown)
        if itemId in recipies:
            self.craft = CraftButton(self, recipies[itemId])
            self.craft.setText("Craft")
            self.craft.setFixedWidth(width)
            self.craft.setStyleSheet('background-color: #505aa3')
            if crafting is not None: 
                self.craft.clicked.connect(lambda: crafting(itemId))
            if width >= height: self.infolay.addWidget(self.craft)
            else: self.lay.addWidget(self.craft)
        else:
            spacer = QSpacerItem(0, 35, QSizePolicy.Minimum, QSizePolicy.Minimum)
            if width >= height: self.infolay.addItem(spacer)
            else: self.lay.addItem(spacer)

        self.setLayout(self.lay)

    def setNeeds(self, amnt:int):
        self.needs.setText(str(amnt))
        self.needed = amnt

    def setCrafts(self, amnt:int):
        self.breakdown.setText(str(amnt))
        self.crafted = amnt

    def setAmount(self, amnt:int):
        self.button.setAmount(amnt)

    def setDisplay(self, display):
        if not hasattr(self, 'craft'): return
        self.craft.display = display

class CraftButton(QPushButton):
    def __init__(self, parent, ids, **kwargs):
        super(CraftButton, self).__init__(parent, **kwargs)
        self.display = True
        self.window = QMainWindow()
        self.window.setWindowTitle("Crafting Materials")
        self.window.layout().setAlignment(Qt.AlignCenter)
        w = 180
        h = 220
        self.window.setFixedSize(len(ids) * w, h)
        self.window.setWindowIcon(QIcon(resource_path('img/extra/logo-black.png')))
        self.image = QGroupBox(self.window)
        self.image.setFixedSize(len(ids) * w, h)
        lay = QHBoxLayout()
        lay.setAlignment(Qt.AlignCenter)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        for i in ids:
            button = MaterialButton(self, i, ids[i], None, None, None, w, h-40)
            button.setFixedSize(w, h)
            button.label.setDisabled(True)
            button.setContentsMargins(0, 0, 0, 0)
            button.label.setStyleSheet('font-size: 18pt')
            lay.addWidget(button)
        self.image.setLayout(lay)
        self.window.hide()
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if not self.display: 
            self.window.hide()
            return super().eventFilter(obj, event)
        if event.type() == QEvent.MouseMove:
            geom = self.window.frameGeometry()
            geom.moveCenter(QCursor.pos())
            geom.moveTop(geom.top()+200)
            self.window.setGeometry(geom)
        elif event.type() == QEvent.Leave:
            self.window.hide()
        elif event.type() == QEvent.Enter:
            self.window.show()
            geom = self.window.frameGeometry()
            geom.moveCenter(QCursor.pos())
            geom.moveTop(geom.top()+200)
            self.window.setGeometry(geom)

        return super().eventFilter(obj, event)