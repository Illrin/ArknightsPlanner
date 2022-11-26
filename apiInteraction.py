import requests
import json
import io
from inventory import ids

def updateStages():
    url = "https://penguin-stats.io/PenguinStats/api/v2/stages/"
    response = requests.get(url)
    if response.status_code != 200: return
    response = response.json()
    codes = {}
    for stage in response:
        exist = stage["existence"]["CN"]
        exist = exist["exist"] and "closeTime" not in exist
        if exist:
            codes[stage["code"]] = stage["stageId"]
    f = io.open("Data/stage_codes.json", 'w', encoding="utf-8")
    json.dump(codes, f)
    f.close()


def getStageDrops(stage: str):
    url = "https://penguin-stats.io/PenguinStats/api/v2/stages/" + stage
    response = requests.get(url)
    if response.status_code != 200: return []
    response = response.json()
    drops = sorted([x for x in [a.get("itemId","") for a in response["dropInfos"]] if x in ids], key=lambda x: ids.index(x))
    return drops


def getPlanner(owned: dict, required: dict, server: str):
    url = "https://planner.penguin-stats.io/plan"
    req = {"owned": owned, "required": required, "server": server, "input_lang": "en", "output_lang": "en"}
    response = requests.post(url, json=req)
    if response.status_code != 200: return None
    return response.json()