import io
import json
import pandas as pd
from inventory import ids
import numpy as np

f = io.open("Data/char_table.json")
char_info = json.load(f)
f.close()
f = io.open("Data/names_to_ids.json")
name_ids = json.load(f)

op_data = pd.ExcelFile('Data/AKData.xlsx')
skills = pd.read_excel(op_data, "Skills")
elites = pd.read_excel(op_data, "Elites")
specs = pd.read_excel(op_data, "Specs")
mods = pd.read_excel(op_data, "Mods")
exp = pd.read_excel(op_data, "Exp")
stage = pd.read_excel(op_data, "Stages")


def get_stage_drops(name):
    drops = stage[(stage["StageId"]==name)].values
    if len(drops) == 0: return
    drops = drops[0][1:]
    i = 0
    return [str(int(x)) for x in drops if x == x and str(int(x)) in ids]

def check_id(name):
    if name in name_ids:
        return name_ids[name]
    return name


def get_operator(name):
    return char_info.get(check_id(name.lower()), None)


def get_exp_costs(elite, startLevel, endLevel):
    needs = exp[(exp['Elite'] == elite) & (exp['Level'] >= startLevel) & (exp['Level'] <= endLevel)].values
    total = np.sum(needs, 0)[2:]
    return {"1000": int(total[0]), "1001": int(total[0])}


def get_skill_cost(name, level):
    name = name.lower()
    needs = skills[(skills['Name'] == name) & (skills['Level'] == level)].values
    if len(needs) > 0:
        needs = needs[0][3:]
    else: return
    needs[needs != needs] = 0
    requirements = {}
    for i in range(len(needs)):
        if needs[i] > 0: requirements[ids[i]] = needs[i]
    return requirements


def get_elite_cost(name, level):
    name = name.lower()
    needs = elites[(elites['Name'] == name) & (elites['Level'] == level)].values
    if len(needs) > 0:
        needs = needs[0][3:]
    else: return
    needs[needs != needs] = 0
    requirements = {}
    for i in range(len(needs)):
        if needs[i] > 0: requirements[ids[i]] = needs[i]
    return requirements


def get_specs_cost(name, level, type):
    name = name.lower()
    needs = specs[(specs['Name'] == name) & (specs['Level'] == level) & (specs['Type'] == type)].values
    if len(needs) > 0:
        needs = needs[0][4:]
    else: return
    needs[needs != needs] = 0
    requirements = {}
    for i in range(len(needs)):
        if needs[i] > 0: requirements[ids[i]] = needs[i]
    return requirements


def get_mod_cost(name, level, type):
    name = name.lower()
    needs = mods[(mods['Name'] == name) & (mods['Level'] == level) & (mods['Type'] == type)].values
    if len(needs) > 0:
        needs = needs[0][4:]
    else: return
    needs[needs != needs] = 0
    requirements = {}
    for i in range(len(needs)):
        if needs[i] > 0: requirements[ids[i]] = needs[i]
    return requirements

if __name__ == "__main__":
    print(get_stage_drops("0"))