from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import *

from operatorInfo import name_ids


class CollapsibleBox(QWidget):
    def __init__(self, parent, name: str, rows: int, width: int, height: int, **kwargs):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QToolButton(
            text=name.capitalize(), checkable=True, checked=False
        )
        self.toggle_button.setFont(QFont("Sans Serif", 18))
        self.toggle_button.setFixedSize(width-height, height)
        self.rows = rows

        self.setFixedSize(width, height)

        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QFrame.NoFrame)

        self.avatarLabel = QLabel()
        image = QPixmap()
        if name != "":
            image = QPixmap("Images/avatars/" + name_ids[name] + ".png")
        image = image.scaled(height, height, transformMode=QtCore.Qt.SmoothTransformation)
        self.avatarLabel.setFixedSize(height, height)
        self.avatarLabel.setPixmap(image)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        hlay = QHBoxLayout(self)
        hlay.setAlignment(QtCore.Qt.AlignLeft)
        hlay.addWidget(self.avatarLabel)
        hlay.addWidget(self.toggle_button)
        lay.addLayout(hlay)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(500)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)