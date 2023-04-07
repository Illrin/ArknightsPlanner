import json
from chars import *
import urllib.request
import pickle
import os
import ijson

from path import resource_path

def loadEquipment():
    f = urllib.request.urlopen("https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/json/gamedata/zh_CN/gamedata/excel/uniequip_table.json")
    equips = list(ijson.items(f, 'equipDict'))
    
    mods = {}
    for equip in equips[0].values():
        if equip['type'] == 'INITIAL': continue
        id = equip['uniEquipId']
        icon = equip['typeIcon']
        type = equip['typeName2']
        charId = equip['charId']
        mod = Module(id, type, icon)
        for i, items in enumerate(equip['itemCost'].values()):
            mod.unlocks[i] = items
        if charId not in mods:
            mods[charId] = []
        mods[charId].append(mod)
    return mods



def loadCharacters():
    modules = loadEquipment()
    f = urllib.request.urlopen('https://raw.githubusercontent.com/Aceship/AN-EN-Tags/master/json/gamedata/zh_CN/gamedata/excel/character_table.json')
    characters = {}
    for id, unit in ijson.kvitems(f, ''):
        name = unit['appellation']
        if unit['nationId'] is None and unit['groupId'] is None and unit['teamId'] is None:
            continue
        rarity = unit['rarity'] + 1
        jobtrans = {
            'tank': 'defender',
            'warrior': 'guard',
            'special': 'specialist',
            'support': 'supporter',
            'pioneer': 'vanguard',
            'sniper': 'sniper',
            'caster': 'caster',
            'medic': 'medic',
            'trap': 'trap',
            'token': 'token'
        }
        faction = unit['nationId']
        job = jobtrans[unit['profession'].lower()]
        if unit['displayNumber'] is None: print(name)
        if job in ['trap', 'token']: continue
        subjob = unit['subProfessionId']
        skillNames = [x['skillId'] for x in unit['skills']]

        ak = Character(id, name, faction, rarity, job, subjob, skillNames)
        
        for i, skillLvl in enumerate(unit['allSkillLvlup']):
            ak.skillSet(i, skillLvl['lvlUpCost'])
        
        for i, elvl in enumerate(unit['phases'], -1):
            if elvl['evolveCost'] is None: continue
            ak.eliteSet(i, elvl['evolveCost'])
        
        for i, skill in enumerate(unit['skills']):
            needs = [x['levelUpCost'] for x in skill['levelUpCostCond']]
            for a, level in enumerate(needs):
                ak.masterSet(i, a, level)

        if id in modules:
            ak.mods = modules[id]

        characters[name] = ak

        altNames = {
            'Роса':'Rosa',
            'Позёмка':'Pozyomka',
            'Młynar':'Mlynar',
            'Зима': 'Zima',
            'Истина': 'Istina',
            'Гум': 'Gummy'

        }
        if name in altNames:
            characters[altNames[name]] = ak
        

    if not os.path.exists(resource_path("save")):
        os.makedirs(resource_path('save'))
    f = open(resource_path('save/akChars.pkl'), 'wb')
    pickle.dump(characters, f)
    f.close()

if __name__ == "__main__":
    loadCharacters()