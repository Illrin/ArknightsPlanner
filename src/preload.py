from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap, QFont, QIcon, QCursor, QImage
from PyQt5.QtWidgets import *
from materialbutton import MaterialButton
from typing import Callable
from akparser import loadCharacters
import pickle
import os
from thefuzz import process
import urllib.request

from path import resource_path

def loadCharacter(character):
        keys = [character.id, character.job, character.subjob]
        for name in character.skillNames:
            keys.append(name)
        while len(keys) < 6:
            keys.append('')
        for mod in character.mods:
            keys.append(mod.icon)
            keys.append(mod.id)
        while len(keys) < 10:
            keys.append('')
        urls = ['https://raw.githubusercontent.com/Aceship/Arknight-Images/main/avatars/',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/classes/class_',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/ui/subclass/sub_',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/skills/skill_icon_',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/skills/skill_icon_',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/skills/skill_icon_',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/equip/type/',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/equip/icon/',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/equip/type/',
                'https://raw.githubusercontent.com/Aceship/Arknight-Images/main/equip/icon/',]
        sizes = [(240, 240), (120, 120), (80, 80), (120, 120), (120, 120), (120, 120), (80, 80), (120, 120), (80, 80), (120, 120),]
        suffix = ['.png', '.png', '_icon.png', '.png', '.png', '.png', '.png', '.png', '.png', '.png', ]
        images = []
        for i in range(len(keys)):
            if keys[i] == '':
                img = None
            else:
                try:
                    img = urllib.request.urlopen(urls[i] + keys[i] + suffix[i]).read()
                except:
                    img = 'img/load_fail.png'
            images.append(img)
        return images

def preload():
    try:
        loadCharacters()
    except:
        exit(-1)

    with open(resource_path('save/akChars.pkl'), mode='rb') as f:
        characters = pickle.load(f)

    images = {}
    for k, v in characters.items():
        images[k] = loadCharacter(v)

    with open(resource_path('save/akImages.pkl'), mode='wb') as f:
        pickle.dump(images, f)