class Character():
    def __init__(self, id:str, name:str, faction:str, rarity:int, job:str, subjob:str, skillNames:list):
        self.id = id
        self.name = name
        self.faction = faction
        self.rarity = rarity
        self.job = job
        self.subjob = subjob
        self.skillNames = skillNames
        self.skills = [None] * 6
        self.master = [[[],[],[]],
                       [[],[],[]],
                       [[],[],[]]]
        self.elites = [None] * 2
        self.mods = []

    def skillSet(self, level, mats):
        self.skills[level] = mats

    def masterSet(self, type, level, mats):
        self.master[type][level].extend(mats)
    
    def eliteSet(self, level, mats):
        self.elites[level] = mats

    def getElite(self, level):
        return self.elites[level-1]

    def getSkill(self, level):
        return self.skills[level-2]
    
    def getSpec(self, type, level):
        return self.master[type][level-1]
    
    def getMod(self, num, level):
        return self.mods[num].unlocks[level-1]
    

class Module():
    def __init__(self, id:str, type:str, icon:str):
        self.id = id
        self.type = type
        self.icon = icon
        self.unlocks = [None] * 3