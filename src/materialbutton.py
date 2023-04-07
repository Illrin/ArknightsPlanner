from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import *
from typing import Callable
import urllib

from path import resource_path

class SpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class SpinDoubleBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()

class MaterialImage(QLabel):
    def __init__(self, parent, itemId: str, amount:int, left: Callable, right: Callable, links:list=None, **kwargs):
        super(MaterialImage, self).__init__(parent, **kwargs)
        self.left = left
        self.right = right
        self.setText(str(amount))
        self.setAlignment(Qt.AlignCenter)

        if 'width' in kwargs: 
            self.wid = kwargs['width']
            self.setFixedWidth(self.wid)
        else:
            self.wid = self.width()
        if 'height' in kwargs: 
            self.hei = kwargs['height']
            self.setFixedHeight(self.hei)
        else:
            self.hei = self.height()

        self.linkedWidgets = links

        image = QPixmap(resource_path("img/material/" + itemId + ".png"))
        image = image.scaled(self.wid, self.hei, transformMode=Qt.SmoothTransformation)
        self.setPixmap(image)

    def setSize(self, w:int, h:int):
        self.setFixedWidth(w)
        self.setFixedHeight(h)

    def setClicks(self, l, r):
        if not callable(l) or not callable(r): return False
        self.left = l
        self.right = r
        return True

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton and self.left is not None:
            amnt = self.left()
        elif QMouseEvent.button() == Qt.RightButton and self.right is not None:
            amnt = self.right()
        else:
            return
        if self.linkedWidgets is not None:
            for widget in self.linkedWidgets:
                if isinstance(widget, QSpinBox):
                    widget.setValue(amnt)
                elif isinstance(widget, QLabel):
                    widget.setText(str(amnt))

class MaterialButton(QGroupBox):
    def __init__(self, parent, itemId: str, amount:int, left: Callable, right: Callable, setter: Callable, width: int, height: int, disable:bool=False, double:bool=False,**kwargs):
        super(MaterialButton, self).__init__(parent, **kwargs)
        self.setFlat(True)
        if width > height:
            imageWidth = height
            imageHeight = height
        elif height >= width:
            imageWidth = width
            imageHeight = width

        self.lay = QVBoxLayout()

        if setter is None:
            setter = lambda x: x


        self.itemId = itemId

        
        self.lay.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)

        if not double:
            self.label = SpinBox(self)
        else:
            self.label = SpinDoubleBox(self)
        self.label.setMaximum(999999999)
        self.label.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.label.setValue(amount)
        self.label.valueChanged.connect(lambda: setter(self.label.value()))

        if disable: self.label.setDisabled(True)

        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedHeight(35)
        self.label.setFixedWidth(width)
        
        self.button = MaterialImage(self, itemId, amount, left, right, [self.label], width=imageWidth, height=imageHeight)

        self.lay.addWidget(self.button)
        self.lay.addWidget(self.label)

        self.setLayout(self.lay)
    
    def setAmount(self, amnt):
        self.label.setValue(amnt)

    def getAmount(self):
        return self.label.value()
    
    def changeAmount(self, amnt):
        self.label.setValue(self.label.value() + amnt)
    
    def getId(self):
        return self.itemId
    
    def deleteLater(self):
        self.button.deleteLater()
        super().deleteLater()