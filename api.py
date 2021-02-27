import requests
import json

class API:
    def __init__(self,api_key):
        self.api_key = api_key
        self.version = self.Get_Latest_Version()
        self.champions = self.Get_Champions(self.version)

    def Get_Latest_Version(self):
        return json.loads(requests.get("https://ddragon.leagueoflegends.com/api/versions.json").text)[0]

    def Get_Champions(self, version):
        champions = []
        r = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json")
        data = json.loads(r.text)['data']
        
        for champ in data:
            champions.append(champ)

        return champions

    def Get_Champion_Png(self, name):   
        return f"http://ddragon.leagueoflegends.com/cdn/{self.version}/img/champion/{name}.png"
