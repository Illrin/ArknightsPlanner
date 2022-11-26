import requests
from inventory import ids
import io
import json

if __name__ == "__main__":
    url = "https://planner.penguin-stats.io/plan"
    req = {"required": {"Orirock Cube":10}, "server":"US", "input_lang":"en", "output_lang":"en"}
    response = requests.post(url, json=req)
    print(response.json())