import json
import io
import copy

idFile = io.open("Data/ids.txt")
ids = idFile.read().split("\t")
idFile.close()
recipe_file = io.open("Data/crafts.json")
recipes = json.load(recipe_file)["crafts"]
recipe_file.close()
nameFile = io.open("Data/material_names.json")
names = json.load(nameFile)
nameFile.close()

class Depot:
    def __init__(self):
        try:
            depot = {}
            try:
                depot = io.open("Data/depot.json", 'r')
                depot = json.load(depot)
            except OSError:
                pass
            for name in ids:
                if name not in depot:
                    depot[name] = 0
            self.depot = depot
            self.depot["1000"] = 0
            for k,v in {"2004":2000,"2003":1000,"2002":400,"2001":200}.items():
                self.depot["1000"] += self.depot[k] * v

        except:
            self.depot = {x: 0 for x in ids}

    def save_depot(self):
        depot_file = io.open("Data/depot.json", 'w')
        json.dump(self.depot, depot_file)

    def upgrade(self, amnt):
        dupe = copy.deepcopy(self.depot)
        tickets = ["2004", "2003", "2002", "2001"]
        exps = [2000, 1000, 400, 200]
        i = 0
        while amnt > 0 and i <= 3:
            if sum(dupe[tickets[x]] * exps[x] for x in range(i,4)) < amnt:
                break
            while amnt >= exps[i]:
                if dupe[tickets[i]] == 0:
                    if not self.craft(dupe,tickets[i],True):
                        break
                amnt -= exps[i]
                dupe[tickets[i]] -= 1
            else:
                i += 1
                continue
            break
        a = 0
        while a < 4 and amnt <= exps[a]: a += 1
        if a == 4 or sum(dupe[tickets[x]] * exps[x] for x in range(a,4)) >= amnt:
            i = 3
        else:
            i = a-1
        while amnt > 0 and i >= 0:
            while amnt > 0 and dupe[tickets[i]] > 0:
                dupe[tickets[i]] -= 1
                amnt -= exps[i]
            i -= 1
        if amnt <= 0:
            self.depot.update(dupe)
            return True
        return False

    def craft(self, inv: dict, craft_id: str, recur=False, simulate=False, amnt=0):
        """
        crafts a singular item of craft_id. makes no changes if inventory is unable to perform craft
        :param simulate: whether or not the craft should actually reflect upon inv
        :param recur: False by default. Will do recursive crafting if True
        :param inv: Inventory dict
        :param craft_id: id of item to be crafted
        :return: operation success/failure
        """
        if craft_id == "1000":
            return self.upgrade(amnt)
        dupe = copy.deepcopy(inv)
        to_deduct = recipes.get(craft_id, None)
        if to_deduct is None:
            return False
        try:
            for k, v in to_deduct.items():
                dupe[k] -= v
                assert dupe[k] >= 0
            dupe[craft_id] += 1
        except KeyError:
            return False
        except AssertionError:
            if recur:
                reduct = copy.deepcopy(inv)
                for k, v in to_deduct.items():
                    left = v - reduct[k]
                    for i in range(int(left)):
                        if recipes.get(k, None) is None:
                            return False
                        if not self.craft(reduct, k, True):
                            return False
                if simulate:
                    return True
                inv.update(reduct)
                return self.craft(inv, craft_id, True)
            else:
                return False
        if not simulate:
            inv.update(dupe)
        return True

    def validate(self):
        return all([x > 0 for x in self.depot.values()])

if __name__ == "__main__":
    t = Depot()
    #for i in range(7):
    for i in ["2004", "2003", "2002", "2001"]:
        print(t.depot[i], end=" ")
    print()
    print(t.upgrade(200))
    for i in ["2004", "2003", "2002", "2001"]:
        print(t.depot[i], end=" ")
