import json
import copy
from chars import *
from path import resource_path

try:
    with open(resource_path("json/ids.json")) as f:
        ids = json.load(f)['ids']
    with open(resource_path("json/crafts.json")) as f:
        recipies = json.load(f)['crafts']
    with open(resource_path("json/material_names.json"), encoding='utf-8') as f:
        names = json.load(f)
except Exception as e:
    raise e

class Depot:
    def __init__(self):
        self.depot = {}
        try:
            with open(resource_path("save/depot.json")) as f:
                self.depot = json.load(f)
            for id in ids:
                if id not in self.depot: self.depot[id] = 0
            self.updateExp()
            
        except Exception as e:
            self.depot = {x: 0 for x in ids}
    
    def updateExp(self):
        exp = 0
        for k,v in {"2004":2000,"2003":1000,"2002":400,"2001":200}.items():
            exp += self.depot[k] * v
        self.depot['1000'] = exp

    def save(self):
        with open(resource_path('save/depot.json'), 'w') as f:
            json.dump(self.depot, f)
    
    def upgrade(self, amnt:int, sim:bool=False):
        dupe = copy.deepcopy(self.depot) # create copy for working
        self.updateExp()
        tickets = ["2004", "2003", "2002", "2001"]
        exps = [2000, 1000, 400, 200]

        # edge towards amnt w/o going past
        i = 0 # level of ticket w/o breaking threshold
        while amnt > 0 and i < 4:
            if sum(dupe[tickets[x]] * exps[x] for x in range(i,4)) < amnt:
                # skip to pt 2 if remaining exp isnt enough
                break
            while amnt >= exps[i]: # dont break past
                # decrement by ticket's exp, use lower tickets if needed as replacement
                if dupe[tickets[i]] == 0:
                    if not self.craft(dupe, tickets[i], True):
                        break
                amnt -= exps[i]
                dupe[tickets[i]] -= 1
            i += 1

        # finish up with smallest amnt of tickets possible
        # set i to highest applicable ticket tier
        a = 0
        while a < 4 and amnt <= exps[a]: a += 1 # go to lowest tier above threshold
        if a == 4 or sum(dupe[tickets[x]] * exps[x] for x in range(a, 4)):
            i = 3
        else:
            i = a - 1

        #use up rest of the tickets as needed
        while amnt > 0 and i >= 0:
            while amnt > 0 and dupe[tickets[i]] > 0:
                dupe[tickets[i]] -= 1
                amnt -= exps[i]
            i -= 1
        if amnt <= 0:
            if not sim: self.depot.update(dupe)
            return True
        return False
    
    def craft(self, inv:dict, craft_id:str, recur:bool=False, simulate:bool=False, amnt:int=0):
        """
        crafts a singular item of craft_id. makes no changes if inventory is unable to perform craft
        :param simulate: whether or not the craft should actually reflect upon inv
        :param recur: False by default. Will do recursive crafting if True
        :param inv: Inventory dict
        :param craft_id: id of item to be crafted
        :param amnt: amnt of exp needed in case of upgrade crafting. ignored if craft_id /= '1000'
        :return: operation success/failure
        """
        if craft_id == '1000':
            return self.upgrade(amnt, simulate)
        dupe = copy.deepcopy(inv)
        to_deduct = recipies.get(craft_id, None)
        if to_deduct is None: return False

        try:
            for k, v in to_deduct.items():
                dupe[k] -= v
            lacking = [(k, v*-1) for k,v in dupe.items() if v < 0]
            assert len(lacking) == 0
            dupe[craft_id] += 1
            if not simulate:
                inv.update(dupe)
            return True
        except KeyError:
            return False
        except AssertionError:
            if not recur: return lacking
            reduct = copy.deepcopy(inv)
            for k, v in to_deduct.items():
                remain = v - reduct[k]
                for i in range(int(remain)):
                    if recipies.get(k, None) is None: return lacking
                    if self.craft(reduct, k, True) != True: return lacking
            if simulate:
                return True
            inv.update(reduct)
            return self.craft(inv, craft_id, True)
            
    def validate(self):
        return all([x > 0 for x in self.depot.values()])
    
    def increment(self, id):
        if id not in self.depot: raise KeyError
        self.depot[id] += 1
        return self.depot[id]

    def decrement(self, id):
        if id not in self.depot: raise KeyError
        if self.depot[id] <= 0: return 0
        self.depot[id] -= 1
        return self.depot[id]

    def self_craft(self, craft_id, recur=False, simulate=False, amnt=0):
        return self.craft(self.depot, craft_id, recur, simulate, amnt)
    
    def get_item(self, id):
        return self.depot[id]
    
    def set_item(self, id, amnt):
        self.depot[id] = amnt
        self.updateExp()

    def reduce_item(self, id, amnt):
        if id == '1000':
            self.upgrade(amnt)
        else:
            self.depot[id] -= amnt
        self.updateExp()